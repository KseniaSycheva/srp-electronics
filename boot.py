import storage
from measure import get_vbat_voltage

# Remame drive to 'SRP-DARE-FC' 
storage.remount('/', readonly=False)

m = storage.getmount('/')
m.label = 'SRP-DARE-FC'


if get_vbat_voltage() < 3.3:
    storage.remount('/', readonly=True)

storage.enable_usb_drive()
