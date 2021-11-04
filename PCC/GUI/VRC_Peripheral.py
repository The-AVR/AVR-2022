# VRC Peripheral Python Library
# Written by Casey Hanner
import serial
import time
from struct import pack, unpack

class VRC_peripheral(object):
    def __init__(self, port, use_serial=True):
        self.port = port

        self.PREAMBLE = (0x24, 0x50)

        self.HEADER_OUTGOING = (*self.PREAMBLE, 0x3c)
        self.HEADER_INCOMING = (*self.PREAMBLE, 0x3e)

        self.commands = {
            'SET_SERVO_OPEN_CLOSE':0,
            'SET_SERVO_MIN':1,
            'SET_SERVO_MAX':2,
            'SET_SERVO_PCT':3,
            'SET_BASE_COLOR':4,
            'SET_TEMP_COLOR':5,
            'RESET_VRC_PERIPH':6,
            'CHECK_SERVO_CONTROLLER':7
        }

        self.use_serial = use_serial

        if self.use_serial is True:

            print("opening serial port")
            self.ser = serial.Serial()
            self.ser.baudrate = 115200
            self.ser.port = self.port
            self.ser.open()

        else:
            print("VRC_Peripheral: Serial Transmission is OFF")        

        self.shutdown = False

    def run(self):
        while self.shutdown is False:
            if self.use_serial is True:
                while self.ser.in_waiting > 0:
                    print(self.ser.read(1),end='')
            time.sleep(.01)
                
    def set_base_color(self, wrgb: list):
        #wrgb + code = 5
        if len(wrgb) != 4:
            wrgb = [0,0,0,0]

        for i,color in enumerate(wrgb):
            if color > 255 or color < 0:
                wrgb[i] = 0

        command = self.commands['SET_BASE_COLOR']
        data = self._construct_payload(command,1 + len(wrgb),wrgb)
        

        if self.use_serial is True:
            self.ser.write(data)
        else:
            print("VRC_Peripheral serial data: ")
            print(data)

    def set_temp_color(self, wrgb: list, time=.5):
        #wrgb + code = 5
        if len(wrgb) != 4:
            wrgb = [0,0,0,0]

        for i,color in enumerate(wrgb):
            if color > 255 or color < 0:
                wrgb[i] = 0

        command = self.commands['SET_TEMP_COLOR']
        time_bytes = self.list_pack("<f",time)
        data = self._construct_payload(command, 1 + len(wrgb)  + len(time_bytes), wrgb + time_bytes)

        if self.use_serial is True:
            self.ser.write(data)
        else:
            print("VRC_Peripheral serial data: ")
            print(data)
    
    def set_servo_open_close(self,servo, action):
        valid_command = False

        command = self.commands['SET_SERVO_OPEN_CLOSE']
        length = 3 # command + servo + action
        data = []

        # 128 is inflection point, over 128 == open; under 128 == close

        if action == 'open':
           data = [servo,150]
           valid_command = True
        elif action == 'close':
           data = [servo,100]
           valid_command = True

        if valid_command:
            if self.use_serial is True:
                self.ser.write(self._construct_payload(command,length,data))
            else:
                print("VRC_Peripheral serial data: ")
                print(data)

    def set_servo_min(self, servo, minimum):
        valid_command = False

        command = self.commands['SET_SERVO_MIN']
        length = 3 # command + servo + min pwm
        data = []
        
        if minimum < 1000 and minimum > 0:
            valid_command = True
            data = [servo,minimum]

        if valid_command:
            if self.use_serial is True:
                self.ser.write(self._construct_payload(command,length,data))
            else:
                print("VRC_Peripheral serial data: ")
                print(data)
    
    def set_servo_max(self, servo, maximum):
        valid_command = False

        command = self.commands['SET_SERVO_MAX']
        length = 3 # command + servo + min pwm
        data = []
        
        if maximum < 1000 and maximum > 0:
            valid_command = True
            data = [servo,maximum]

        if valid_command:
            if self.use_serial is True:
                self.ser.write(self._construct_payload(command,length,data))
            else:
                print("VRC_Peripheral serial data: ")
                print(data)

    def set_servo_pct(self, servo, pct):
        valid_command = False

        command = self.commands['SET_SERVO_PCT']
        length = 3 # command + servo + percent
        data = []

        if pct < 100 and pct > 0:
            valid_command = True
            data = [servo,int(pct)]

        if valid_command:
            if self.use_serial is True:
                self.ser.write(self._construct_payload(command,length,data))
            else:
                print("VRC_Peripheral serial data: ")
                print(data)

    
    def reset_vrc_peripheral(self):

        command  = self.commands['RESET_VRC_PERIPH']
        length = 1 #just the reset command

        if self.use_serial is True:

            self.ser.write(self._construct_payload(command,length))
            self.ser.close()
            #wait for the VRC_Periph to reboot
            time.sleep(5)
            
            #try to reconnect
            self.ser.open()
        else:
            print("VRC_Peripheral reset triggered (NO SERIAL)")
    
    def check_servo_controller(self):
        command = self.commands['CHECK_SERVO_CONTROLLER']
        length = 1
        if self.use_serial is True:
            self.ser.write(self._construct_payload(command,length))
        else:
            print("VRC_Peripheral serial data: ")
            print(data)
    
    def _construct_payload(self, 
                           code: int,
                           size: int = 0,
                           data: list = []
                           ):
        #[$][P][>][LENGTH-HI][LENGTH-LOW][DATA][CRC]
        payload = bytes()

        data = (
            ("<3b", self.HEADER_OUTGOING),
            (">H", [size]),
            ("<B", [code]),
            ("<%dB" % len(data), data)
        )

        for section in data:
            payload += pack(section[0], *section[1])

        data = payload[3:]

        crc = self.calc_crc(payload, len(payload))

        payload += pack("<B", crc)

        return payload
    
    def list_pack(self, bit_format, value):
        bytez = pack(bit_format,value)

        ret_list = []

        for byte in bytez:
            ret_list.append(byte)

        return ret_list
    
    def crc8_dvb_s2(self, crc, a):
        crc ^= a
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0xD5) % 256
            else:
                crc = (crc << 1) % 256
        return crc

    def calc_crc(self, string, length):
        crc = 0
        for i in range(0,length):
            crc = self.crc8_dvb_s2(crc,string[i])
        return crc
