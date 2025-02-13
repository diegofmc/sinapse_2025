import board
import digitalio
import adafruit_max31856
from multiplex import Multiplex3
import time

# Create sensor object, communicating over the board's default SPI bus
spi = board.SPI()

# allocate a CS pin and set the direction
cs = digitalio.DigitalInOut(board.PA7)
cs.direction = digitalio.Direction.OUTPUT

mp = Multiplex3()
mp.set_canal(1)
mp.set_sensor(1)

# create a thermocouple object with the above
thermocouple = adafruit_max31856.MAX31856(spi, cs)

# print the temperature!
#print(thermocouple.temperature)

#print the internal temperature
#print(thermocouple.reference_temperature)

sensor = 1
canal = 3
while(sensor != 17):
    mp.set_canal(canal)
    mp.set_sensor(sensor)
    time.sleep(0.5)
    #canal = canal + 1
    #if(canal > 16):
    #    sensor = 16
    print(thermocouple.temperature)
    sensor = sensor + 1
