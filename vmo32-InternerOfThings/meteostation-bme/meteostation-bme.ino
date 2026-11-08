#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_BME280.h>

const char* ssid = "PixelHotspot";
const char* password = "jj9i5b9beyv9ujy";
const char* serverUrl = "http://37.220.81.208:5000/data";

Adafruit_BME280 bme;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  Wire.begin(21, 22);

  if (!bme.begin(0x76)) {
    Serial.println("BME280 not found!");
    while (1);
  }
}

void loop() {
  float pressure = bme.readPressure() / 100.0;
  float temp = bme.readTemperature();
  float humidity = bme.readHumidity();

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"temperature\":" + String(temp) + ",";
    json += "\"humidity\":" + String(humidity) + ",";
    json += "\"pressure\":" + String(pressure);
    json += "}";

    http.POST(json);
    http.end();
  }

  delay(60000); // раз в минуту
}