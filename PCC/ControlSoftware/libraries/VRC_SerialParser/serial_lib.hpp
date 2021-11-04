#include <Arduino.h>
#include "cppQueue.h"

typedef enum 
{
    IDLE,
    START,
    CC,
    DIRECTION,
    LENGTH_HI,
    LENGTH_LOW,
    DATA,
    CRC
}uart_states;


typedef enum
{
    SET_SERVO_OPEN_CLOSE,
    SET_SERVO_MIN,
    SET_SERVO_MAX,
    SET_SERVO_PCT,
    SET_BASE_COLOR,
    SET_TEMP_COLOR,
    RESET_VRC_PERIPH,
    CHECK_SERVO_CONTROLLER,
    COMMAND_END
} commands;


typedef struct 
{
  uint8_t command;
  uint8_t data[128];
} packet_t;

typedef enum
{
    QUEUE_EMPTY,
    SUCCESS,
} cmd_result;

static char* outgoing_preamble = "$P>";//towards arduino
static char* incoming_preamble = "$P<";//towards jetson

class VRCSerialParser 
{
  public:
    VRCSerialParser(Adafruit_USBD_CDC port, cppQueue queue_q);
    void poll(void);
    uart_states get_state(void);
    cmd_result get_command(packet_t* msg);
    uint32_t available = 0;
  private:
    Adafruit_USBD_CDC serial_bus;  //arduino serial object
    uart_states state;
    unsigned long last_byte_received = 0;

    //temp space for receiving sm to work with...
    uint8_t length_bytes[2] = {0};
    uint16_t length = 0;
    uint8_t data_bytes[512] = {0};
    uint16_t write_index = 0;
    uint8_t crc_bytes[2] = {0};
    uint8_t messages_available = 0;
    
    uint8_t crc8_dvb_s2(uint8_t crc, unsigned char a);
    uint8_t calc_crc(uint8_t* buffer, uint16_t length);

    uint32_t messages_dropped=0;

    cppQueue q;

    
};


