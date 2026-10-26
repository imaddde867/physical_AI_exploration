#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>
#include <math.h>

// Project pin choices for an ESP32-S3 DevKitC-style board; verify actual labels.
constexpr int PIN_SDA = 8;
constexpr int PIN_SCL = 9;
constexpr uint8_t OLED_ADDRESS = 0x3C;
constexpr uint8_t MPU_ADDRESS = 0x68;
constexpr uint32_t BAUD_RATE = 115200;
constexpr uint32_t IMU_SAMPLE_MS = 40;
constexpr uint32_t SHAKE_COOLDOWN_MS = 1500;
constexpr float SHAKE_DELTA_G = 0.55f; // heuristic, not calibrated

Adafruit_SSD1306 oled(128, 64, &Wire, -1);
bool oledReady = false;
bool imuReady = false;
String activeFace = "neutral";
String commandBuffer;
bool droppingOverlongLine = false;
bool eyesClosed = false;
uint32_t surpriseUntil = 0;
uint32_t lastShake = 0;
uint32_t lastImuSample = 0;
uint8_t consecutiveShocks = 0;

bool validFace(const String &name) {
  return name == "neutral" || name == "happy" || name == "sad" ||
         name == "sleepy" || name == "surprised" || name == "thinking";
}

void sendReply(const char *type, const char *field, const char *value) {
  JsonDocument doc;
  doc["type"] = type;
  doc[field] = value;
  serializeJson(doc, Serial);
  Serial.println();
}

void drawFace() {
  if (!oledReady) return;
  oled.clearDisplay();
  const bool reacting = surpriseUntil != 0 && (int32_t)(surpriseUntil - millis()) > 0;
  const String shown = reacting ? "surprised" : activeFace;
  const bool blinkNow = (millis() % 4300UL) < 120UL && shown != "sleepy";
  eyesClosed = blinkNow;
  const int a = 38, b = 90, y = 27;
  if (eyesClosed || shown == "sleepy") {
    oled.drawLine(a - 11, y, a + 11, y, SSD1306_WHITE);
    oled.drawLine(b - 11, y, b + 11, y, SSD1306_WHITE);
  } else if (shown == "sad") {
    oled.drawLine(a - 12, y + 5, a + 12, y - 3, SSD1306_WHITE);
    oled.drawLine(b - 12, y - 3, b + 12, y + 5, SSD1306_WHITE);
  } else if (shown == "happy") {
    oled.drawRoundRect(a - 12, y - 5, 24, 14, 7, SSD1306_WHITE);
    oled.drawRoundRect(b - 12, y - 5, 24, 14, 7, SSD1306_WHITE);
  } else if (shown == "surprised") {
    oled.drawCircle(a, y, 10, SSD1306_WHITE);
    oled.drawCircle(b, y, 10, SSD1306_WHITE);
  } else {
    oled.fillRoundRect(a - 9, y - 9, 18, 24, 7, SSD1306_WHITE);
    oled.fillRoundRect(b - 9, y - 9, 18, 24, 7, SSD1306_WHITE);
    if (shown == "thinking") oled.drawLine(76, 9, 102, 12, SSD1306_WHITE);
  }
  oled.setTextSize(1);
  oled.setTextColor(SSD1306_WHITE);
  oled.setCursor(5, 54);
  oled.print("macdesk / ");
  oled.print(shown);
  oled.display();
}

bool configureImu() {
  Wire.beginTransmission(MPU_ADDRESS);
  Wire.write(0x6B); // PWR_MGMT_1: leave sleep mode
  Wire.write(0x00);
  return Wire.endTransmission() == 0;
}

bool readAcceleration(float &magnitudeG) {
  Wire.beginTransmission(MPU_ADDRESS);
  Wire.write(0x3B); // ACCEL_XOUT_H
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)MPU_ADDRESS, 6) != 6) return false;
  const int16_t x = (int16_t)((Wire.read() << 8) | Wire.read());
  const int16_t y = (int16_t)((Wire.read() << 8) | Wire.read());
  const int16_t z = (int16_t)((Wire.read() << 8) | Wire.read());
  // MPU-6050 reset defaults to +/- 2 g: 16384 LSB/g.
  const float fx = (float)x / 16384.f;
  const float fy = (float)y / 16384.f;
  const float fz = (float)z / 16384.f;
  magnitudeG = sqrtf(fx * fx + fy * fy + fz * fz);
  return true;
}

void checkMotion(uint32_t now) {
  if (!imuReady || now - lastImuSample < IMU_SAMPLE_MS) return;
  lastImuSample = now;
  float magnitudeG = 0;
  if (!readAcceleration(magnitudeG)) {
    consecutiveShocks = 0;
    imuReady = false;
    sendReply("event", "name", "imu_disconnected");
    return;
  }
  if (fabsf(magnitudeG - 1.0f) > SHAKE_DELTA_G) {
    if (consecutiveShocks < 3) ++consecutiveShocks;
  } else {
    consecutiveShocks = 0;
  }
  if (consecutiveShocks >= 2 && (lastShake == 0 || now - lastShake > SHAKE_COOLDOWN_MS)) {
    lastShake = now;
    consecutiveShocks = 0;
    surpriseUntil = now + 700;
    drawFace();
    sendReply("event", "name", "shake");
  }
}

void handleLine(const String &line) {
  JsonDocument input;
  if (deserializeJson(input, line)) {
    sendReply("error", "reason", "invalid_json");
    return;
  }
  if (!input["cmd"].is<const char *>() ||
      strcmp(input["cmd"].as<const char *>(), "face") != 0 ||
      !input["value"].is<const char *>()) {
    sendReply("error", "reason", "unknown_command");
    return;
  }
  const String requested = input["value"].as<String>();
  if (!validFace(requested)) {
    sendReply("error", "reason", "invalid_face");
    return;
  }
  activeFace = requested;
  surpriseUntil = 0;
  drawFace();
  sendReply("ack", "face", activeFace.c_str());
}

void setup() {
  Serial.begin(BAUD_RATE);
  Wire.begin(PIN_SDA, PIN_SCL);
  oledReady = oled.begin(SSD1306_SWITCHCAPVCC, OLED_ADDRESS);
  imuReady = configureImu(); // optional: OLED-only mode works without sensor
  drawFace();
  JsonDocument ready;
  ready["type"] = "ready";
  ready["display"] = oledReady ? "ok" : "not_found";
  ready["imu"] = imuReady ? "ok" : "not_found";
  ready["protocol"] = 1;
  serializeJson(ready, Serial);
  Serial.println();
}

void loop() {
  while (Serial.available()) {
    const char ch = (char)Serial.read();
    if (ch == '\n') {
      if (!droppingOverlongLine) handleLine(commandBuffer);
      commandBuffer = "";
      droppingOverlongLine = false;
    } else if (ch != '\r' && !droppingOverlongLine) {
      if (commandBuffer.length() >= 255) {
        commandBuffer = "";
        droppingOverlongLine = true; // discard entire line, not just valid suffix
        sendReply("error", "reason", "line_too_long");
      } else commandBuffer += ch;
    }
  }
  const uint32_t now = millis();
  checkMotion(now);
  const bool reacting = surpriseUntil != 0 && (int32_t)(surpriseUntil - now) > 0;
  const bool shouldBlink = (now % 4300UL) < 120UL && (reacting || activeFace != "sleepy");
  static bool wasReacting = false;
  if (reacting != wasReacting || shouldBlink != eyesClosed) {
    wasReacting = reacting;
    drawFace();
  }
  delay(2);
}
