import time
import buzzer
import external
from measure import is_pyro_inserted, is_bw_inserted, is_armed, get_vbat_voltage

class States():
        SYSTEMS_CHECK = 0
        ERROR_MODE = 1
        IDLE_MODE = 2
        PREPERATION_MODE = 3
        ARMED_MODE = 4
        LAUNCHED_MODE = 5
        DEPLOYED_MODE = 6

class Statemachine:

        def __init__(self, PYRO_FIRE_DELAY_MS=60000):
                self.state = States.SYSTEMS_CHECK
                self.last_in_state_action = round(time.monotonic()*1000)
                self.last_state_transition = round(time.monotonic()*1000)
                self.launched_time =0
                self.do_state_action()
                self.STATE_ACTION_DELAY_MS = 5000
                self.MIN_STATE_DELAY_MS = 500
                self.PYRO_FIRE_DELAY_MS = PYRO_FIRE_DELAY_MS
                self.LAUNCHED = False


        def tick(self):
            if self.last_in_state_action + self.STATE_ACTION_DELAY_MS < round(time.monotonic()*1000):
                self.do_state_action()
                self.last_in_state_action = round(time.monotonic()*1000)
            if self.last_state_transition + self.MIN_STATE_DELAY_MS < round(time.monotonic()*1000):
                self.check_state_transition()

        def check_state_transition(self):
            if self.state == States.SYSTEMS_CHECK:
                if not is_pyro_inserted() or not self._battery_voltage_valid():
                    self.do_state_transition(States.ERROR_MODE)
                elif is_pyro_inserted() and self._battery_voltage_valid():
                    self.do_state_transition(States.IDLE_MODE)

            elif self.state == States.ERROR_MODE:
                if is_pyro_inserted() and not is_armed() and self._battery_voltage_valid():
                    self.do_state_transition(States.IDLE_MODE)

            elif self.state == States.IDLE_MODE:
                if is_armed():
                    self.do_state_transition(States.ERROR_MODE)
                elif is_bw_inserted():
                    self.do_state_transition(States.PREPERATION_MODE)

            elif self.state == States.PREPERATION_MODE:
                if is_armed() and not is_pyro_inserted():
                    self.do_state_transition(States.ERROR_MODE)
                elif is_armed() and is_pyro_inserted():
                    self.do_state_transition(States.ARMED_MODE)
                elif not is_bw_inserted():
                    self.do_state_transition(States.IDLE_MODE)

            elif self.state == States.ARMED_MODE:
                if not is_armed():
                    self.do_state_transition(States.PREPERATION_MODE)
                elif not is_bw_inserted():
                    self.do_state_transition(States.LAUNCHED_MODE)


            elif self.state == States.LAUNCHED_MODE:
                if self.check_if_pyro_should_be_fired():
                    self.do_state_transition(States.DEPLOYED_MODE)

            elif self.state == States.DEPLOYED_MODE:
                pass


        def do_state_action(self):
            if self.state == States.SYSTEMS_CHECK:
                external.neopixel_disable()
            elif self.state == States.ERROR_MODE:
                self._queue_long_beep()
                external.neopixel_set_rgb(255,0,0)
            elif self.state == States.IDLE_MODE:
                external.neopixel_set_rgb(0,0,255)
            elif self.state == States.PREPERATION_MODE:
                external.neopixel_set_rgb(255,255,0)
            elif self.state == States.ARMED_MODE:
                external.neopixel_set_rgb(255,100,0)
            elif self.state == States.LAUNCHED_MODE:
                self._queue_short_beep()
                external.neopixel_set_rgb(0,255,0)
            elif self.state == States.DEPLOYED_MODE:
                self._queue_long_beep()
                external.neopixel_set_rgb(255,30,70)
                external.PYRO_DETONATE()

        def do_state_transition(self, to_state):
            state_trans_has_happened = False

            if self.state == States.SYSTEMS_CHECK:
                if to_state == States.ERROR_MODE:
                    self.state = States.ERROR_MODE
                    state_trans_has_happened = True
                elif to_state == States.IDLE_MODE:
                    self.state = States.IDLE_MODE
                    self._queue_short_beep()
                    state_trans_has_happened = True

            elif self.state == States.IDLE_MODE:
                if to_state == States.PREPERATION_MODE:
                    self.state = States.PREPERATION_MODE
                    self._queue_short_beep()
                    state_trans_has_happened = True
                elif to_state == States.ERROR_MODE:
                    self.state = States.ERROR_MODE
                    state_trans_has_happened = True

            elif self.state == States.PREPERATION_MODE:
                if to_state == States.ARMED_MODE:
                    self.state = States.ARMED_MODE
                    self._queue_short_beep()
                    state_trans_has_happened = True
                elif to_state == States.IDLE_MODE:
                    self.state = States.IDLE_MODE
                    self._queue_long_beep()
                    state_trans_has_happened = True
                elif to_state == States.ERROR_MODE:
                    self.state = States.ERROR_MODE
                    state_trans_has_happened = True

            elif self.state == States.ARMED_MODE:
                if to_state == States.PREPERATION_MODE:
                    self.state = States.PREPERATION_MODE
                    self._queue_long_beep()
                    state_trans_has_happened = True
                elif to_state == States.LAUNCHED_MODE:
                    self.state = States.LAUNCHED_MODE
                    self.LAUNCHED = True
                    self.set_launched_time()
                    state_trans_has_happened = True

            elif self.state == States.LAUNCHED_MODE:
                if to_state == States.DEPLOYED_MODE:
                    self.state = States.DEPLOYED_MODE
                    state_trans_has_happened = True

            elif self.state == States.ERROR_MODE:
                if to_state == States.IDLE_MODE:
                    self.state = States.IDLE_MODE
                    # self._queue_short_beep()
                    state_trans_has_happened = True

            if state_trans_has_happened:
                for _ in range(self.state):
                    self._queue_short_beep()
                self.do_state_action()
                self._reset_state_timer()

        def check_if_pyro_should_be_fired(self):
            if self.state != States.LAUNCHED_MODE: # Not in launching state of the statediagram
                return False
            if self.LAUNCHED == False: # Has not launched yet
                return False
            if self.launched_time == 0: # The launchtimer has not been set yet
                return False
            if self.launched_time + self.PYRO_FIRE_DELAY_MS < round(time.monotonic()*1000): # The amount of time has passed
                return True
            else:
                return False

        def set_launched_time(self):
            if self.LAUNCHED == True:
                self.launched_time = round(time.monotonic()*1000)

        def _reset_state_timer(self):
            self.last_state_transition = round(time.monotonic()*1000)

        def _queue_short_beep(self):
            buzzer.append_buzzer_note(2000, 100)
            buzzer.append_buzzer_wait(100)
            buzzer.append_buzzer_note(2000, 100)
            buzzer.append_buzzer_wait(100)

        def _queue_long_beep(self):
            buzzer.append_buzzer_note(2000, 1000)
            buzzer.append_buzzer_wait(1000)

        def _battery_voltage_valid(self): # Todo: Make it depend on the battery configuration
            if get_vbat_voltage() > 3.0:
                return True
            else:
                return False
