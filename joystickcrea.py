import machine
import time
import random
from machine import Pin, I2C
import ssd1306

# GPIO pin setup
# LED pins
led_a_up = machine.Pin(25, machine.Pin.OUT)    # A LED (up)
led_b_down = machine.Pin(26, machine.Pin.OUT)  # B LED (down)
led_c_left = machine.Pin(27, machine.Pin.OUT)  # C LED (left)
led_d_right = machine.Pin(4, machine.Pin.OUT)  # D LED (right)

# Joystick pins (ADC)
joystick1_x = machine.ADC(machine.Pin(35))  # Player1 X-axis
joystick1_y = machine.ADC(machine.Pin(32))  # Player1 Y-axis
joystick2_x = machine.ADC(machine.Pin(34))  # Player2 X-axis
joystick2_y = machine.ADC(machine.Pin(33))  # Player2 Y-axis

# ADC range setup
joystick1_x.atten(machine.ADC.ATTN_11DB)  # Full range 0-3.3V
joystick1_y.atten(machine.ADC.ATTN_11DB)
joystick2_x.atten(machine.ADC.ATTN_11DB)
joystick2_y.atten(machine.ADC.ATTN_11DB)

buzzer_pin = machine.Pin(15, machine.Pin.OUT)  # Buzzer pin

# Initialize OLED (using GPIO 13 and 14 as I2C pins)
i2c = I2C(scl=Pin(14), sda=Pin(13))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Direction thresholds
THRESHOLD_HIGH = 3000  # Above this = pushed
THRESHOLD_LOW = 1000   # Below this = pushed
CENTER_THRESHOLD = 600  # Center position tolerance

def reset_lights():
    """Turn off all LEDs"""
    led_a_up.off()
    led_b_down.off()
    led_c_left.off()
    led_d_right.off()

def read_joystick(x_pin, y_pin):
    """Read joystick and return direction"""
    x_value = x_pin.read()
    y_value = y_pin.read()
    
    if y_value < THRESHOLD_LOW:
        return 'up'
    elif y_value > THRESHOLD_HIGH:
        return 'down'
    elif x_value < THRESHOLD_LOW:
        return 'left'
    elif x_value > THRESHOLD_HIGH:
        return 'right'
    else:
        return 'neutral'

def is_centered(x_pin, y_pin):
    """Check if joystick is centered"""
    x_value = x_pin.read()
    y_value = y_pin.read()
    x_center = 2048  # ADC center value (12-bit ADC, 0-4095)
    y_center = 2048
    
    return (abs(x_value - x_center) < CENTER_THRESHOLD and 
            abs(y_value - y_center) < CENTER_THRESHOLD)

def display_message(line1, line2="", line3="", line4=""):
    """Show message on OLED"""
    oled.fill(0)
    oled.text(line1, 0, 0)
    oled.text(line2, 0, 16)
    oled.text(line3, 0, 32)
    oled.text(line4, 0, 48)
    oled.show()

def start_game():
    display_message("Preparing...", "Please wait")
    reset_lights()
    wait_time = random.uniform(2, 5)  # Random delay 2-5 sec
    time.sleep(wait_time)  
    
    # Check if players moved during wait
    if not is_centered(joystick1_x, joystick1_y):
        buzzer_pin.off()  # Turn on buzzer
        display_message("Player1 foul!", "Moved early")
        time.sleep(1)
        buzzer_pin.on()   # Turn off buzzer
        return
    
    if not is_centered(joystick2_x, joystick2_y):
        buzzer_pin.off()  # Turn on buzzer
        display_message("Player2 foul!", "Moved early")
        time.sleep(1)
        buzzer_pin.on()   # Turn off buzzer
        return
    
    # Randomly select a direction
    direction = random.choice(['up', 'down', 'left', 'right'])
    direction_text = {'up': 'UP', 'down': 'DOWN', 'left': 'LEFT', 'right': 'RIGHT'}[direction]
    
    if direction == 'up':
        led_a_up.on()
    elif direction == 'down':
        led_b_down.on()
    elif direction == 'left':
        led_c_left.on()
    elif direction == 'right':
        led_d_right.on()
        
    display_message("Direction:","React fast!")
    start_time = time.ticks_ms()  # Record start time

    while True:
        # Check player1 input
        player1_dir = read_joystick(joystick1_x, joystick1_y)
        if player1_dir == direction:
            player = 1
            break
            
        # Check player2 input
        player2_dir = read_joystick(joystick2_x, joystick2_y)
        if player2_dir == direction:
            player = 2
            break
            
        time.sleep(0.01)  # Prevent CPU overload

    reaction_time = time.ticks_diff(time.ticks_ms(), start_time)  # Calculate reaction time
    reset_lights()  # Turn off all LEDs
    buzzer_pin.on()  # Turn off buzzer
    
    # Show result on OLED
    display_message(f"Player {player} wins!", 
                   f"Reaction time:", 
                   f"{reaction_time} ms", 
                   "Press to restart")

# Initialization
reset_lights()
buzzer_pin.on()  # Ensure buzzer is off initially
display_message("Reaction Game", "Ready to start", "Press to begin", "1 vs 2")

while True:
    # Wait for any button press
    input("Press Enter to start...")  # In MicroPython, replace with actual button detection
    start_game()
