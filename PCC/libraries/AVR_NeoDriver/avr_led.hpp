#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_NeoPixel.h>

class AVRLED : public Adafruit_NeoPixel
{
public:
    AVRLED(uint8_t pin, uint8_t num_pixels, neoPixelType t = NEO_GRBW);
    void show_temp_color(uint32_t seconds);
    void set_temp_color_target(uint8_t white, uint8_t red, uint8_t green, uint8_t blue);
    void set_base_color_target(uint8_t white, uint8_t red, uint8_t green, uint8_t blue);
    void set_strip_color(void);
    void run(void);
    //uint32_t get_strip_color(void);
    //uint8_t get_red_channel(void);
    //uint8_t get_green_channel(void);
    //uint8_t get_blue_channel(void);
    //uint8_t get_white_channel(void);

private:
    //uint8_t rgbw[4] = {0};

    uint32_t current_color = 0;
    uint32_t temp_color = 0;
    uint32_t base_color = 0;

    uint32_t temp_start = 0;
    uint32_t temp_duration = 0;
    uint32_t last_strip_show = 0;

    bool needs_color_update = false;
    bool temp_running = false;
};