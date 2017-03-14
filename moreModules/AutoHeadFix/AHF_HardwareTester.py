#! /usr/bin/python3
#-*-coding: utf-8 -*-


import RPi.GPIO as GPIO
from time import sleep
from AHF_TagReader import AHF_TagReader
from AHF_CageSet import AHF_CageSet
from time import time

if __name__ == '__main__':
    def hardwareTester():
        """
        Hardware Tester for Auto Head Fixing, allows you to verify the various hardware bits are working
        """
        cageSet = AHF_CageSet()
        # set up GPIO to use BCM mode for GPIO pin numbering
        GPIO.setwarnings(False)
        GPIO.setmode (GPIO.BCM)
        GPIO.setup (cageSet.pistonsPin, GPIO.OUT)
        GPIO.setup (cageSet.rewardPin, GPIO.OUT)
        GPIO.setup (cageSet.ledPin, GPIO.OUT)
        GPIO.setup (cageSet.tirPin, GPIO.IN)
        GPIO.setup (cageSet.contactPin, GPIO.IN)
        # open TagReader
        try:
            tagReader = AHF_TagReader (cageSet.serialPort, True)
        except IOError:
            tagReader = None
        htloop (cageSet, tagReader)
else:
    def hardwareTester (cageSet, tagReader):
        """
        Hardware Tester for Auto Head Fixing, allows you to verify the various hardware bits are working
        """
        htloop (cageSet, tagReader)

