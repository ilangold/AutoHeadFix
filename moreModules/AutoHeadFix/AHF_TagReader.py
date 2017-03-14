#! /usr/bin/python
#-*-coding: utf-8 -*-

import serial


class AHF_TagReader:
    """
    Class to read values from a Innovations RFID tag reader, such as ID-20LA
    """

    def __init__(self, serialPort, doChecksum=False):
        """
        Makes a new AHF_TagReader object
        :param serialPort: serial port tag reader is attached to, /dev/ttyUSB0 or /dev/ttyAMA0 for instance
        :param doCheckSum: set to calculate the checksum on each tag read
        """
        # initialize serial port
        self.serialPort = None
        try:
            self.serialPort = serial.Serial(str(serialPort), baudrate=9600)
        except IOError as anError:
            print ("Error initializing TagReader serial port.." + str(anError))
            raise anError
        if (self.serialPort.isOpen() == False):
            self.serialPort.open()
        self.serialPort.flushInput()
        # set boolean for doing checksum on each read
        self.doCheckSum = bool(doChecksum)

    def clearBuffer(self):
        """
        Clears the serial buffer for the serialport used by the tagReader
        """
        self.serialPort.flushInput()

    def readTag(self):
        """
        Reads a hexidecimal RFID tag from the serial port using a blocking read and returns the decimal equivalent

        RFID Tag is 16 characters: STX(02h) DATA (10 ASCII) CHECK SUM (2 ASCII) CR LF ETX(03h)
        1 char of junk, 10 of hexadecimal data, 2 of hexadecimal check sum, 3 of junk

        :returns decimal value of RFID tag
        :raises IOError: if serialPort not read
        raises ValueError: if checksum or conversion from hex to decimal fails

        """
        serialJunk = self.serialPort.read(1)
        serialTag = self.serialPort.read(10)
        serialCheckSum = self.serialPort.read(2)
        serialJunk = self.serialPort.read(3)
        if serialJunk.__len__() < 3:
            self.serialPort.flushInput()
            raise IOError
        try:
            decVal = int(serialTag, 16)
        except ValueError as anError:
            print ("TagReader Error converting tag to integer: " +
                   str(serialTag) + ': ' + str(anError))
            self.serialPort.flushInput()
            raise ValueError
        else:
            if self.doCheckSum == True:
                if self.checkSum(serialTag, serialCheckSum) == True:
                    return decVal
                else:
                    print ("TagReader checksum error: " +
                           str(serialTag) + ': ' + str(serialCheckSum))
                    self.serialPort.flushInput()
                    raise ValueError
            else:
                return decVal

    def checkSum(self, tag, checkSum):
        """
           Sequentially XOR-ing 2 byte chunks of the 10 byte tag value will give the 2-byte check sum

           :param tag: the 10 bytes of tag value
           :param checksum: the two butes of checksum value
           :returns: True if check sum calculated correctly, else False
        """
        checkedVal = 0
        try:
            for i in range(0, 5):
                checkedVal = checkedVal ^ int(tag[(2 * i): (2 * (i + 1))], 16)
            if checkedVal == int(checkSum, 16):
                return True
            else:
                return False
        except Exception:
            return False

    def __del__(self):
        if self.serialPort is not None:
            self.serialPort.close()


if __name__ == '__main__':

    serialPort = '/dev/ttyUSB0'
    doCheckSum = True
    nReads = 3
    try:
        tagReader = AHF_TagReader(serialPort, doCheckSum)
        for i in range(0, nReads):
            print (tagReader.readTag())
        print ('Read ' + str(nReads) + ' tags')
    except Exception:
        print ('Tag reader not found, check port ' + serialPort)
