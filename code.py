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
         #external.PYRO_DETONATE()
      print('Pyro check')
      await asyncio.sleep(1)


async def poll_sensors(statemachine, bmp280, gps, rfm9x, data):
   last_measured = time.time()
   curr_buffer_size = 0
   init_altitude = bmp280.altitude
   timeout = 10

   while True:
      if 1 or statemachine.state == 4:  # state is armed
         # start data collection at 1 input per second
         if time.time() - last_measured > 1:
            success = await update_buffer(buffer, bmp280, gps)
            if success: curr_buffer_size += 1

      elif statemachine.state > 4:
         if time.time() - last_measured > 0.1:
            success = await update_buffer(buffer, bmp280, gps)
            if success: curr_buffer_size += 1
            if success >= buffer_capacity:
               await save_and_transmit(rfm9x, data)

      buzzer.buzzer_tick()
      states.tick()
      print('State:', statemachine.state)
      await save_and_transmit(rfm9x, data)
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
    gps = adafruit_gps.GPS(uart, debug=True)
except:
    gps = FakeGPS()
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")

try:
    rfm9x = adafruit_rfm9x.RFM9x(spi, digitalio.DigitalInOut(lora_cs), digitalio.DigitalInOut(lora_rst), radio_freq_mhz)
    print('lora true')
except:
    rfm9x = FakeRFM9X()
    print('lora false')
rfm9x.send(bytes("Hello world!\r\n", "utf-8"))

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
external.set_external_GPIO(0)
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

# while True:
#    while True:
      # gps.update()
      # if not gps.has_fix:
      #    print("Waiting for fix...")
      #    continue
      #
      # print(
      #    "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
      #       gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
      #       gps.timestamp_utc.tm_mday,  # struct_time object that holds
      #       gps.timestamp_utc.tm_year,  # the fix time.  Note you might
      #       gps.timestamp_utc.tm_hour,  # not get all data like year, day,
      #       gps.timestamp_utc.tm_min,  # month!
      #       gps.timestamp_utc.tm_sec,
      #    )
      # )
      # if len(buffer['temperature']) > data['buffer_capacity']:
      #   for key in buffer.keys():
      #      print(key + ": ", buffer[key])
      #      buffer[key] = []

      #buffer['temperature'].append(bmp280.temperature)
      #buffer['pressure'].append(bmp280.pressure)
      #buffer['altitude'].append(bmp280.altitude)
      # gps_buffer['latitude'].append(gps.latitude)
      # gps_buffer['longitude'].append(gps.longitude)
      # gps_buffer['latitude_degrees'].append(gps.latitude_degrees)
      # gps_buffer['longitude_degrees'].append(gps.longitude_degrees)
      # gps_buffer['latitude_minutes'].append(gps.latitude_minutes)
      # gps_buffer['longitude_minutes'].append(gps.longitude_minutes)

   # if statemachine.state == 4: #state is armed
   #      #start data collection at 1 input per second
   #    if time.time() - last_measured > 1:
   #       update_buffer(buffer, bmp280, gps)

   #if statemachine.State = 5 or statemachine.State = 6: #state is launched or deployed
        #start data collection at 10 inputs per second
        #start sending data using LORA

        #if time_since_launch >= [t_apogee - 3] and apogee_data_save = False:
            #first save on SD Card to prevent corruption
            #apogee_data_save = True

        #if not pyro_deployed and time_since_launch >= [t.apogee - 2 seconds] and time_since_launch <= [2 + t_apogee]:
            #if statemachine.State = 5:
                #Barometer_check_if_time_for_apogee

        #if not pyro_deployed and time_since_launch >= [2 + t_apogee]:
            #deploy pyro

        #if (time_since_launch > [t_apogee] and gps_thinks_we_are_about_to_land:
            #second save on SD card to prevent corruption

        #if time_since_laucnh >= 150:
            #play recovery buzzer song
            #external.set_external_GPIO(0) #turns off the camera
            #camera_on = False


   # buzzer.buzzer_tick()
   # states.tick()
