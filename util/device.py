"PM2.5 module"
import board, busio
from adafruit_pm25.i2c import PM25_I2C

# DEVICE READER
reset_pin = None
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
pm25 = PM25_I2C(i2c, reset_pin)

def getPM25():
    return pm25



