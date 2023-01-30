from time import sleep, localtime
from threading import Thread
from tm1637 import TM1637
import Adafruit_DHT
import drivers
import RPi.GPIO as GPIO

# import socket
# import fcntl
# import struct
import os
import subprocess


DIOHora = 27
CLKHora = 22

DIOCronometro = 17
CLKCronometro = 4

display = drivers.Lcd()
pin_btn = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_btn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

ip = subprocess.check_output(['hostname', '-I']).decode().strip()

# def get_ip_address(ifname):
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     return socket.inet_ntoa(fcntl.ioctl(
#         s.fileno(),
#         0x8915,
#         struct.pack('256s', ifname[:15])
#     )[20:24])


class Clock:
    def __init__(self, tm_instance):
        self.tm = tm_instance
        self.show_colon = False

    def run(self):
        while True:
            t = localtime()
            if t.tm_hour > 12:
                hora = t.tm_hour-12
            else:
                hora = t.tm_hour
            self.show_colon = not self.show_colon
            tm.numbers(hora, t.tm_min, self.show_colon)
            sleep(1)


class Temp:
    def __init__(self, tm_instance):
        self._running = True
        self.tm2 = tm_instance

    def run(self):
        DHT_SENSOR = Adafruit_DHT.DHT22
        DHT_PIN = 14

        while True:
            humidity, temperature = Adafruit_DHT.read_retry(
                DHT_SENSOR, DHT_PIN)
            if humidity is not None and temperature is not None:
                tm2.numbers(int(temperature), int(humidity), False)
                #print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
            else:
                tm2.numbers(88, 88, True)
                #print("Failed to retrieve data from humidity sensor")


class Lcd20x4:
    def __init__(self):
        self.running = True

        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # return socket.inet_ntoa(fcntl.ioctl(
        #     s.fileno(),
        #     0x8915,
        #     struct.pack('256s', ifname[:15])
        # )[20:24])

    def run(self):
        horaJapon = 0
        diaSiguiente = False

        while True:
            if GPIO.input(pin_btn) == GPIO.HIGH:
                print('Me estas tocando bb')
                # display.lcd_display_extended_string('Luz Encendida', 4)
            # else:
                # display.lcd_display_extended_string('Luz Apagada     ', 4)
            display.lcd_display_string(ip, 4)

            t = localtime()
            tiempoHora = t.tm_hour
            tiempoMin = t.tm_min
            horaJapon = tiempoHora + 15
            if horaJapon > 24:
                horaJapon = horaJapon - 24
                diaSiguiente = True
            if diaSiguiente == True:
                display.lcd_display_string(
                    'Tokyo: ' + str(horaJapon) + ':' + str(tiempoMin) + ' |*|', 1)

            else:
                display.lcd_display_string(
                    'Tokyo: ' + str(horaJapon) + ':' + str(tiempoMin) + '      ', 1)


if __name__ == '__main__':
    display.lcd_backlight(0)
    tm = TM1637(CLKHora, DIOHora)
    tm.brightness(7)
    Reloj = Clock(tm)

    RelojThread = Thread(target=Reloj.run)
    RelojThread.start()

    tm2 = TM1637(CLKCronometro, DIOCronometro)
    tm2.brightness(7)

    PantallaAzul = Lcd20x4()
    PantallaAzulThread = Thread(target=PantallaAzul.run)
    PantallaAzulThread.start()

    Temperatura = Temp(tm2)
    TemperaturaThread = Thread(target=Temperatura.run)
    TemperaturaThread.start()
