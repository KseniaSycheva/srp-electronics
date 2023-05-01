import board


def get_uart_pins(data):
   pins = data['UART']
   return getattr(board, pins['TX']), getattr(board, pins['RX'])


def get_i2c_pins(data):
   pins = data['I2C']
   return getattr(board, pins['SCL']), getattr(board, pins['SDA'])


def get_spi_pins(data):
    pins = data['SPI']
    return getattr(board, pins['SCLK']), getattr(board, pins['MISO']), getattr(board, pins['MOSI'])
