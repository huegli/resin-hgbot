#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want
import time
import os
import sys
import pygame
import PicoBorgRev
import UltraBorg
import XLoBorg
import lcd_i2c
import compass

# Re-direct our output to standard error, we need to ignore standard out to hide some nasty print statements from pygame
sys.stdout = sys.stderr

# Setup the PicoBorg Reverse
PBR = PicoBorgRev.PicoBorgRev()
#PBR.i2cAddress = 0x44                  # Uncomment and change the value if you have changed the board address
PBR.Init()
if not PBR.foundChip:
    boards = PicoBorgRev.ScanForPicoBorgReverse()
    if len(boards) == 0:
        print 'No PicoBorg Reverse found, check you are attached :)'
    else:
        print 'No PicoBorg Reverse at address %02X, but we did find boards:' % (PBR.i2cAddress)
        for board in boards:
            print '    %02X (%d)' % (board, board)
        print 'If you need to change the I²C address change the setup line so it is correct, e.g.'
        print 'PBR.i2cAddress = 0x%02X' % (boards[0])
    sys.exit()
#PBR.SetEpoIgnore(True)                 # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
# Ensure the communications failsafe has been enabled!
failsafe = False
for i in range(5):
    PBR.SetCommsFailsafe(True)
    failsafe = PBR.GetCommsFailsafe()
    if failsafe:
        break
if not failsafe:
    print 'Board %02X failed to report in failsafe mode!' % (PBR.i2cAddress)
    sys.exit()
PBR.ResetEpo()

# Settings for the joystick
axisUpDown = 1                          # Joystick axis to read for up / down position
axisUpDownInverted = False              # Set this to True if up and down appear to be swapped
axisLeftRight = 0                       # Joystick axis to read for left / right position
axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped
buttonResetEpo = 3                      # Joystick button number to perform an EPO reset (Start)
buttonSlow = 8                          # Joystick button number for driving slowly whilst held (L2)
slowFactor = 0.5                        # Speed to slow to when the drive slowly button is held, e.g. 0.5 would be half speed
buttonFastTurn = 9                      # Joystick button number for turning fast (R2)
interval = 0.10                         # Time between updates in seconds, smaller responds faster but uses more processor time

buttonRight = 7
buttonUp = 6
buttonLeft = 5
buttonDown = 4

pitch = 0.0
pitch_delta = 0.02
direction = 0.0
direction_delta = 0.02

time.sleep(1)
UB = UltraBorg.UltraBorg()
UB.Init()
UB.SetServoPosition1(pitch)
UB.SetServoPosition2(direction)
time.sleep(1)

XLoBorg.Init()
time.sleep(1)

# Initialise display
lcd_i2c.lcd_init()

cp = compass.Compass()
doCalibration = -1
isCalibrated = 0
delayReadCount = 0


# Power settings
voltageIn = 12.0                        # Total battery voltage to the PicoBorg Reverse
voltageOut = 12.0 * 0.95                # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Setup pygame and wait for the joystick to become available
PBR.MotorsOff()
os.environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pygame.init()
#pygame.display.set_mode((1,1))
print 'Waiting for joystick... (press CTRL+C to abort)'
while True:
    try:
        try:
            pygame.joystick.init()
            # Attempt to setup the joystick
            if pygame.joystick.get_count() < 1:
                # No joystick attached, toggle the LED
                PBR.SetLed(not PBR.GetLed())
                pygame.joystick.quit()
                time.sleep(0.5)
            else:
                # We have a joystick, attempt to initialise it!
                joystick = pygame.joystick.Joystick(0)
                break
        except pygame.error:
            # Failed to connect to the joystick, toggle the LED
            PBR.SetLed(not PBR.GetLed())
            pygame.joystick.quit()
            time.sleep(0.5)
    except KeyboardInterrupt:
        # CTRL+C exit, give up
        print '\nUser aborted'
        PBR.SetLed(True)
        sys.exit()
print 'Joystick found'
joystick.init()
PBR.SetLed(False)


