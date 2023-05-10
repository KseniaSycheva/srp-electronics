import asyncio
import external
import time
import digitalio
import statemachine
import buzzer
import adafruit_bmp280
import adafruit_gps
import adafruit_rfm9x
import busio
import json
from utils import *
import os


async def fire_pyro_backup(states):
   while True:
      if states.check_if_pyro_should_be_fired():
         external.neopixel_set_rgb(255,30,70)
         external.PYRO_DETONATE()
      buzzer.buzzer_tick()
      states.tick()
      await asyncio.sleep(0.1)


async def poll_sensors(statemachine, bmp280, gps, rfm9x, data):
   last_measured = time.time()
   curr_buffer_size = 0
   init_altitude = bmp280.altitude
   mode = 'w'
   counter = 0
   should_save = True

   while True:
      if statemachine.state == 4:  # state is armed
         # start data collection at 1 input per second
         if time.time() - last_measured > 1:
            success = await update_buffer(data, bmp280, gps)
            if success: curr_buffer_size += 1

      if statemachine.state > 4:
         if time.time() - last_measured > 0.1:
            success = await update_buffer(data, bmp280, gps)
            if success: curr_buffer_size += 1
            if curr_buffer_size >= buffer_capacity:
                print('saving')
                if should_save:
                    counter += 1
                    await save_and_transmit(rfm9x, data, mode)
                    should_save = counter <= file_writes
                await empty_buffer(data)
            mode = 'a'

      print('State:', statemachine.state)
      await asyncio.sleep(5)


try:
    os.mkdir('/data')
except:
    pass


config_path = '/config.json'
with open(config_path, 'r') as fp:
   data = json.load(fp)

buffer_capacity = data["buffer_capacity"]
delay_pyro_miliseconds = data["deployment_delay_in_miliseconds"]
radio_freq_mhz = data["radio_freq_mhz"]
file_writes = data["file_writes"]

print(f'Read in a delay of {delay_pyro_miliseconds} ms from the config file')

states = statemachine.Statemachine(PYRO_FIRE_DELAY_MS = delay_pyro_miliseconds)

tx, rx = get_uart_pins(data)
scl, sda = get_i2c_pins(data)
sck, miso, mosi = get_spi_pins(data)
lora_cs, lora_rst = get_lora_pins(data)

uart = busio.UART(tx, rx, baudrate=9600, timeout=5)
spi = busio.SPI(sck, mosi, miso)

try:
    i2c = busio.I2C(scl, sda)
    print('hi')
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
    print(bmp280.temperature)
except:
    bmp280 = FakeBMP280()
bmp280.sea_level_pressure = 1013.25

try:
    print('gps')
    gps = adafruit_gps.GPS(uart, debug=True)
except:
    print('no gps')
    gps = FakeGPS()
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")

try:
    rfm9x = adafruit_rfm9x.RFM9x(spi, digitalio.DigitalInOut(lora_cs), digitalio.DigitalInOut(lora_rst), radio_freq_mhz)
    print('lora true')
except:
    rfm9x = FakeRFM9X()
    print('lora false')
#while True:
#    rfm9x.send(bytes("Hello world!\r\n", "utf-8"))
#    time.sleep(5)

buffer = {
   'temperature': [],
   'pressure': [],
   'altitude': [],
   'latitude': [],
   'longitude': [],
   'latitude_degrees': [],
   'longitude_degrees': [],
   'latitude_minutes': [],
   'longitude_minutes': [],
}

#hidde temlate material
external.set_external_led(1)
camera_on = False
apogee_data_save = False
#end of temlate material

init_altitude = bmp280.altitude
last_measured = time.time()


async def main():
   interrupt_task = asyncio.create_task(fire_pyro_backup(states))
   polling_task = asyncio.create_task(poll_sensors(states, bmp280, gps, rfm9x, buffer))

   await asyncio.gather(interrupt_task, polling_task)


asyncio.run(main())
