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

// One approved identity: image authored specifically for this 240x240 screen.
// The generated header is built from assets/face-idle-240.png, NOT from a UI mockup.
// RLE palette asset lives in flash and is streamed a scanline at a time.
#include "face_asset.h"

constexpr uint16_t BLACK = 0x0000;
constexpr uint16_t WARM = 0xFE1A;
constexpr uint16_t WARM_DIM = 0xBCAF;
Adafruit_GC9A01A lcd(TFT_CS, TFT_DC, TFT_RST);
String activeFace = "neutral";
String commandBuffer;
bool droppingOverlongLine = false;
bool imuReady = false;
bool previouslyReacting = false;
bool blinkActive = false;
uint32_t blinkFinish = 0;
uint32_t nextBlinkAt = 0;
uint32_t surpriseUntil = 0;
uint32_t lastShake = 0;
uint32_t lastImuSample = 0;
uint8_t consecutiveShocks = 0;
static uint16_t lineBuffer[kFaceWidth];  // only 480 bytes, no full framebuffer

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

// Display the *actual approved raster* as RGB565 in 240 scanline writes.
// 32-color palette; compact one-byte tokens encode up to 8 repeated pixels.
// No PNG, alpha compositing or heap allocation runs on the microcontroller.
void paintApprovedFace() {
  lcd.startWrite();
  lcd.setAddrWindow(0, 0, kFaceWidth, kFaceHeight);
  uint16_t x = 0;
  for (size_t i = 0; i < kFaceRunCount; ++i) {
    const uint8_t token = pgm_read_byte(&kFacePackedRuns[i]);
    uint8_t count = (token >> 5) + 1;
    const uint16_t color = pgm_read_word(&kFacePalette[token & 31]);
    while (count--) {
      lineBuffer[x++] = color;
      if (x == kFaceWidth) {
        lcd.writePixels(lineBuffer, kFaceWidth);
        x = 0;
      }
    }
  }
  lcd.endWrite();
}

// The six original protocol states remain supported, but *all* use one
// single identity. These are restrained mouth/lid changes, not new avatars.
void applyMood(const String &mood) {
  if (mood == "neutral") return;
  if (mood == "sleepy") {
    lcd.fillRect(106, 148, 33, 20, BLACK);
    lcd.drawFastHLine(111, 157, 19, WARM_DIM);
    return;
  }
  lcd.fillRect(106, 148, 33, 20, BLACK);
  if (mood == "happy") {
    lcd.drawLine(111, 153, 122, 159, WARM);
    lcd.drawLine(122, 159, 134, 152, WARM);
  } else if (mood == "sad") {
    lcd.drawLine(111, 161, 121, 156, WARM_DIM);
    lcd.drawLine(121, 156, 134, 162, WARM_DIM);
  } else if (mood == "thinking") {
    lcd.drawFastHLine(117, 157, 16, WARM_DIM);
  } else if (mood == "surprised") {
    lcd.drawCircle(122, 158, 5, WARM);
  }
}

// A short blink. Preserve the eyebrow silhouettes and original character.
// The eyes are restored from the approved sprite when blink ends.
void paintBlink() {
  lcd.fillRoundRect(35, 119, 70, 40, 9, BLACK);
  lcd.fillRoundRect(135, 119, 75, 40, 9, BLACK);
  lcd.drawLine(42, 132, 97, 135, WARM_DIM);
  lcd.drawLine(145, 134, 201, 136, WARM_DIM);
}

void drawFace(uint32_t now) {
  paintApprovedFace();
  const bool reacting = surpriseUntil != 0 &&
                        (int32_t)(surpriseUntil - now) > 0;
  applyMood(reacting ? String("surprised") : activeFace);
  if (activeFace == "sleepy" || blinkActive) paintBlink();
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
    previouslyReacting = true;
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
  nextBlinkAt = millis() + 3300 + (esp_random() % 3400);
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
  if (reacting != previouslyReacting) {
    previouslyReacting = reacting;
    drawFace(now);
  }
  // Organic enough not to feel like a metronome; only one character animates.
  if (!blinkActive && activeFace != "sleepy" &&
      (int32_t)(now - nextBlinkAt) >= 0) {
    blinkActive = true;
    blinkFinish = now + 135;
    paintBlink();
  } else if (blinkActive && (int32_t)(now - blinkFinish) >= 0) {
    blinkActive = false;
    nextBlinkAt = now + 3300 + (esp_random() % 3400);
    drawFace(now);
  }
  delay(2);
}