def htloop (cageSet, tagReader):
    """
    Presents a menu asking user to choose a bit of hardware to test, and runs the tests

    If a test fails, a dialog is presented asking user to change the pin setup. The modified pinout
    can be saved, overwriting the configuration in ./AHF_Config.jsn
    Commands are:
    t= tagReader: trys to read a tag and, if successful, monitors Tag in Range Pin until tag goes away
    r = reward solenoid:  Opens the reward solenoid for a 1 second duration, then closes it
    c = contact check:  Monitors the head contact pin until contact, and then while contact is maintained
    p = pistons solenoid: Energizes the pistons for a 2 second duration, and then de-energizes them
    l = LED: Turns on the brain illumination LED for a 2 second duration, then off
    h = sHow config settings: Prints out the current pinout in the AHF_CageSet object
    v = saVe modified config file: Saves the the AHF_CageSet object to the file ./AHF_Config.jsn
    q = quit: quits the program
    """
    try:
        while (True):
            inputStr = input ('t=tagReader, r=reward solenoid, c=contact check, p=pistons solenoid, l=LED, h=sHow config, v= saVe config, q=quit:')
            if inputStr == 't': # t for tagreader
                if tagReader == None:
                    cageSet.serialPort = input ('First, set the tag reader serial port:')
                    try:
                        tagReader = AHF_TagReader (cageSet.serialPort, True)
                        inputStr =  input ('Do you want to read a tag now?')
                        if inputStr[0] == 'n' or inputStr[0] == "N":
                            continue
                    except IOError as anError:
                        print ('Try setting the serial port again.')
                        tagReader = None
                if tagReader is not None:
                    try:
                        if (tagReader.serialPort.inWaiting() < 16):
                            print ('No data in serial buffer')
                            tagError = True
                        else:
                            tagID = tagReader.readTag()
                            tagError = False
                    except (IOError, ValueError) as anError:
                        tagError = True
                    if tagError == True:
                        print ('Serial Port Tag-Read Error\n')
                        tagReader.clearBuffer()
                        inputStr = input ('Do you want to change the tag reader serial port (currently ' + cageSet.serialPort + ')?')
                        if inputStr == 'y' or inputStr == "Y":
                            cageSet.serialPort = input ('Enter New Serial Port:')
                            # remake tagReader and open serial port
                            tagReader = AHF_TagReader (cageSet.serialPort, True)
                    else:
                        print ("Tag ID =", tagID)
                        # now check Tag-In-Range pin function
                        if (GPIO.input (cageSet.tirPin)== GPIO.LOW):
                            print ('Tag was never registered as being "in range"')
                            tagError = True
                        else:
                            startTime = time()
                            GPIO.wait_for_edge (cageSet.tirPin, GPIO.FALLING, timeout= 10000)
                            if (time () > startTime + 10.0):
                                print ('Tag stayed in range for over 10 seconds')
                                tagError = True
                            else:
                                print ('Tag no longer in range')
                                tagError = False
                        if (tagError == True):
                            inputStr = input ('Do you want to change the tag-in-range Pin (currently ' + str (cageSet.tirPin) + ')?')
                            if inputStr[0] == 'y' or inputStr[0] == "Y":
                                cageSet.tirPin = int (input('Enter New tag-in-range Pin:'))
                                GPIO.setup (cageSet.tirPin, GPIO.IN)
            elif inputStr == 'r': # r for reward solenoid
                print ('Reward Solenoid opening for 1 sec')
                GPIO.output(cageSet.rewardPin, 1)
                sleep(1.0)
                GPIO.output(cageSet.rewardPin, 0)
                inputStr= input('Reward Solenoid closed.\nDo you want to change the Reward Solenoid Pin (currently ' + str (cageSet.rewardPin) + ')?')
                if inputStr[0] == 'y' or inputStr[0] == "Y":
                    cageSet.rewardPin = int (input('Enter New Reward Solenoid Pin:' ))
                    GPIO.setup (cageSet.rewardPin, GPIO.OUT, initial=GPO.LOW)
            elif inputStr == 'c': #c for contact on head fix
                if (GPIO.input (cageSet.contactPin)== GPIO.HIGH):
                    print ('Contact pin already high.')
                    err=True
                else:
                    GPIO.wait_for_edge (cageSet.contactPin, GPIO.RISING, timeout= 10000)
                    if (GPIO.input (cageSet.contactPin)== GPIO.LOW):
                        print ('No Contact after 10 seconds.')
                        err = True
                    else:
                        print ('Contact Made.')
                        GPIO.wait_for_edge (cageSet.contactPin, GPIO.FALLING, timeout= 10000)
                        if (GPIO.input (cageSet.contactPin)== GPIO.HIGH):
                            print ('Contact maintained for 10 seconds.')
                            err = True
                        else:
                            print ('Contact Broken')
                            err = False
                if err == True:
                    inputStr= input ('Do you want to change the Head Contact Pin (currently ' + str (cageSet.contactPin) + ')?')
                    if inputStr[0] == 'y' or inputStr[0] == "Y":
                        cageSet.contactPin = int (input('Enter New Head Contact Pin:'))
                        GPIO.setup (cageSet.contactPin, GPIO.IN)
            elif inputStr == 'p': # p for pistons
                print ('Pistons Solenoid energizing for 2 sec')
                GPIO.output(cageSet.pistonsPin, 1)
                sleep (2)
                GPIO.output(cageSet.pistonsPin, 0)
                inputStr=input ('Pistons Solenoid de-energized.\nDo you want to change the Pistons Solenoid Pin (currently ' + str(cageSet.pistonsPin) + ')?')
                if inputStr[0] == 'y' or inputStr[0] == "Y":
                    cageSet.pistonsPin = int (input('Enter New Pistons Solenoid Pin:'))
                    GPIO.setup (cageSet.pistonsPin, GPIO.OUT)
            elif inputStr == 'l': # l for LED trigger
                print ('LED turning ON for 2 seconds.')
                GPIO.output(cageSet.ledPin, 1)
                sleep (2)
                GPIO.output(cageSet.ledPin, 0)
                inputStr=input ('LED turned OFF\nDo you want to change the LED Pin (currently ' + str(cageSet.ledPin) + ')?')
                if inputStr == 'y' or inputStr == "Y":
                    cageSet.ledPin = int (input('Enter New LED Pin:'))
                    GPIO.setup (cageSet.ledPin, GPIO.OUT, initial = GPIO.LOW)
            elif inputStr == 'h':
                cageSet.show()
            elif inputStr=='v':
                cageSet.save()
            elif inputStr == 'q':
                break
    except KeyboardInterrupt:
        print ("quitting.")
    finally:
        if __name__ == '__main__':
            GPIO.cleanup() # this ensures a clean exit

if __name__ == '__main__':
    hardwareTester()
