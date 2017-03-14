#! /usr/bin/python
#-*-coding: utf-8 -*-

import json
import os
import pwd
import grp


class AHF_CageSet (object):

    """
    Manages settings for hardware GPIO pin-outs and some other cage-specific settings for the raspberry Pi used for Auto Head Fix

    The class AHF_CageSet defines the following settings:
       :cageID: str - whatver name you have for this cage
       :pistonsPin: int - connected to solenoids that drive pistons for head fixing
       :rewardPin: int - connected to solenoid for delivering water reward
       :tirPin: int - tag in-range pin for the ID tag reader
       :contactPin: int - connected to the head contacts
       :ledPin: int - output pin for the Blue LED that illuminates the brain
       :serialPort: str - "/dev/ttyUSB0" for USB with sparkFun breakout or "/dev/ttyAMA0" for built-in
       :dataPath: str - path to base folder, possibly on removable media, where data will be saved in created subfolders

    The settings are saved between program runs in a json-styled text config file, AHFconfig.jsn, in a human readable and editable key=value form.
"""

    def __init__(self):
        """
        Makes a new AHF_CageSet object by loading from AHFconfig.jsn or by querying the user

        Either reads a dictionary from a config file, AHFconfig.jsn, in the same directory in
        which the program is run, or if the file is not found, it querries the user for settings and then writes a new file.

        """
        try:
            with open ('AHFconfig.jsn', 'r') as fp:
                data = fp.read()
                configDict = json.loads(data)
                fp.close()
                self.cageID = configDict.get('Cage ID')
                self.pistonsPin= int(configDict.get('Pistons Pin'))
                self.rewardPin = int(configDict.get('Reward Pin'))
                self.tirPin = int(configDict.get('Tag In Range Pin'))
                self.contactPin = int (configDict.get ('Head Contact Pin'))
                self.ledPin =  int (configDict.get ('LED Pin'))
                self.serialPort = configDict.get ('Serial Port')
                self.dataPath =configDict.get ('Path to Save Data')
        except IOError as e:
            #we will make a file if we didn't find it
            print ('Unable to open base confiuration file, AHFconfig.jsn, let\'s make a new one.\n')
            self.cageID = input('Enter the cage ID:')
            self.pistonsPin = int(input ('Enter the GPIO pin connected to the Head Fixing pistons:'))
            self.rewardPin = int (input ('Enter the GPIO pin connected to the water delivery solenoid:'))
            self.tirPin= int (input ('Enter the GPIO pin connected to the Tag-in-Range pin on the Tag reader:'))
            self.contactPin= int (input ('Enter the GPIO pin connected to the headbar contacts:'))
            self.ledPin = int (input ('Enter the GPIO pin connected to the blue LED for camera illumination:'))
            self.serialPort = input ('Enter serial port for tag reader(likely either /dev/ttyAMA0 or /dev/ttyUSB0):')
            self.dataPath = input ('Enter the path to the directory where the data will be saved:')
            self.show()
            doSave = input ('Enter \'e\' to re-edit the new Cage settings, or any other character to save the new settings to a file.')
            if doSave == 'e' or doSave == 'E':
                self.edit()
            else:
                self.save()
        return


    def save(self):
        """
        Saves current configuration stored in this AHF_CageSet object into the file ./AHFconfig.jsn

        Call this function after modifying the contents of the AHF_CageSet to save your changes

           :param: none
           :returns: nothing
        """
        jsonDict={'Cage ID':self.cageID, 'Pistons Pin':self.pistonsPin, 'Reward Pin' : self.rewardPin}
        jsonDict.update ({'Tag In Range Pin': self.tirPin, 'Head Contact Pin' :  self.contactPin, 'LED Pin' : self.ledPin})
        jsonDict.update ({'Serial Port' : self.serialPort, 'Path to Save Data' : self.dataPath})
        with open ('AHFconfig.jsn', 'w') as fp:
            fp.write (json.dumps (jsonDict))
            fp.close ()
            uid = pwd.getpwnam ('pi').pw_uid
            gid = grp.getgrnam ('pi').gr_gid
            os.chown ('AHFconfig.jsn', uid, gid) # we run as root for GPIO, so we need to expicitly set ownership

    def show (self):
        """
        Prints the current configuration stored in this AHF_CageSet to the console, nicely formatted

           :param: none
           :returns: nothing
        """
        print ('****************Current Auto-Head-Fix Cage Settings********************************')
        print ('1:Cage ID=' + str (self.cageID))
        print ('2:Pistons Solenoid Pin=' +  str (self.pistonsPin))
        print ('3:Reward Solenoid Pin=' + str (self.rewardPin))
        print ('4:Tag-In-Range Pin=' + str (self.tirPin))
        print ('5:Head Bar ContactPin=' + str(self.contactPin))
        print ('6:Brain LED Illumination Pin=' + str(self.ledPin))
        print ('7:Tag Reader serialPort=' + self.serialPort)
        print ('8:dataPath=' + self.dataPath)
        print ('**************************************************************************************')
        

    def edit (self):
        """
        Allows the user to edit and save the cage settings
        """
        while True:
            self.show()
            editNum = int(input ('Enter number of paramater to Edit, or 0 when done to save file:'))
            if editNum == 0:
                break
            elif editNum == 1:
                self.cageID = input('Enter the cage ID:')
            elif editNum == 2:
                self.pistonsPin = int(input ('Enter the GPIO pin connected to the Head Fixing pistons:'))
            elif editNum ==3:
               self.rewardPin = int (input ('Enter the GPIO pin connected to the water delivery solenoid:'))
            elif editNum ==4:
                self.tirPin= int (input ('Enter the GPIO pin connected to the Tag-in-Range pin on the Tag reader:'))
            elif editNum ==5:
                self.contactPin= int (input ('Enter the GPIO pin connected to the headbar contacts:'))
            elif editNum ==6:
                self.ledPin = int (input ('Enter the GPIO pin connected to the blue LED for camera illumination:'))
            elif editNum == 7:
                self.serialPort = input ('Enter serial port for tag reader(likely either /dev/ttyAMA0 or /dev/ttyUSB0):')
            elif editNum == 8:
                self.dataPath = input ('Enter the path to the directory where the data will be saved:')
            else:
                print ('I don\'t recognize that number ' + str (editNum))
        self.show()
        self.save()
        return



## for testing purposes
if __name__ == '__main__':
    hardWare = AHF_CageSet ()
    print ('Cage ID:', hardWare.cageID,'\tPistons Pin:', hardWare.pistonsPin, '\n')
    hardWare.edit()
    hardWare.save()
