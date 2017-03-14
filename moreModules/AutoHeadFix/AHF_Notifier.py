import requests


class AHF_Notifier:
    """
    Sends a text message using a web service, textbelt.com

    AHF_Notifier needs requests module, which is not installed by default.
    The best way to install python modules is with pip. Assuming you are using Python 3:
    sudo apt-get install python3-pip
    sudo pip-3.2 install requests
    """

    def __init__(self, cageID_p, phoneList_p):
        """Makes a new AHF_Notifier object

        The notifier will send text messages to a tuple of phone numbers using a web service, textbelt.com
        As it uses http requests to send the message to the web service, you need to be online
        for notifier to work.
        :param cageID_p: identifier for cage, sent in message
        :param durationSecs_p: duration that mouse has been in tube, sent in message
        :param phoneList_p: tuple of telephone numbers to which the message will be sent
        return: nothing
        """
        self.URL = 'http://textbelt.com/canada'
        self.cageID = str(cageID_p)
        self.phoneList = phoneList_p

    def notify(self, tag, durationSecs, isStuck):
        """
        Sends a text message with the given information.

        Two types of message can be sent, depending if isStuck is True or False
        No timing is done by the AHF_Notifier class, the durations are only for building the text mssg
        :param tag: RFID tag of the mouse
        :param durationSecs: how long the mouse has been inside the chamber
        :param isStuck: boolean signifying if the mouse has been inside the chamber for too long, or has just left the chamber
        :return: nothing
        """

        if isStuck == True:
            alertString = 'Mouse ' + str(tag) + ' has been inside the chamber of cage ' + \
                self.cageID + \
                ' for {:.2f}'.format(durationSecs / 60) + ' minutes.'
        else:
            alertString = 'Mouse ' + str(tag) + ', the erstwhile stuck mouse in cage ' + self.cageID + \
                ' has finally left the chamber after being inside for {:.2f}'.format(
                    durationSecs / 60) + ' minutes.'
        for i in self.phoneList:
            requests.post(self.URL, data={'number': i, 'message': alertString})
        print (alertString, ' Messages have been sent.')
