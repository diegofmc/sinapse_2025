# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import digitalio
import adafruit_max31856
from multiplex import Multiplex

# Create sensor object, communicating over the board's default SPI bus
spi = board.SPI()

# allocate a CS pin and set the direction
cs = digitalio.DigitalInOut(board.PA7)
cs.direction = digitalio.Direction.OUTPUT

# create a thermocouple object with the above
thermocouple = adafruit_max31856.MAX31856(spi, cs)

mp = Multiplex()
mp.set_canal(16)
mp.set_sensor(1)

# print the temperature!
print(thermocouple.temperature)
print(thermocouple.reference_temperature)
