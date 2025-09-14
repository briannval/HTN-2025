import RPi.GPIO as GPIO
import time
from threading import Timer

class Button:
    def __init__(self, pin, click_callback=None, hold_callback=None, hold_time=0.4, bounce_time=20):
        """
        Initialize button with callbacks for click and hold events.
        
        Args:
            pin (int): GPIO pin number (BCM numbering)
            click_callback (function): Function to call on button click
            hold_callback (function): Function to call when button is held
            hold_time (float): Time in seconds to consider as a hold
            bounce_time (int): Debounce time in milliseconds
        """
        self.pin = pin
        self.click_callback = click_callback
        self.hold_callback = hold_callback
        self.hold_time = hold_time
        self.bounce_time = bounce_time
        
        # Button state
        self.pressed_time = None
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Add event detection
        GPIO.add_event_detect(
            self.pin,
            GPIO.BOTH,
            callback=self._button_state_changed,
            bouncetime=self.bounce_time
        )
    
    def _button_state_changed(self, channel):
        GPIO.remove_event_detect(self.pin)
        try:
            if GPIO.input(self.pin) == GPIO.HIGH:
                # Button pressed
                self._button_pressed()
            else:
                # Button released
                self._button_released()
        finally:
            GPIO.add_event_detect(
                self.pin,
                GPIO.BOTH,
                callback=self._button_state_changed,
                bouncetime=self.bounce_time
            )
    
    def _button_pressed(self):
        self.pressed_time = time.time()
    
    def _button_released(self):
        press_duration = time.time() - self.pressed_time
        
        if press_duration < self.hold_time:
            self.click_callback(press_duration)
        else:
            self.hold_callback(press_duration)
        self.pressed_time = None
    
    def cleanup(self):
        """Clean up GPIO resources"""
        GPIO.remove_event_detect(self.pin)
        GPIO.cleanup(self.pin)

# Example usage:
def on_click(press_duration):
    print(f"Button clicked! Press duration: {press_duration:.2f}s")

def on_hold(hold_duration):
    print(f"Button held for {hold_duration:.2f} seconds!")

if __name__ == "__main__":
    button = None
    try:
        # Initialize button on GPIO 25 with callbacks
        button = Button(
            pin=25,
            click_callback=on_click,
            hold_callback=on_hold,
            hold_time=0.4
        )
        
        print("Button test started. Press CTRL+C to exit.")
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if button:
            button.cleanup()