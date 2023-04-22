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

   buzzer.buzzer_tick()
   states.tick()
