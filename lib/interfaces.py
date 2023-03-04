import json
import board
import busio
import adafruit_bmp280
import digitalio


def _get_SPI_pins(data):
    pins = data['SPI']
    return getattr(board, pins['SCK']), getattr(board, pins['MISO']), getattr(board, pins['MOSI'])


def _get_I2C_pins(data):
    pins = data['I2C']
    return getattr(board, pins['SCL']), getattr(board, pins['SDA'])


def _get_UART_pins(data):
    pins = data['UART']
    return getattr(board, pins['TX']), getattr(board, pins['RX'])


class Interface:
    def __init__(self, config_path):
        with open(config_path, 'r') as fp:
            data = json.load(fp)

        sck, miso, mosi = _get_SPI_pins(data)
        scl, sda = _get_I2C_pins(data)
        tx, rx = _get_UART_pins(data)

        self.SPI = busio.SPI(sck, MISO=miso, MOSI=mosi)
        self.I2C = busio.I2C(scl, sda)
        self.UART = busio.UART(tx, rx)

        self.bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(self.I2C)
        self.bmp280.sea_level_pressure = 1013.25

        out = getattr(board, data['SX1276']['cs'])
        self.lora_cs = digitalio.DigitalInOut(out)
        self.lora_cs.direction = digitalio.Direction.OUTPUT
        self.lora_cs.value = True

    def _read_bmp280_data(self):
        return self.bmp280.temperature, self.bmp280.pressure, self.bmp280.altitude

    def send_bmp280_data(self):
        t, p, a = self._read_bmp280_data()
        self.lora_cs.value = False
        self.SPI.write([t, p, a])
        self.lora_cs.value = True



