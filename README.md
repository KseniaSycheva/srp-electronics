# SRP Electronics Software
### DARE - Small Rocket Project

this is the base code for the system.
make a fork of this repo for your own code!

In essence this code is plug and play for the default SRP case. The only thing that has to be configured is when the pyro will fire, this can be changed in the *config.json*.
By default, there is no code in the statemachine for servos as the use of them varies from rocket to rocket. There is however basecode for them in *external.py*

### Installation

The boards already come with custom firmware preinstalled
This custom firware contains custom pin definitions with useful and recognizable names. 
to see all compatible pins type the following:

```python
>>> import board
>>> dir(board)
['__class__', '__name__', 'A0', 'A1', 'A2', 'ARM_MEAS', 'BUZZER', 'BW', 'CONT_MEAS', 'D0', 'D1', 'D11', 'D6', 'EXT_GPIO', 'I2C', 'LED', 'LED_EXT', 'MISO', 'MOSI', 'NEOPIXEL', 'PYRO_DETONATE', 'RX', 'SCK', 'SCL', 'SDA', 'SERVO', 'SPI', 'STEMMA_I2C', 'TX', 'UART', 'VBAT_MEAS', 'board_id']
```

If, for some reason, the firware is not flashed, do the following

1. Remove all power from the board.
2. Hold the BOOTSEL pin on the feather.
3. Plug the USB into your computer.
4. A drive should show up.
5. Copy the .uf2 file in _firmware/_ to the drive.
6. Once succesfully copied, the drive will auto-eject and startup again.
7. Drag _boot.py_ , _code.py_, _config.json_ and _lib/_ to the drive.
8. Reset the board by either removing the power and inserting it again, or simply presssing the reset button
9. You are all set!

### Editor
To have an interactive runtime with the board. Install the [Mu editor](https://codewith.mu/)
More information can be found on [The circuitpython website](https://circuitpython.org/)
