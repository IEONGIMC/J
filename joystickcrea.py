import machine
import time
import random

# 設定 GPIO 腳位
# LED 腳位
led_a_up = machine.Pin(25, machine.Pin.OUT)    # A燈（向上）
led_b_down = machine.Pin(26, machine.Pin.OUT)  # B燈（向下）
led_c_left = machine.Pin(27, machine.Pin.OUT)  # C燈（向左）
led_d_right = machine.Pin(4, machine.Pin.OUT) # D燈（向右）

# Joystick 腳位 (ADC)
joystick1_x = machine.ADC(machine.Pin(35))  # 玩家1 X軸
joystick1_y = machine.ADC(machine.Pin(32))  # 玩家1 Y軸
joystick2_x = machine.ADC(machine.Pin(34))  # 玩家2 X軸
joystick2_y = machine.ADC(machine.Pin(33))  # 玩家2 Y軸

# 設定 ADC 範圍
joystick1_x.atten(machine.ADC.ATTN_11DB)  # 設定全量程 0-3.3V
joystick1_y.atten(machine.ADC.ATTN_11DB)
joystick2_x.atten(machine.ADC.ATTN_11DB)
joystick2_y.atten(machine.ADC.ATTN_11DB)

buzzer_pin = machine.Pin(15, machine.Pin.OUT)  # 蜂鳴器腳位

# 方向閾值
THRESHOLD_HIGH = 3000  # 高於此值視為推動
THRESHOLD_LOW = 1000   # 低於此值視為推動
CENTER_THRESHOLD = 600  # 中心位置允許的誤差範圍

def reset_lights():
    """關閉所有LED燈"""
    led_a_up.off()
    led_b_down.off()
    led_c_left.off()
    led_d_right.off()

def read_joystick(x_pin, y_pin):
    """讀取 Joystick 狀態並返回方向"""
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
    """檢查 Joystick 是否在中心位置"""
    x_value = x_pin.read()
    y_value = y_pin.read()
    x_center = 2048  # ADC 中心值 (12-bit ADC, 0-4095)
    y_center = 2048
    
    return (abs(x_value - x_center) < CENTER_THRESHOLD and 
            abs(y_value - y_center) < CENTER_THRESHOLD)

def start_game():
    print("準備中...")
    reset_lights()
    wait_time = random.uniform(2, 5)  # 隨機延遲 2 到 5 秒
    time.sleep(wait_time)  
    
    # 再次檢查玩家是否在等待期間移動 Joystick
    if not is_centered(joystick1_x, joystick1_y):
        buzzer_pin.off()  # 開啟蜂鳴器
        print("玩家 1 犯規！在等待期間移動 Joystick")
        time.sleep(1)
        buzzer_pin.on()   # 關閉蜂鳴器
        return
    
    if not is_centered(joystick2_x, joystick2_y):
        buzzer_pin.off()  # 開啟蜂鳴器
        print("玩家 2 犯規！在等待期間移動 Joystick")
        time.sleep(1)
        buzzer_pin.on()   # 關閉蜂鳴器
        return
    
    # 隨機選擇一個方向燈亮起
    direction = random.choice(['up', 'down', 'left', 'right'])
    if direction == 'up':
        led_a_up.on()
    elif direction == 'down':
        led_b_down.on()
    elif direction == 'left':
        led_c_left.on()
    elif direction == 'right':
        led_d_right.on()
    start_time = time.ticks_ms()  # 記錄開始時間

    while True:
        # 檢查玩家1的輸入
        player1_dir = read_joystick(joystick1_x, joystick1_y)
        if player1_dir == direction:
            player = 1
            break
            
        # 檢查玩家2的輸入
        player2_dir = read_joystick(joystick2_x, joystick2_y)
        if player2_dir == direction:
            player = 2
            break
            
        time.sleep(0.01)  # 防止 CPU 過度佔用

    reaction_time = time.ticks_diff(time.ticks_ms(), start_time)  # 計算反應時間
    reset_lights()  # 關閉所有燈
    buzzer_pin.on()  # 關閉蜂鳴器
    print("玩家 {} 反應時間: {} 毫秒".format(player, reaction_time, direction))

# 初始化
reset_lights()
buzzer_pin.on()  # 確保蜂鳴器初始為關閉狀態

while True:
    input("按 Enter 開始遊戲...")
    start_game()