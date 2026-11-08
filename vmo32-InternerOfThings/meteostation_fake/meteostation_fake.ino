#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "PixelHotspot";
const char* password = "jj9i5b9beyv9ujy";
const char* serverUrl = "http://37.220.81.208:5000/data";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi connected");
}

void loop() {
  float temp = random(200, 300) / 10.0;
  float hum  = random(300, 700) / 10.0;
  float pres = random(9900, 10300) / 10.0;

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"temperature\":" + String(temp) + ",";
    json += "\"humidity\":" + String(hum) + ",";
    json += "\"pressure\":" + String(pres);
    json += "}";

    int code = http.POST(json);

    if (code > 0) {
      Serial.printf("HTTP OK: %d\n", code);
    } else {
      Serial.printf("HTTP ERROR: %s\n", http.errorToString(code).c_str());
    }

    Serial.print("HTTP response: ");
    Serial.println(code);

    http.end();
  }

  delay(10000);
}