#include <Arduino.h>
#include "serial_lib.hpp"
#include "avr_led.hpp"
#include "avr_servo.hpp"

//////////////// S E R I A L  I N T E R F A C E ///////////////
uint16_t queue_len = 10;
uint16_t entry_size = sizeof(packet_t);

cppQueue q(entry_size, queue_len, FIFO);

AVRSerialParser serial(Serial, q);
///////////////////////////////////////////////////////////////

///////////////// N E O - P I X E L S /////////////////////////
#define NEO_PIN 5
#define PWR_PIN 10
#define LASER_PIN A4

// Seconds the laser is allowed to be on for
#define LASER_ON_SECONDS 0.25
// Seconds before the laser can be activated again
#define LASER_NEXT_ALLOW_SECONDS 0.75

#define LASER_BLIP_SECONDS 0.1
#define LASER_NEXT_BLIP_SECONDS 0.5

#define NUM_PIXELS 30

AVRLED strip(NEO_PIN, NUM_PIXELS, NEO_GRB);
AVRLED onboard(8, 2, NEO_GRB);
///////////////////////////////////////////////////////////////

/////////////// S E R V O S ///////////////////////////////////
AVRServo servos = AVRServo();
///////////////////////////////////////////////////////////////

void setup()
{
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(PWR_PIN, OUTPUT);
  digitalWrite(PWR_PIN, HIGH);
  pinMode(LASER_PIN,OUTPUT);


  //////////// N E O - P I X E L  S E T U P ////////////////////
  strip.begin();
  strip.setBrightness(255);
  strip.show();

  onboard.begin();
  onboard.setBrightness(64);
  onboard.show();
  //////////////////////////////////////////////////////////////

  ///////////// S E R V O  S E T U P ///////////////////////////
  servos.begin();
  servos.setOscillatorFrequency(27000000);
  servos.setPWMFreq(SERVO_FREQ);
  //////////////////////////////////////////////////////////////

  Serial.println("init");
}

double next_allow_laser = -1;
double next_force_laser_off = 999999999999;
double next_force_laser_on = 0;
unsigned long light_on = 0;
unsigned long laser_on = 0;




void loop()
{
  // put your main code here, to run repeatedly:
  serial.poll();

  if (serial.available > 0)
  {
    packet_t message;
    cmd_result res = serial.get_command(&message);
    //Serial.printf("res: %d", res);
    digitalWrite(LED_BUILTIN, HIGH);
    light_on = millis();

    switch (message.command)
    {
    case SET_BASE_COLOR:
    {
      uint8_t white = message.data[0];
      uint8_t red = message.data[1];
      uint8_t green = message.data[2];
      uint8_t blue = message.data[3];
      strip.set_base_color_target(white, red, green, blue);
      //onboard.set_color_target(0,red,green,blue);
    }
    break;
    case SET_TEMP_COLOR:
    {
      uint8_t white = message.data[0];
      uint8_t red = message.data[1];
      uint8_t green = message.data[2];
      uint8_t blue = message.data[3];

      float time = 1.0;

      memcpy(&time, &message.data[4], sizeof(float));

      //Serial.printf("Time %f",time);

      strip.set_temp_color_target(white, red, green, blue);

      uint32_t long_time = (uint32_t)(time * 1000.0);
      strip.show_temp_color(long_time);
      //onboard.set_temp_color_target(0,red,green,blue);
    }
    break;
    case SET_SERVO_OPEN_CLOSE:
    {
      uint8_t which_servo = message.data[0];
      uint8_t value = message.data[1];

      if (value > 127)
      {
        servos.open_servo(which_servo);
        onboard.set_base_color_target(0, 255, 0, 0);
      }
      else
      {
        servos.close_servo(which_servo);
        onboard.set_base_color_target(0, 0, 255, 0);
      }
    }
    break;
    case SET_SERVO_PCT:
    {
      uint8_t which_servo = message.data[0];
      uint8_t percent = message.data[1];

      servos.set_servo_percent(which_servo, percent);
    }
    break;
    case RESET_AVR_PERIPH:
    {
      //digitalWrite(RST_PIN,LOW);
    }
    break;
    case CHECK_SERVO_CONTROLLER:
    {
      //Serial.printf("Checking controller...\n");
      uint8_t res = servos.check_controller();
      //Serial.printf("Res: %d\n",res);
    }
    break;
    case SET_LASER_OFF:
    {
        laser_on = 0;
        digitalWrite(LED_BUILTIN, LOW);
    }
    break;
    case SET_LASER_ON:
    {
        laser_on = 1;
        digitalWrite(LASER_PIN,HIGH);
        next_force_laser_off = millis() + LASER_BLIP_SECONDS * 1000;
        next_force_laser_on = millis() + LASER_NEXT_BLIP_SECONDS * 1000;
    }
    break;
    case FIRE_LASER:
    {
      if (millis() > next_allow_laser) {
        digitalWrite(LASER_PIN,HIGH);
        next_force_laser_off = millis() + LASER_ON_SECONDS * 1000;
        next_allow_laser = millis() + LASER_NEXT_ALLOW_SECONDS * 1000;
      }
    }
    break;
    }
  }

  if (millis() - light_on > 100)
  {
    digitalWrite(LED_BUILTIN, LOW);
  }

  if (millis() > next_force_laser_off)
  {
    digitalWrite(LASER_PIN,LOW);
    next_force_laser_off = 999999999999;
  }

  if (millis() > next_force_laser_on)
  {
    if (laser_on) {
        digitalWrite(LASER_PIN,HIGH);
    }
    next_force_laser_off = millis() + LASER_BLIP_SECONDS * 1000;
    next_force_laser_on = millis() + LASER_NEXT_BLIP_SECONDS * 1000;
  }

  strip.run();
  onboard.run();
}

// void colorWipe(void)
// {
//   uint16_t i;

//   // 'Color wipe' across all pixels
//   for(uint32_t c = 0xFF000000; c; c >>= 8) { // Red, green, blue  wgrb
//     for(i=0;i<strip.numPixels(); i++) {
//       strip.setPixelColor(i, c);
//       strip.show();
//       delay(500);
//     }
//   }
// }
