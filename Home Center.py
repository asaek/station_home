from time import sleep, localtime
from threading import Thread
from tm1637 import TM1637
import Adafruit_DHT
import drivers
from datetime import datetime

DIOHora = 27
CLKHora = 22

DIOCronometro = 17
CLKCronometro = 4

display = drivers.Lcd()

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
#             if GPIO.input(32) == GPIO.HIGH:
#                 print("Button was pushed!")

            horaJapon = 0
            diaSiguiente = False
            tiempoHora = t.tm_hour
            tiempoMin = t.tm_min
            horaJapon = tiempoHora + 15

            if horaJapon > 24:
                horaJapon = horaJapon - 24
                diaSiguiente = True
            
            if diaSiguiente == True:
                display.lcd_display_string('Tokyo: ' + str(horaJapon) + ':' + str(tiempoMin) + ' |*|', 1)
            else:
                display.lcd_display_string('Tokyo: ' + str(horaJapon) + ':' + str(tiempoMin) , 1)
                
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


if __name__ == '__main__':
    tm = TM1637(CLKHora, DIOHora)
    tm.brightness(7)
    Reloj = Clock(tm)
    RelojThread = Thread(target=Reloj.run)
    RelojThread.start()

    tm2 = TM1637(CLKCronometro, DIOCronometro)
    tm2.brightness(7)
#     CronometroRun = Cronometro(tm2)
#     CronometroThread = Thread(target=CronometroRun.run)
#     CronometroThread.start()

    Temperatura = Temp(tm2)
    TemperaturaThread = Thread(target=Temperatura.run)
    TemperaturaThread.start()
