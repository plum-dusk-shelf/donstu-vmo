#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_AHTX0.h>
#include <Adafruit_BMP280.h>

const char* ssid = "PixelHotspot";
const char* password = "jj9i5b9beyv9ujy";
const char* serverUrl = "http://37.220.81.208:5000/data";

Adafruit_AHTX0 aht;
Adafruit_BMP280 bmp;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  aht.begin();
  bmp.begin(0x77);
}

void loop() {
  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);

  float pressure = bmp.readPressure() / 100.0;

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"temperature\":" + String(temp.temperature) + ",";
    json += "\"humidity\":" + String(humidity.relative_humidity) + ",";
    json += "\"pressure\":" + String(pressure);
    json += "}";

    http.POST(json);
    http.end();
  }

  delay(60000); // раз в минуту
}