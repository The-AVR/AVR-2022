#CLI Test app to test functionality of the VRC Peripheral Control Computer
#written by Casey Hanner
from VRC_Peripheral import VRC_peripheral

import sys, threading, time, queue

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()

class VRC_peripheral_test(object):
    def __init__(self, port):
        self.port = port

        self.vrc_p = VRC_peripheral(self.port, use_serial=True)

        #button input queue & listening thread
        print("creating queue")
        self.input_queue = queue.Queue()
        print("creating thread")
        self.input_thread = threading.Thread(target=self.add_input, args=(self.input_queue,))
        self.input_thread.daemon = True

        # self.serial_thread = threading.Thread(target=self.vrc_p.run)
        # self.serial_thread.daemon = True

        self.shutdown = False

    def run(self):
        print("starting threads")
        self.input_thread.start()
        # self.serial_thread.start()
        print("starting listening")
        while self.shutdown is False:
            if not self.input_queue.empty():
                kinput = self.input_queue.get()
                #print ("\ninput:", kinput)
                color = [0,0,0,0]
                if kinput == b'w':
                    color = [255,0,0,0]
                    self.vrc_p.set_base_color(color)
                elif kinput == b'r':
                    color = [0,255,0,0]
                    self.vrc_p.set_temp_color(color)
                elif kinput == b'g':
                    color = [0,0,255,0]
                    self.vrc_p.set_temp_color(color)
                elif kinput == b'b':
                    color = [0,0,0,255]
                    self.vrc_p.set_temp_color(color)
                elif kinput == b't':
                    color = [0,255,255,0]
                    self.vrc_p.set_base_color(color)
                elif kinput == b'h':
                    color = [0,52,235,150]
                    self.vrc_p.set_base_color(color)
                elif kinput == b'n':
                    color = [0,235,52,229]
                    self.vrc_p.set_base_color(color)
                elif kinput == b'q':
                    self.vrc_p.reset_vrc_peripheral()
                
                elif kinput == b'4':
                    self.vrc_p.set_servo_open_close(0, 'open')
                elif kinput == b'1':
                    self.vrc_p.set_servo_open_close(0, 'close')
                
                elif kinput == b'5':
                    self.vrc_p.set_servo_open_close(1, 'open')
                elif kinput == b'2':
                    self.vrc_p.set_servo_open_close(1, 'close')
                
                elif kinput == b'6':
                    self.vrc_p.set_servo_open_close(2, 'open')
                elif kinput == b'3':
                    self.vrc_p.set_servo_open_close(2, 'close')

                elif kinput == b'+':
                    self.vrc_p.set_servo_open_close(3, 'open')
                elif kinput == b'\r':
                    self.vrc_p.set_servo_open_close(3, 'close')
                elif kinput == b'z':
                    self.vrc_p.check_servo_controller()
                else:
                    self.vrc_p.set_base_color(color)
            time.sleep(.01)


    def add_input(self,input_queue):
        while True:
            #input_queue.put(sys.stdin.read(1))
            char = getch()
            if char == b'\x03':
                self.shutdown = True
                raise KeyboardInterrupt
            else:
                input_queue.put(char)
            time.sleep(.01)

if __name__ == "__main__":
    try:
        print("creating module")
        test = VRC_peripheral_test("COM6")
        print("starting module")
        test.run()
    finally:
        test.vrc_p.ser.close()

