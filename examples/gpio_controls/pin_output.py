from RPi import GPIO


class PinOutput (object):
    pin = None
    control = None    

    def __init__(self, pin, logic='high', default=False):
        # GPIO mode: use the GPIOn number
        GPIO.setmode(GPIO.BCM)
        # Set GPIO PIN
        assert type(pin) is int
        self.pin = pin          
        
        # Set control logic
        if logic == 'high':
            self.control = {False: GPIO.LOW, True: GPIO.HIGH}
        elif logic == 'low':
            self.control = {False: GPIO.HIGH, True: GPIO.LOW}
            
        # Set GPIO PIN as output
        GPIO.setup(self.pin, GPIO.OUT, initial=self.control[default])
   
    def read_state(self):
        # Read PIN level    
        level = GPIO.input(self.pin)
        return self.control.keys()[self.control.values().index(level)]
 
    def write_state(self, state):    
        GPIO.output(self.pin, self.control[state])
    
    def close(self):
        GPIO.cleanup()
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        GPIO.cleanup()
        
    def __str__(self):
        state = self.read_state()        
        return '%s' % ('ON' if state else 'OFF')

    def __repr__(self):        
        return '<GPIO%d %s>' % (self.pin, self)


