from time import sleep, localtime
from threading import Thread
from tm1637 import TM1637
import Adafruit_DHT
# import drivers
import RPi.GPIO as GPIO
# import board
# import busio
# import adafruit_character_lcd.character_lcd_i2c as character_lcd
import drivers


import subprocess

lcd_columns = 20
lcd_rows = 4
# i2cAddress = 0x27
display = drivers.Lcd()
# display.lcd_backlight(1)


DIOHora = 27
CLKHora = 22

DIOCronometro = 17
CLKCronometro = 4

pin_btn_central = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_btn_central, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

ip = subprocess.check_output(['hostname', '-I']).decode().strip()


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

    def run(self):
        horaJapon = 0
        encendidoLuz = False
        diaSiguiente = False
        tiempoLuz = 10

        while True:
            t = localtime()
            tiempoHora = t.tm_hour
            tiempoMin = t.tm_min
            tiempoSegundos = t.tm_sec

            horaJapon = tiempoHora + 15
            if horaJapon > 24:
                horaJapon = horaJapon - 24
                diaSiguiente = True

            if GPIO.input(pin_btn_central) == GPIO.HIGH:
                if diaSiguiente == True:
                    display.lcd_display_string(
                        'Tokyo: ' + str(horaJapon) + ':' + str(tiempoMin) + ' |*|   ', 1)
                else:
                    display.lcd_display_string(
                        'Tokyo: ' + str(horaJapon) + ':' + str(tiempoMin) + '       ', 1)
                display.lcd_display_string(ip, 4)
                encendidoLuz = True
                tiempoLuz = t.tm_sec

            if encendidoLuz == True and tiempoSegundos <= tiempoLuz + 2 and GPIO.input(pin_btn_central) == GPIO.LOW:
                display.lcd_backlight(1)
            else:
                display.lcd_backlight(0)
                encendidoLuz = False


if __name__ == '__main__':
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
