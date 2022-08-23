#include "avr_servo.hpp"

AVRServo::AVRServo() : Adafruit_PWMServoDriver()
{
    servo_min = SERVOMIN;
    servo_max = SERVOMAX;
}

void AVRServo::open_servo(uint8_t servo)
{
    setPWM(servo, 0, servo_max);
}

void AVRServo::close_servo(uint8_t servo)
{
    setPWM(servo, 0, servo_min);
}

void AVRServo::set_servo_percent(uint8_t servo, uint8_t percent)
{
    if (percent > 100)
        percent = 100;

    uint16_t pwm = map(percent, 0, servo_min, 100, servo_max);

    setPWM(servo, 0, pwm);
}

void AVRServo::set_servo_absolute(uint8_t servo, uint16_t absolute)
{
    writeMicroseconds(servo, absolute);
}

uint8_t AVRServo::check_controller(void)
{
    int res = (int)readPrescale();

    if (res != 0)
        return 1;
    else
        return 0;
}