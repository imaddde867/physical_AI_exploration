// MacDesk Buddy: original round RGB-face firmware.
// GC9A01 240x240 SPI IPS; optional MPU-6050 on an independent I2C bus.
#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_GC9A01A.h>
#include <ArduinoJson.h>
#include <math.h>
#include <string.h>

// Verify all GPIOs against your actual ESP32-S3 board pinout.
// Display SCL and SDA mean SPI SCK and MOSI, NOT sensor I2C.
constexpr int TFT_MOSI = 11;
constexpr int TFT_SCLK = 12;
constexpr int TFT_CS = 10;
constexpr int TFT_DC = 13;
constexpr int TFT_RST = 14;
// Leave optional LCD BLK unconnected unless its electrical behavior is verified.
constexpr int IMU_SDA = 8;
constexpr int IMU_SCL = 9;
constexpr uint8_t IMU_ADDRESS = 0x68;
constexpr uint32_t IMU_SAMPLE_MS = 40;
constexpr uint32_t SHAKE_COOLDOWN_MS = 1500;
constexpr float SHAKE_DELTA_G = 0.55f;  // experimental, calibrate on hardware

constexpr uint16_t BG = 0x0000;
constexpr uint16_t AQUA = 0x7FFF;
constexpr uint16_t LILAC = 0xA2FF;
constexpr uint16_t PINK = 0xF2DC;
constexpr uint16_t CREAM = 0xFF7A;
constexpr uint16_t GOLD = 0xFDE0;
constexpr uint16_t DARK = 0x18C5;
constexpr uint16_t RIM = 0x21AB;

Adafruit_GC9A01A lcd(TFT_CS, TFT_DC, TFT_RST);
String activeFace = "neutral";
String commandBuffer;
bool droppingOverlongLine = false;
bool imuReady = false;
bool eyesClosed = false;
bool previouslyReacting = false;
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

// Draws curves algorithmically: no external copyrighted bitmap assets.
void drawMouth(bool smile, uint16_t color) {
  int lastX = 0, lastY = 0;
  for (int x = 88; x <= 152; x += 2) {
    const int delta = x - 120;
    const int depth = (delta * delta) / 60;
    const int y = smile ? 176 - depth : 162 + depth;
    if (x > 88) {
      lcd.drawLine(lastX, lastY, x, y, color);
      lcd.drawLine(lastX, lastY + 1, x, y + 1, color);
    }
    lastX = x;
    lastY = y;
  }
}
void drawEyes(uint16_t color, bool blink, bool lookingRight) {
  const int positions[2] = {82, 158};
  for (int cx : positions) {
    if (blink) {
      lcd.fillRoundRect(cx - 19, 105, 38, 6, 3, color);
      continue;
    }
    lcd.fillRoundRect(cx - 18, 86, 36, 55, 16, color);
    const int offset = lookingRight ? 7 : 0;
    lcd.fillRoundRect(cx - 8 + offset, 107, 17, 25, 8, DARK);
    lcd.fillCircle(cx - 5 + offset, 108, 5, CREAM);
  }
}
// A redraw happens on a face/blink/sensor transition, not every loop.
void drawFace(uint32_t now) {
  const bool reacting = surpriseUntil != 0 &&
                        (int32_t)(surpriseUntil - now) > 0;
  const String shown = reacting ? "surprised" : activeFace;
  const bool blink = (now % 4300UL) < 130UL && shown != "sleepy";
  eyesClosed = blink;
  lcd.fillScreen(BG);
  lcd.drawCircle(120, 120, 112, RIM);
  lcd.drawCircle(120, 120, 111, RIM);
  if (shown == "sleepy") {
    drawEyes(LILAC, true, false);
    lcd.fillRoundRect(110, 167, 20, 4, 2, PINK);
  } else if (shown == "happy") {
    drawEyes(AQUA, blink, false);
    if (!blink) {
      lcd.fillCircle(49, 150, 5, PINK);
      lcd.fillCircle(191, 150, 5, PINK);
    }
    drawMouth(true, PINK);
  } else if (shown == "sad") {
    drawEyes(LILAC, blink, false);
    drawMouth(false, LILAC);
  } else if (shown == "surprised") {
    drawEyes(GOLD, blink, false);
    lcd.fillCircle(120, 174, 12, PINK);
    lcd.fillCircle(120, 175, 7, BG);
  } else if (shown == "thinking") {
    drawEyes(AQUA, blink, true);
    lcd.fillCircle(113, 177, 4, PINK);
    lcd.fillCircle(124, 174, 4, PINK);
    lcd.fillCircle(135, 177, 4, PINK);
  } else {
    drawEyes(AQUA, blink, false);
    lcd.fillRoundRect(101, 171, 38, 5, 2, PINK);
  }
}
bool configureImu() {
  Wire.beginTransmission(IMU_ADDRESS);
  Wire.write(0x6B); Wire.write(0x00);
  return Wire.endTransmission() == 0;
}
bool readAcceleration(float &magnitudeG) {
  Wire.beginTransmission(IMU_ADDRESS);
  Wire.write(0x3B);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)IMU_ADDRESS, 6) != 6) return false;
  const int16_t x = (int16_t)((Wire.read() << 8) | Wire.read());
  const int16_t y = (int16_t)((Wire.read() << 8) | Wire.read());
  const int16_t z = (int16_t)((Wire.read() << 8) | Wire.read());
  const float fx = (float)x / 16384.0f;
  const float fy = (float)y / 16384.0f;
  const float fz = (float)z / 16384.0f;
  magnitudeG = sqrtf(fx*fx + fy*fy + fz*fz);
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
  } else consecutiveShocks = 0;
  if (consecutiveShocks >= 2 &&
      (lastShake == 0 || now - lastShake > SHAKE_COOLDOWN_MS)) {
    lastShake = now;
    consecutiveShocks = 0;
    surpriseUntil = now + 700;
    drawFace(now);
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
  drawFace(millis());
  sendReply("ack", "face", activeFace.c_str());
}
void setup() {
  Serial.begin(115200);
  SPI.begin(TFT_SCLK, -1, TFT_MOSI, TFT_CS);
  lcd.begin(24000000);
  lcd.setRotation(0);
  // LCD has a write-only SPI bus: cannot electronically verify pixels lit.
  Wire.begin(IMU_SDA, IMU_SCL);
  imuReady = configureImu();
  drawFace(millis());
  JsonDocument ready;
  ready["type"] = "ready";
  ready["display"] = "init_sent_unverified";
  ready["driver"] = "GC9A01";
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
        droppingOverlongLine = true;
        sendReply("error", "reason", "line_too_long");
      } else commandBuffer += ch;
    }
  }
  const uint32_t now = millis();
  checkMotion(now);
  const bool reacting = surpriseUntil != 0 &&
                        (int32_t)(surpriseUntil - now) > 0;
  const bool expectedBlink = (now % 4300UL) < 130UL &&
                             (reacting || activeFace != "sleepy");
  if (reacting != previouslyReacting || expectedBlink != eyesClosed) {
    previouslyReacting = reacting;
    drawFace(now);
  }
  delay(2);
}
