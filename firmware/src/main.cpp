#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>
#include <math.h>

// Pin mapping is for the selected ESP32-S3 DevKitC style board.
// Verify your board's pinout BEFORE attaching a display.
constexpr int PIN_SDA = 8;
constexpr int PIN_SCL = 9;
constexpr uint8_t OLED_ADDR = 0x3C;
constexpr int WIDTH = 128;
constexpr int HEIGHT = 64;
Adafruit_SSD1306 display(WIDTH, HEIGHT, &Wire, -1);
String currentFace = "neutral";
String pending;
bool displayReady = false;

bool validFace(const String &name) {
  return name == "neutral" || name == "happy" || name == "sad" ||
         name == "sleepy" || name == "surprised" || name == "thinking";
}

void drawFace() {
  if (!displayReady) return;
  display.clearDisplay();
  const int cx1 = 39, cx2 = 89, y = 26;
  if (currentFace == "sleepy" || currentFace == "sad") {
    display.drawLine(cx1-13, y, cx1+13, y+3, SSD1306_WHITE);
    display.drawLine(cx2-13, y+3, cx2+13, y, SSD1306_WHITE);
  } else if (currentFace == "happy") {
    display.drawRoundRect(cx1-11, y-4, 22, 12, 5, SSD1306_WHITE);
    display.drawRoundRect(cx2-11, y-4, 22, 12, 5, SSD1306_WHITE);
  } else if (currentFace == "surprised") {
    display.drawCircle(cx1, y, 9, SSD1306_WHITE);
    display.drawCircle(cx2, y, 9, SSD1306_WHITE);
  } else {
    display.fillRoundRect(cx1-9, y-9, 18, 23, 7, SSD1306_WHITE);
    display.fillRoundRect(cx2-9, y-9, 18, 23, 7, SSD1306_WHITE);
  }
  if (currentFace == "thinking") display.drawLine(75, 10, 101, 14, SSD1306_WHITE);
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(4, 53);
  display.print("macdesk / ");
  display.print(currentFace);
  display.display();
}
void reply(const char *type, const String &detail, const String &value) {
  JsonDocument doc;
  doc["type"] = type;
  doc[detail] = value;
  serializeJson(doc, Serial);
  Serial.println();
}
void handleLine(const String &line) {
  JsonDocument doc;
  if (deserializeJson(doc, line)) { reply("error", "reason", "invalid_json"); return; }
  if (doc["cmd"] != "face" || !doc["value"].is<const char*>()) {
    reply("error", "reason", "unknown_command"); return;
  }
  String requested = doc["value"].as<String>();
  if (!validFace(requested)) { reply("error", "reason", "invalid_face"); return; }
  currentFace = requested;
  drawFace();
  reply("ack", "face", currentFace);
}
void setup() {
  Serial.begin(115200);
  Wire.begin(PIN_SDA, PIN_SCL);
  displayReady = display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR);
  if (displayReady) drawFace();
  reply("ready", "display", displayReady ? "ok" : "not_found");
}
void loop() {
  while (Serial.available()) {
    char ch = (char)Serial.read();
    if (ch == '\n') {
      handleLine(pending);
      pending = "";
    } else if (ch != '\r') {
      if (pending.length() >= 255) {
        pending = "";
        reply("error", "reason", "line_too_long");
      } else pending += ch;
    }
  }
}
