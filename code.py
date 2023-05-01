import board
import storage
import external
import time
import digitalio
import statemachine
import buzzer
import config
import adafruit_bmp280
import adafruit_gps
import adafruit_sdcard
import busio
import json
from utils import *


delay_pyro_miliseconds = config.get_deployment_timer()
print(f'Read in a delay of {delay_pyro_miliseconds} ms from the config file')
config_path = '/config.json'

states = statemachine.Statemachine(PYRO_FIRE_DELAY_MS = delay_pyro_miliseconds)
with open(config_path, 'r') as fp:
   data = json.load(fp)

tx, rx = get_uart_pins(data)
scl, sda = get_i2c_pins(data)
sck, miso, mosi = get_spi_pins(data)

sensor_poll_freq = 0.5

#uart = busio.UART(tx, rx, baudrate=9600, timeout=10)
i2c = busio.I2C(scl, sda)
spi = busio.SPI(sck, mosi, miso)

bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, 0x76)
bmp280.sea_level_pressure = 1013.25

# gps = adafruit_gps.GPS(uart, debug=True)
# gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
# gps.send_command(b"PMTK220,1000")

# sdcard = adafruit_sdcard.SDCard(
#     board.SPI(),
#     digitalio.DigitalInOut(sck),
# )
# vfs = storage.VfsFat(sdcard)
# storage.mount(vfs, "/sd")

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

while True:
   while True:
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
      if len(buffer['temperature']) > data['buffer_capacity']:
         for key in buffer.keys():
            print(key + ": ", buffer[key])
            buffer[key] = []

      buffer['temperature'].append(bmp280.temperature)
      buffer['pressure'].append(bmp280.pressure)
      buffer['altitude'].append(bmp280.altitude)
      # gps_buffer['latitude'].append(gps.latitude)
      # gps_buffer['longitude'].append(gps.longitude)
      # gps_buffer['latitude_degrees'].append(gps.latitude_degrees)
      # gps_buffer['longitude_degrees'].append(gps.longitude_degrees)
      # gps_buffer['latitude_minutes'].append(gps.latitude_minutes)
      # gps_buffer['longitude_minutes'].append(gps.longitude_minutes)

   #if statemachine.State = 4: #state is armed
        #start data collection at 1 input per second
        #if not camera_on:
            #external.set_external_GPIO(1) #turns the camera on

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

   
   buzzer.buzzer_tick()
   states.tick()
   time.sleep(1 / sensor_poll_freq)
