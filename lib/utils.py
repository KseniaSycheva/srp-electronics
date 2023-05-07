import board
import random


def get_uart_pins(data):
   pins = data['UART']
   return getattr(board, pins['TX']), getattr(board, pins['RX'])


def get_i2c_pins(data):
   pins = data['I2C']
   return getattr(board, pins['SCL']), getattr(board, pins['SDA'])


def get_spi_pins(data):
    pins = data['SPI']
    return getattr(board, pins['SCLK']), getattr(board, pins['MISO']), getattr(board, pins['MOSI'])


def get_sdcard_pins(data):
    sd_cs = data['microSD']["cs"]
    return getattr(board, sd_cs)


def get_lora_pins(data):
    lora_cs = data['SX1276']["cs"]
    lora_rst = data['SX1276']["RST"]
    return getattr(board, lora_cs), getattr(board, lora_rst)


async def update_buffer(buffer, bmp280, gps):
    success = False
    try:
        buffer['temperature'].append(bmp280.temperature)
        buffer['pressure'].append(bmp280.pressure)
        buffer['altitude'].append(bmp280.altitude)
        success = True
    except:
        pass
    try:
        gps.update()
        if not gps.has_fix:
            return success
        buffer['latitude'].append(gps.latitude)
        buffer['longitude'].append(gps.longitude)
        buffer['latitude_degrees'].append(gps.latitude_degrees)
        buffer['longitude_degrees'].append(gps.longitude_degrees)
        buffer['latitude_minutes'].append(gps.latitude_minutes)
        buffer['longitude_minutes'].append(gps.longitude_minutes)
        success = True
    except:
        pass

    return success


async def save_and_transmit(sd, rfmx9, data):
    pass


class FakeDevice:
    def __init__(self, device_name):
        self.name = device_name
        random.seed(42)


class FakeBMP280(FakeDevice):
    def __init__(self):
        super().__init__("bmp280")
        self.altitude = random.random()
        self.pressure = random.random()
        self.sea_level_pressure = random.random()
        self.temperature = random.random()


class FakeGPS(FakeDevice):
    def __init__(self):
        super().__init__("gps")
        self.latitude = random.random()
        self.longitude = random.random()
        self.latitude_degrees = random.random()
        self.longitude_degrees = random.random()
        self.latitude_minutes = random.random()
        self.longitude_minutes = random.random()

    def send_command(self, command):
        print(f'Sending command {command}')

    def update(self):
        pass

    def has_fix(self):
        return random.random() > 0.5


class FakeRFM9X(FakeDevice):
    def __init__(self):
        super().__init__("rfm9x")

    def send(self, command):
        pass