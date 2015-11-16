#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# twisted.words.protocols.irc not ported to python 3 yet m(

#USAGE: ./christian.py #Channel

#twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl

#system imports
import sys,os,random
from datetime import datetime


class HQ():
    #TODO: Should be persistent and set on startup
    isopen = False

class EasterEggs():

    def GetRandomLine(self,filename):

        #Random Selection from Jonathan Kupferman:
        #http://www.regexprn.com/2008/11/read-random-line-in-large-file-in.html
        #Open the file:

        file = open(filename,'r')

        #Get the total file size
        file_size = os.stat(filename)[6]

        #seek to a place in the file which is a random distance away
        #Mod by file size so that it wraps around to the beginning
        file.seek((file.tell()+random.randint(0,file_size-1))%file_size)

        #dont use the first readline since it may fall in the middle of a line
        file.readline()

        #this will return the next (complete) line from the file
        line = file.readline()
        file.close()
        return line


    def GetURL(self,filename):
        file = open(filename,'r')
        url = file.readline()
        file.close()
        return url


    def DarkWing(self,channel,cb):
        filename = "./mylines/darkwing.txt"
        myline = self.GetRandomLine(filename)
        cb.say(channel,myline)

    def Balu(self,channel,cb):
        filename = "./mylines/balu.txt"
        myline = self.GetRandomLine(filename)
        cb.say(channel,myline)

    def Raspel(self,channel,cb):
        #TODO: Read from file
        filename = "./myurls/raspel.url"
        url = self.GetURL(filename)
        cb.say(channel,url)

class ServiceFunctions():

    def Donnerstag(self,channel,cb):
        #TODO: Read from file
        cb.say(channel,"Wir treffen uns immer Donnerstags um 19:00 Uhr in Bockenheim in unserem Hackquarter in der Häuser Gasse 2")

    def Help(self, user, channel, cb):
        if channel[1:] == factory.getChannel():
            helpText = """
Help ahead, my lost sailor!
You'll find the desired information in teh webz:
https://wiki.ccc-ffm.de/
"""
        else:
            helpText = """
I'd like to help you but from where are you talking to me, and why?
You'll find some help right here:
https://wiki.ccc-ffm.de/
"""
        cb.msg(user, helpText, 120)

class KeyFunctions():
    hq = HQ ()

    def __init__(self):
        self.keyholders = []
        #TODO verfiy that file exists
        self.keyfile="./storage/keys.txt"
        with open(self.keyfile, 'r') as keyfile:
            for line in keyfile:
                self.keyholders.append(" ".join(line.split()))

    def ListKeys(self,channel,cb):
        """List current holders of hq keys"""
        print("ListKeys")
        keyMessage = "All the keys are belong to: "
        keyMessage += ", ".join(self.keyholders)
        cb.say(channel,keyMessage)

    def OpenHQ(self,channel,cb):
        """This changes the channel topic"""
        print "Open"
        if self.hq.isopen == False:
            self.hq.isopen = True
            #Get Time:
            time = datetime.now().strftime('%d-%m-%Y %H:%M')
            cb.say(channel,"HQ is open since: " + time)
            #Set Topic
            cb.topic(channel,"HQ is open since: " + time)

    def CloseHQ(self,channel,cb):
        print "Close"
        """This changes the channel topic"""
        if self.hq.isopen == True:
            self.hq.isopen = False
            cb.say(channel, "HQ is closed!")
            cb.topic(channel,"HQ is closed!")
            #Set Topic


    def ChangeKeyholders(self,channel,cb,oldholder,newholder):
        """ Hand one key from an holder to another one """
        if newholder in self.keyholders:
            cb.say(channel, "Noooooo! No more than one key for "+newholder+"!")
            return(False)
        if oldholder in self.keyholders:
            self.keyholders[self.keyholders.index(oldholder)] = newholder
            self.ListKeys(channel,cb)
            with open(self.keyfile, 'w') as keyfile:
                for holder in self.keyholders:
                    print>>keyfile,holder

            return(True)
        else:
            cb.say(channel, oldholder+ " has no key, better luck next time!")
            return(False)

class InternBot(irc.IRCClient):
    nickname = 'dieter'
    channelIntern = "#testgnarplong"

    """Action Objects"""
    key = KeyFunctions()
    eggs = EasterEggs()
    service = ServiceFunctions()

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        print ("connection Established")

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        #TODO Get and Set Keyholders from Channel topic
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""

    def alterCollidedNick(self, nickname):
        return nickname+'_'

    def privmsg(self, user, channel, message):
        """This is called on any message seen in the given channel"""
        nick, _, host = user.partition('!')
        msg = message.split(" ")
        if msg[0] == "!help":
            self.service.Help(nick, channel, self)

        if channel[1:] != factory.getChannel():
            return(False)
        if msg[0] == "!keys":
            if len(msg) == 3:
                self.key.ChangeKeyholders(channel, self, msg[1], msg[2])
            else:
                self.key.ListKeys(channel,self)
        elif msg[0] == "!donnerstag":
            self.service.Donnerstag(channel,self)
        elif msg[0] == "!darkwing":
            self.eggs.DarkWing(channel,self)
        elif msg[0] == "!balu":
            self.eggs.Balu(channel,self)
        elif msg[0] == "!raspel":
            self.eggs.Raspel(channel,self)
        elif msg[0] == "!open":
            self.key.OpenHQ(channel,self)
        elif msg[0] == "!close":
            self.key.CloseHQ(channel,self)

class BotFactory(protocol.ClientFactory):
    """A factory for Bots.
    A new protocol instance will be created each time we connect to the server.
    """

    protocol = InternBot

    def __init__(self, channel):
        self.channel = 'testgnarplong' #channel


    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print ("connection failed: %s", reason)
        reactor.stop()

    def getChannel(self):
        return(self.channel)

if __name__ == '__main__':
    #create intern
    factory = BotFactory(sys.argv[1])
    #create new keys
    keys = KeyFunctions()

    #TODO: Parse from config file
    hostname = 'irc.hackint.org'
    port = 9999
    reactor.connectSSL(hostname, port, factory, ssl.ClientContextFactory())

    #run
    reactor.run()
