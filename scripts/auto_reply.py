#!/usr/bin/env python
###############################################################################
# AUTO SMS REPLY
# Using SL4A allows a user to specify a phone number to which a pre determined
# message will be sent in reply to any received message.
# Copyright (C) 2012  Alan Barr  
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This code was inspired by:
#   BLOWFISH SMS - https://github.com/s7ephen/Blowfish-SMS
#   A blowfish encrypted SMS client for Android Phones.
#   August 2010
#   stephen@sa7ori.org
#
#   This module is open source; you can redistribute it and/or
#   modify it under the terms of the GPL or Artistic License.
#   These licenses are available at http://www.opensource.org
#
#   This software must be used and distributed in accordance
#   with the law. The author claims no liability for its
#   misuse.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
###############################################################################

__author__ = "Alan Barr, Stephen A. Ridley <stephen@sa7ori.org>"

import android
import time
import sys

def logSentSms(smsMessage, reply_message):
    sentTimeString     = time.strftime("%d.%m.%y %H:%M:%S", time.localtime())
    receivedTime = float(smsMessage["date"]) / 1000
    receivedTimeString = time.strftime("%d.%m.%y %H:%M:%S",
                                       time.localtime(receivedTime))

    logString = "Replied to:" + "\n" + "%s" %smsMessage["address"] + "\n" + \
                "Message Text:" + "\n" + "%s" %smsMessage["body"]  + "\n" + \
                "Received On:" + "\n" + "%s" %receivedTimeString   + "\n" + \
                "With:" + "\n" + "%s" %reply_message               + "\n" + \
                "At:" + "\n" + "%s" %sentTimeString                + "\n"

    log = open("/sdcard/.autoReply.log", "a")
    log.write("####################\n")
    log.write(logString)
    log.write("####################\n\n")
    log.close()

def poll_sms_inbox(contact_number, reply_message, droid):
    replied = False
    messages_resp = droid.smsGetMessages(True).result
    ids_to_mark_read = []
    if messages_resp != None:
        if len(messages_resp) > 0:
            for m in messages_resp:
                print m
                sms_number = m["address"]
                sms_number = sms_number.strip()
                sms_number = sms_number.replace("-","")
                sms_number = sms_number.replace(".","")
                if contact_number in sms_number:
                    droid.smsSend(sms_number, reply_message)
                    ids_to_mark_read.append(int(m["_id"]))
                    print "Sent: %s to %s" %(reply_message, sms_number)
                    logSentSms(m, reply_message)
                    replied = True
                    break
            droid.smsMarkMessageRead(ids_to_mark_read, True)
        else:
            pass
    return replied


def getContactLocation(options):
    droid.dialogCreateAlert("Get contact number from:")
    droid.dialogSetItems(options)
    droid.dialogSetNegativeButtonText("Cancel")
    droid.dialogShow()
    return droid.dialogGetResponse().result


def getContactNumber():
    options=["Contacts","Manual"]

    result = getContactLocation(options)

    if result.has_key("item"):
        choice = result["item"]
    else:
        sys.exit()

    if choice == 0:
        contact = droid.pickPhone().result
        contact = contact.replace("-","")
        contact = contact.replace(".","")
        contact = contact.strip()
    elif choice == 1:
        contact = droid.dialogGetInput("Contact:",
                                       "Please enter contact's number:").result
        contact = contact.replace("-","")
        contact = contact.replace(".","")
        contact = contact.strip()
    else:
        sys.exit()
    
    if len(contact) < 9:
        sys.exit()

    contact = contact[-10:]
    return contact


if __name__ == "__main__":
    droid = android.Android()
    contact = getContactNumber()
    reply_message = droid.dialogGetInput("Auto Reply Message:").result
    reply_message.strip()
    
    while 1:
        if poll_sms_inbox(contact, reply_message, droid):
            droid.dialogCreateAlert("Message Transmitted")
            droid.dialogSetNeutralButtonText("Exit")
            droid.dialogShow()
            sys.exit()
        time.sleep(5)