try:
    print 'Press CTRL+C to quit'
    driveLeft = 0.0
    driveRight = 0.0
    running = True
    hadEvent = False
    upDown = 0.0
    leftRight = 0.0
    # Loop indefinitely
    while running:
        # Get the latest events from the system
        hadEvent = False
        events = pygame.event.get()
        # Handle each event individually
        for event in events:
            if event.type == pygame.QUIT:
                # User exit
                running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                # A button on the joystick just got pushed down
                hadEvent = True                    
            elif event.type == pygame.JOYAXISMOTION:
                # A joystick has been moved
                hadEvent = True
            if hadEvent:

                # Read axis positions (-1 to +1)
                if axisUpDownInverted:
                    upDown = -joystick.get_axis(axisUpDown)
                else:
                    upDown = joystick.get_axis(axisUpDown)
                if axisLeftRightInverted:
                    leftRight = -joystick.get_axis(axisLeftRight)
                else:
                    leftRight = joystick.get_axis(axisLeftRight)
                # Apply steering speeds
                if not joystick.get_button(buttonFastTurn):
                    leftRight *= 0.5
                # Determine the drive power levels
                driveLeft = -upDown
                driveRight = -upDown
                if leftRight < -0.05:
                    # Turning left
                    driveLeft *= 1.0 + (2.0 * leftRight)
                elif leftRight > 0.05:
                    # Turning right
                    driveRight *= 1.0 - (2.0 * leftRight)
                # Check for button presses
                if joystick.get_button(buttonResetEpo):
                    PBR.ResetEpo()
                if joystick.get_button(buttonSlow):
                    driveLeft *= slowFactor
                    driveRight *= slowFactor

                pitch = joystick.get_axis(3)
                direction = -joystick.get_axis(2)
#                if joystick.get_button(buttonUp):
#                    if pitch < 1.0:
#                        pitch += pitch_delta;
#                if joystick.get_button(buttonDown):
#                    if pitch > -1.0:
#                        pitch -= pitch_delta;
#                if joystick.get_button(buttonLeft):
#                    if direction > -1.0:
#                        direction -= direction_delta;
#                if joystick.get_button(buttonRight):
#                    if direction < 1.0:
#                        direction += direction_delta;
                if joystick.get_button(12):
                    if (doCalibration != 1):
                        lcd_i2c.lcd_string("Calibrating...",lcd_i2c.LCD_LINE_1)
                        lcd_i2c.lcd_string("Drive in circles",lcd_i2c.LCD_LINE_2)
                        time.sleep(2)
                        lcd_i2c.lcd_byte(0x01,lcd_i2c.LCD_CMD) # 000001 Clear display
                        doCalibration = 1
                if joystick.get_button(14):
                    if (doCalibration == 1):
                        lcd_i2c.lcd_string("Calibration",lcd_i2c.LCD_LINE_1)
                        lcd_i2c.lcd_string("stopped",lcd_i2c.LCD_LINE_2)
                        time.sleep(2)
                        lcd_i2c.lcd_byte(0x01,lcd_i2c.LCD_CMD) # 000001 Clear display
                        doCalibration = 0
                        cp.calibrate_compass()
                        print("number of samples: %d" % len(cp.rawX))
                        print("D1 origin: %d, scale %d" % (cp.origin_D1, cp.scale_D1))
                        print("D2 origin: %d, scale %d" % (cp.origin_D2, cp.scale_D2))
                        isCalibrated = 1
#                print("direction:%.2f pitch: %.2f" % (direction, pitch))
                UB.SetServoPosition1(pitch)
                UB.SetServoPosition2(direction)
                #UB.SetServoPosition1(upDown)
                #UB.SetServoPosition2(leftRight)
                # Set the motors to the new speeds
                PBR.SetMotor1(driveRight * maxPower)
                PBR.SetMotor2(-driveLeft * maxPower)
#                print("joystick up/down: %.2f left/right %.2f" % (upDown, leftRight))
        # Change the LED to reflect the status of the EPO latch
        PBR.SetLed(PBR.GetEpo())
        # Wait for the interval period
        time.sleep(interval)

        if (doCalibration == 1):
            mx, my, mz = XLoBorg.ReadCompassRaw()
            cp.push_calibration_value(mx, my, mz)
#            print("Raw data: %d %d %d" % (mx, my, mz))
#            lcd_i2c.lcd_string("calibrating...",lcd_i2c.LCD_LINE_1)
        if (isCalibrated == 1):
            if (delayReadCount < 10):
                delayReadCount += 1
            else:
                mx, my, mz = XLoBorg.ReadCompassRaw()
                heading = cp.get_heading(mx,my,mz)
    #            print("Direction: %d" % heading)
                lcd_i2c.lcd_string("Direction: %d" % heading,lcd_i2c.LCD_LINE_1)
                delayReadCount = 0
    # Disable all drives
    PBR.MotorsOff()
except KeyboardInterrupt:
    # CTRL+C exit, disable all drives
    PBR.MotorsOff()
    UB.SetServoPosition1(0.0)
    UB.SetServoPosition2(0.0)
print
