from evdev import InputDevice, categorize, ecodes
import time
import sys
import syslog

import RPi.GPIO as GPIO
ENA = 26
ENB = 0
IN1 = 19
IN2 = 13
time.sleep(2)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

motor_pwm = GPIO.PWM(ENA, 100)
motor_pwm.start(0)
streer_pwm = GPIO.PWM(ENB, 100)
streer_pwm.start(0)


gamepad = None

NEUTRAL = -1
STOP = 0
FORWARD = 1
BACK = 2

RIGHT = 3
LEFT = 4

ECHO_MODE = 5
NORMAL_MODE = 2
SPORT_MODE = 1

current_gear = NEUTRAL
last_gear = NEUTRAL
last_value = 0
mode = ECHO_MODE
def set_motor(direction, value):
    percent = value / 255.0 * 100 / mode
    print('Motor: ', direction , percent)
    if direction == FORWARD:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    elif direction == BACK:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
    elif direction == STOP:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
    motor_pwm.ChangeDutyCycle(percent)

def set_streering(value):
    if value <128:
        print('LEFT ', (128 - value)/128.0 * 100)
    elif value == 128:
        print('CENTER')
    elif value > 128:
        print('RIGHT ', (value -128 +1)/128.0 * 100 )
    streer_pwm.ChangeDutyCycle(value/255.0*100)
def process_event(event):
    global current_gear
    global last_gear
    global last_value
    global mode
    if event.code == 304:
        print('A')
    elif event.code == 305:
        #print('B')
        if event.value == 1:
            last_gear = current_gear
            current_gear = STOP
            set_motor(current_gear, 0)
        elif event.value == 0:
            current_gear = last_gear
            set_motor(current_gear, last_value)
    elif event.code == 307:
        print('X')
    elif event.code == 308:
        print('Y')
    elif event.code == 314:
        if event.value == 1:
            if mode == SPORT_MODE:
                mode = ECHO_MODE
            elif mode == ECHO_MODE:
                mode = NORMAL_MODE
            elif mode == NORMAL_MODE:
                mode = SPORT_MODE
            print('mode : ', mode)
        #print('select')
    elif event.code == 315:
        print('start')
    elif event.code == 316:
        print('mode')
    elif event.code == 310:
        #print('LB')
        if event.value==1:
            current_gear = BACK
    elif event.code == 311:
        #print('RB')
        if event.value==1:
            current_gear = FORWARD
    elif event.code == 317:
        print('L3B')
    elif event.code == 318:
        print('R3B')
    elif event.type == ecodes.EV_ABS and event.code == 17:
        if event.value == -1:
            print('hat-up')
        elif event.value == 1:
            print('hat-down')
        elif event.value == 0:
            print('hat off')
    elif event.type == ecodes.EV_ABS and event.code == 16:
        if event.value == -1:
            print('hat-left')
        elif event.value == 1:
            print('hat-right')
        elif event.value == 0:
            print('hat off')
    elif event.type == ecodes.EV_ABS and event.code == 10:
        print('LT ',(event.value))
    elif event.type == ecodes.EV_ABS and event.code == 9:
        if current_gear == STOP:
            last_value = event.value
        elif current_gear == NEUTRAL:
            pass
        else:
            set_motor(current_gear, event.value)
        #print('RT ',(event.value))
    elif event.type == ecodes.EV_ABS and event.code == 0:
        #print('L3 left-right',(event.value))
        set_streering(event.value)
    elif event.type == ecodes.EV_ABS and event.code == 1:
        print('L3 up-down',(event.value))
    elif event.type == ecodes.EV_ABS and event.code == 2:
        print('R3 left-right',(event.value))
    elif event.type == ecodes.EV_ABS and event.code == 5:
        print('R3 up-down',(event.value))


while(True):
    try:
        if gamepad == None:
            gamepad = InputDevice('/dev/input/event2')
            syslog.syslog(str(gamepad))
            print(gamepad)

        for event in gamepad.read_loop():
                process_event(event)

    except KeyboardInterrupt:
        print('Bye')
        GPIO.cleanup()
        sys.exit()
    except Exception as err:
        syslog.syslog(syslog.LOG_INFO, str(err))
        print(err)
        gamepad = None
        time.sleep(5)
