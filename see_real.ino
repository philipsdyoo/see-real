int cameraPin = 2;
int pirPin = 4;
int onoffPin = 7;
int ledPin = 6;

int survState = LOW;
int pirState = LOW;
int recordTime = 5000;

void setup() {
  pinMode(pirPin, INPUT);
  pinMode(onoffPin, INPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(cameraPin, OUTPUT);
  digitalWrite(cameraPin, HIGH);
  Serial.begin(9600);
}

void switchState(int prev) {
  if (prev == 1) {
    survState = LOW;
    digitalWrite(ledPin, LOW);
  }
  else {
    survState = HIGH;
    digitalWrite(ledPin, HIGH);
  }
}

void triggerCamera() {
  digitalWrite(cameraPin, LOW);
  delay(550);
  digitalWrite(cameraPin, HIGH);
}

void loop() {
  int val = digitalRead(pirPin);
  int onoffVal = digitalRead(onoffPin);
  
  // Button was pressed = switch states
  if (onoffVal == HIGH) {
    switchState(survState);
    delay(200);
  }

  if (survState == HIGH) {
    if (val == HIGH) {
      if (pirState == LOW) {
        Serial.println("Motion detected!");
        
        triggerCamera();
        delay(3000+recordTime);
        triggerCamera();
        delay(200);
        
        pirState = HIGH;
      }
    }
    else {
      if (pirState == HIGH) {
        Serial.println("Motion ended!");
        pirState = LOW;
      }
    }
  }
}
