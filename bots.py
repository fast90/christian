#twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl

#Import bot modules
from hq import HQ
from eggs import EasterEggs
from service import ServiceFunctions
from keys import KeyFunctions

class InternBot(irc.IRCClient):
    nickname = 'foo'
    channelIntern = "#testgnarplong"

    """Action Objects"""
    key = KeyFunctions()
    eggs = EasterEggs()
    service = ServiceFunctions()
    hq = HQ()

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        print ("connection Established")

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        # set topic on join
        self.say(channel, "Hello my friends! I'm back!")
        if self.hq.isopen == "open":
            self.topic(channel, "HQ is open since " + self.hq.statusSince)
        elif self.hq.isopen == "private":
            self.topic(channel, "HQ is open for members only since " + self.hq.statusSince)
        elif self.hq.isopen == "closed":
            self.topic(channel, "HQ is closed")
        else:
            # if proper status is unknown ask for it
            self.say(channel, "I don't know the current status of the HQ. Please double-check the status and set it to the proper value!")


    def alterCollidedNick(self, nickname):
        return nickname+'_'

    def getUsers(self, message, nick):
        msg = message.split()
        if len(msg) == 1:
            users = [nick]
        else:
            users = msg[1:]
        return(users)

    def privmsg(self, user, channel, message):
        """This is called on any message seen in the given channel"""
        nick, _, host = user.partition('!')
        #do nothing if first sign is something else than a !
        if message[0] != "!":
            return(False)

        ## replace nick aliases by the actual nickname
        aliases = {}
        with open("./config/aliases", "r") as fileA:
            for line in fileA:
                alias = line.split(":")
                aliases[alias[0]] = alias[1].strip().encode()
        for alias, nickname in aliases.items():
            message = re.sub(alias, nickname, message)
        msg = message.split(" ")

        if msg[0] == "!help":
            self.service.Help(nick, channel, self)

        if channel[1:] != factory.getChannel():
            return(False)
        if msg[0] == "!keys":
            if len(msg) == 3:
                self.key.ChangeKeyholders(channel, self, msg[1], msg[2])
            else:
                self.key.ListKeys(channel,nick,self)
        elif msg[0] == "!donnerstag":
            self.service.Donnerstag(channel,self)
        elif msg[0] == "!darkwing":
            self.eggs.DarkWing(channel,self)
        elif msg[0] == "!balu":
            self.eggs.Balu(channel,self)
        elif msg[0] == "!raspel":
            self.eggs.Raspel(channel,self)
        elif msg[0] == "!open":
            self.hq.OpenHQ(channel,self)
        elif msg[0] == "!private":
            self.hq.PrivateHQ(channel, self)
        elif msg[0] == "!close":
            self.hq.CloseHQ(channel,self)
        elif msg[0] == "!join":
            users = self.getUsers(message, nick)
            self.hq.Join(channel,self, self.getUsers(message, nick))
            if self.hq.isopen == "closed":
                self.hq.OpenHQ(channel, self)
        elif msg[0] == "!leave" or msg[0] == "!part":
            users = self.getUsers(message, nick)
            self.hq.Leave(channel,self, self.getUsers(message, nick))
        elif msg[0] == "!whois":
            self.hq.Whois(channel,self)