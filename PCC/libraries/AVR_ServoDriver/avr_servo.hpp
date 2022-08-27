#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define SERVOMIN 150  // This is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX 425  // This is the 'maximum' pulse length count (out of 4096)
#define USMIN 600     // This is the rounded 'minimum' microsecond length based on the minimum pulse of 150
#define USMAX 2400    // This is the rounded 'maximum' microsecond length based on the maximum pulse of 600
#define SERVO_FREQ 50 // Analog servos run at ~50 Hz updates

class AVRServo : public Adafruit_PWMServoDriver
{
public:
    AVRServo();

    void open_servo(uint8_t servo);
    void close_servo(uint8_t servo);
    void set_servo_percent(uint8_t servo, uint8_t percent);
    void set_servo_absolute(uint8_t servo, uint16_t absolute);

    void set_servo_min();
    void set_servo_max();
    uint8_t check_controller(void);

private:
    uint16_t servo_min;
    uint16_t servo_max;
};