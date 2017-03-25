//Pins for the components and sensors
int cameraPin = 2;
int pirPin = 4;
int onoffPin = 7;   //button toggle for surveillance notes
int ledPin = 6;

//Surveillance mode ON/OFF
int survState = LOW;
//Motion currently happening YES/NO
int pirState = LOW;
//The length of the video clip recorded each time (milliseconds)
int recordTime = 10000;

void setup() {
  //Set up the pins
  pinMode(pirPin, INPUT);
  pinMode(onoffPin, INPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(cameraPin, OUTPUT);
  //The camera begins at HIGH
  digitalWrite(cameraPin, HIGH);
  Serial.begin(9600);
}

//Toggles surveillance mode and LED light
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

//Trigger the camera to begin or end recording
void triggerCamera() {
  digitalWrite(cameraPin, LOW);
  delay(550);   //>500ms for video and <=500ms for photo
  digitalWrite(cameraPin, HIGH);
}

void loop() {
  //Read the PIR value and the button value
  int val = digitalRead(pirPin);
  int onoffVal = digitalRead(onoffPin);
  
  // Button was pressed = switch states
  if (onoffVal == HIGH) {
    switchState(survState);
    delay(200);
    delay(2000); //slight delay between presses
  }

  //If surveillance mode is ON
  if (survState == HIGH) {
    //And the PIR detects motion
    if (val == HIGH) {
      //And the PIR state was previously OFF
      if (pirState == LOW) {
        //Tell the Python script to send an email
        Serial.println("Motion detected!");

        //Trigger the camera to record a video
        triggerCamera();
        delay(3000+recordTime);
        triggerCamera();
        delay(200);
        
        pirState = HIGH;
      }
    }
    else {
      //The PIR stops detecting motion
      if (pirState == HIGH) {
        Serial.println("Motion ended!");
        pirState = LOW;
      }
    }
  }
}
