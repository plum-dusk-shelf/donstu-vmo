#define LED_BUILTIN 2
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}
void loop() {
  for(int i = 0; i < 255; i+=1){
    analogWrite(LED_BUILTIN, i);
    delay(5);
  }
  delay(50);
  for(int i = 255; i > 0; i-=1){
    analogWrite(LED_BUILTIN, i);
    delay(5);
  }
  delay(300);
}