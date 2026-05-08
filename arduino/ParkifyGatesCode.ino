#include <Servo.h>
Servo servo1;
Servo servo2; 
String command = "";

bool EntryGateInOpen = false;
bool ExitGateInOpen = false;
unsigned long EntryGateInOpenTime = 0;
unsigned long ExitGateInOpenTime = 0;

void setup() {
  Serial.begin(9600);
  
  servo1.attach(9); 
  servo2.attach(10);

  servo1.write(90);  
  servo2.write(90);

  Serial.println("SYSTEM IS READY");
}

void loop() {
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "OPEN_ENTRY_GATE") {
      servo1.write(0);  
      EntryGateInOpen = true;
      EntryGateInOpenTime = millis(); 
      Serial.println("Entry Gate Is Open");
    }

    else if (command == "OPEN_EXIT_GATE") {
      servo2.write(0);  
      ExitGateInOpen = true;
      ExitGateInOpenTime = millis(); 
      Serial.println("Exit Gate Is Open");
    }
  }

 
  if (EntryGateInOpen && (millis() - EntryGateInOpenTime >= 10000)) {
    servo1.write(90); 
    EntryGateInOpen = false;
    Serial.println("Entry Gate Is Closed Automatically after 10 Seconds");
  }


  if (ExitGateInOpen && (millis() - ExitGateInOpenTime >= 10000)) {
    servo2.write(90); 
    ExitGateInOpen = false;
    Serial.println("Exit Gate Is Closed Automatically after 10 Seconds");
  }
}
