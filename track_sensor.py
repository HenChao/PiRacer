import time
import RPi.GPIO as GPIO

# 3     - Left Pre-stage    - LPS
# 5     - Left Stage        - LS
# 7     - Left Red Light    - LRL
# 11    - Left 60ft Line    - L60
# 12    - Left Finish Line  - LFL
# 13    - Right Pre-stage   - RPS
# 15    - Right Stage       - RS
# 16    - Right Red Light   - RRL
# 18    - Right 60ft Line   - R60
# 22    - Right Finish Line - RFL
# 23    - Left Lights Pre-Stage - LLPS
# 24    - Left Lights Stage - LLS
# 26    - Left Lights Red - LLR
# 29    - Right Lights Pre-Stage - RLPS
# 31    - Right Lights Stage - RLS
# 32    - Right Lights Red - RLR
# 33    - Amber Lights 1   - AL1
# 35    - Amber Lights 2   - AL2
# 36    - Amber Lights 3   - AL3
# 37    - Green Light - GL

LPS = 3
LS = 5
LRL = 7
L60 = 11
LFL = 12
RPS = 13
RS = 15
RRL = 16
R60 = 18
RFL = 22
LLPS = 23
LLS = 24
LLR = 26
RLPS = 29
RLS = 31
RLR = 32
AL1 = 33
AL2 = 35
AL3 = 36
GL = 37

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LPS, GPIO.IN)
GPIO.setup(LS, GPIO.IN)
GPIO.setup(LRL, GPIO.IN)
GPIO.setup(L60, GPIO.IN)
GPIO.setup(LFL, GPIO.IN)
GPIO.setup(RPS, GPIO.IN)
GPIO.setup(RS, GPIO.IN)
GPIO.setup(RRL, GPIO.IN)
GPIO.setup(R60, GPIO.IN)
GPIO.setup(RFL, GPIO.IN)
GPIO.setup(LLPS, GPIO.OUT)
GPIO.setup(LLS, GPIO.OUT)
GPIO.setup(LLR, GPIO.OUT)
GPIO.setup(RLPS, GPIO.OUT)
GPIO.setup(RLS, GPIO.OUT)
GPIO.setup(RLR, GPIO.OUT)
GPIO.setup(AL1, GPIO.OUT)
GPIO.setup(AL2, GPIO.OUT)
GPIO.setup(AL3, GPIO.OUT)
GPIO.setup(GL, GPIO.OUT)

# Stage values
# 0 - initial
# 1 - at pre-stage
# 2 - at stage, ready to start
# 3 - racing
# 4 - completed
LSTATE = 0
RSTATE = 0

START_TIME = 0
L_60_TIME = 0
R_60_TIME = 0
L_FINISH_TIME = 0
R_FINISH_TIME = 0

def all_lights_on():
    GPIO.output(LLPS, GPIO.HIGH)
    GPIO.output(LLS, GPIO.HIGH)
    GPIO.output(LLR, GPIO.HIGH)
    GPIO.output(RLPS, GPIO.HIGH)
    GPIO.output(RLS, GPIO.HIGH)
    GPIO.output(RLR, GPIO.HIGH)
    GPIO.output(AL1, GPIO.HIGH)
    GPIO.output(AL2, GPIO.HIGH)
    GPIO.output(AL3, GPIO.HIGH)
    GPIO.output(GL, GPIO.HIGH)

def all_lights_off():
    GPIO.output(LLPS, GPIO.LOW)
    GPIO.output(LLS, GPIO.LOW)
    GPIO.output(LLR, GPIO.LOW)
    GPIO.output(RLPS, GPIO.LOW)
    GPIO.output(RLS, GPIO.LOW)
    GPIO.output(RLR, GPIO.LOW)
    GPIO.output(AL1, GPIO.LOW)
    GPIO.output(AL2, GPIO.LOW)
    GPIO.output(AL3, GPIO.LOW)
    GPIO.output(GL, GPIO.LOW)

def initialize():
    for i in range(3):
        all_lights_off()
        time.sleep(1)
        all_lights_on()
        time.sleep(1)
    reset()

def reset():
    global LSTATE, RSTATE
    LSTATE = 0
    RSTATE = 0
    all_lights_off()

def set_event(channel, edge, function):
    # Set bouncetime value to prevent switch bounce (in ms)
    GPIO.add_event_detect(channel, edge, callback=function, bouncetime=200)

def prestage(channel):
    global LSTATE, RSTATE
    if (channel == LPS) and (LSTATE == 0):
        GPIO.output(LLPS, GPIO.HIGH)
        LSTATE = 1
    elif (channel == RPS) and (RSTATE == 0):
        GPIO.output(RLPS, GPIO.HIGH)
        RSTATE = 1

set_event(LPS, GPIO.FALLING, prestage)
set_event(RPS, GPIO.FALLING, prestage)

def staged(channel):
    global LSTATE, RSTATE
    if (channel == LS) and (GPIO.input(LS) == 0) and (GPIO.input(LRL) == 1) and (LSTATE == 1):
        GPIO.output(LLS, GPIO.HIGH)
        LSTATE = 2
    elif (channel == RS) and (GPIO.input(RS) == 0) and (GPIO.input(RRL) == 1) and (RSTATE == 1):
        GPIO.output(RLS, GPIO.HIGH)
        RSTATE = 2

set_event(LS, GPIO.FALLING, staged)
set_event(RS, GPIO.FALLING, staged)

def cross_60(channel):
    global L_60_TIME, R_60_TIME, START_TIME
    if (channel == L60):
        L_60_TIME = time.time() - START_TIME
    elif (channel == R60):
        R_60_TIME = time.time() - START_TIME

set_event(L60, GPIO.FALLING, cross_60)
set_event(R60, GPIO.FALLING, cross_60)

def cross_finish(channel):
    global L_FINISH_TIME, R_FINISH_TIME, START_TIME, LSTATE, RSTATE
    if (channel == LFL):
        L_FINISH_TIME = time.time() - START_TIME
        LSTATE = 4
    elif (channel == RFL):
        R_FINISH_TIME = time.time() - START_TIME
        RSTATE = 4

def main_loop():
    global START_TIME, LSTATE, RSTATE, L_FINISH_TIME, R_FINISH_TIME
    if (LSTATE == 2) and (RSTATE == 2):
        time.sleep(2)
        GPIO.output(AL1, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(AL2, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(AL3, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(GL, GPIO.HIGH)
        START_TIME = time.time()
        LSTATE = 3
        RSTATE = 3
    elif (LSTATE == 4):
        print("Left finish time: %s (s)" % L_FINISH_TIME)
    elif (RSTATE == 4):
        print("Right finish time: %s (s)" % R_FINISH_TIME)

try:
    initialize()
    while 1:
        main_loop()
finally:
    GPIO.cleanup()
