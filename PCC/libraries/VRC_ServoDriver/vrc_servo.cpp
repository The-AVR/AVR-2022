#include "vrc_servo.hpp"

VRCServo::VRCServo() : Adafruit_PWMServoDriver()
{
    servo_min = SERVOMIN;
    servo_max = SERVOMAX;
}

void VRCServo::open_servo(uint8_t servo)
{
    setPWM(servo, 0, servo_max);
}

void VRCServo::close_servo(uint8_t servo)
{
    setPWM(servo, 0, servo_min);
}

void VRCServo::set_servo_percent(uint8_t servo, uint8_t percent)
{
    if (percent > 100)
        percent = 100;

    uint16_t pwm = map(percent, 0, servo_min, 100, servo_max);

    setPWM(servo, 0, pwm);
}
uint8_t VRCServo::check_controller(void)
{
    int res = (int)readPrescale();

    if (res != 0)
        return 1;
    else
        return 0;
}