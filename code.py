import board
import storage
import external
import time
import measure
import statemachine
import buzzer
import config
import adafruit_gps
import busio
import json


def _get_UART_pins(data):
   pins = data['UART']
   return getattr(board, pins['TX']), getattr(board, pins['RX'])


def _get_I2C_pins(data):
   pins = data['I2C']
   return getattr(board, pins['SCL']), getattr(board, pins['SDA'])


delay_pyro_miliseconds = config.get_deployment_timer()
print(f'Read in a delay of {delay_pyro_miliseconds} ms from the config file')
config_path = '/config.json'

states = statemachine.Statemachine(PYRO_FIRE_DELAY_MS = delay_pyro_miliseconds)
with open(config_path, 'r') as fp:
   data = json.load(fp)

tx, rx = _get_UART_pins(data)
scl, sda = _get_I2C_pins(data)

uart = busio.UART(tx, rx, baudrate=9600, timeout=10)
i2c = busio.I2C(scl, sda)

gps = adafruit_gps.GPS(uart, debug=True)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")
gps_buffer = {
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
   last_print = time.monotonic()
   while True:
      gps.update()
      current = time.monotonic()
      if current - last_print >= 1.0:
         last_print = current
         if not gps.has_fix:
            print("Waiting for fix...")
            continue

         print(
            "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
               gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
               gps.timestamp_utc.tm_mday,  # struct_time object that holds
               gps.timestamp_utc.tm_year,  # the fix time.  Note you might
               gps.timestamp_utc.tm_hour,  # not get all data like year, day,
               gps.timestamp_utc.tm_min,  # month!
               gps.timestamp_utc.tm_sec,
            )
         )

         gps_buffer['latitude'].append(gps.latitude)
         gps_buffer['longitude'].append(gps.longitude)
         gps_buffer['latitude_degrees'].append(gps.latitude_degrees)
         gps_buffer['longitude_degrees'].append(gps.longitude_degrees)
         gps_buffer['latitude_minutes'].append(gps.latitude_minutes)
         gps_buffer['longitude_minutes'].append(gps.longitude_minutes)

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
