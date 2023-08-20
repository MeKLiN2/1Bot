# Spam 2.6 Module
# odsum
# 04.06.18

import time
import re

import pinylib
from util import words


class Spam:

    def __init__(self, tinybot, conf):
        """
        Initialize the Spam class.

        :param tinybot: An instance of TinychatBot.
        :type tinybot: TinychatBot
        :param user: The User object to check.
        :type user: User
        :param conf: The config file.
        :type conf: config
        """
        self.tinybot = tinybot
        self.config = conf
        self.general = ["hey", "hi", "yes", "no", "yo", "sup", "hello", "cheers", "tokes"]
        self.msgs = {}

        self.joind_time = 0
        self.joind_count = 0

        self.autoban_time = 0

        self.silent = False
        self.ban_time = 0
        self.lockdown = False

    def lockdown_onjoin(self, _user, t):

        if self.lockdown:
            return True

        if self.joind_time == 0:
            self.joind_time = t

        elif t - self.joind_time > 8:
            self.joind_count = 0
            self.joind_time = 0
            self.autoban_time = 0

        if self.joind_count > 3:
            self.autoban_time = t
            return True

        self.joind_count += 1

        self.tinybot.console_write(pinylib.COLOR['cyan'], '[User] %s:%d joined the room. (%s)' % (
            _user.nick, _user.id, self.joind_count))

        return False

    def check_lockdown(self):

        tlaped = 240

        if self.autoban_time != 0:
            self.tinybot.console_write(pinylib.COLOR['red'],
                                       '[Security] Lockdown timer started: ' + format(self.autoban_time))
        else:
            self.autoban_time = time.time()
            tlaped = 3600
            self.tinybot.console_write(pinylib.COLOR['red'],
                                       '[Security] Lockdown manually called - 1hr')
        while True:
            if not self.lockdown:
                self.tinybot.console_write(pinylib.COLOR['red'], '[Security] Lockdown Mode Reset')
                break

            time.sleep(30)
            t = time.time()
            if self.autoban_time -t < tlaped:
                self.autoban_time = 0
                self.lockdown = False

                self.do_lockdown(1)

                self.tinybot.console_write(pinylib.COLOR['red'], '[Security] Lockdown Mode Reset')
                break


    def check_msg(self, msg):

        spammer = False
        ban = False
        kick = False

        urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', msg)

        msg = words.removenonascii(msg)
        chat_words = msg.split(' ')

        chatr_user = self.tinybot.active_user.nick
        chatr_account = self.tinybot.active_user.account

        msg_time = int(time.time())
        totalcopies = 0

        # each word reviewed and scored

        spamlevel = 0.1 # no such thing as no spam

        if self.config.B_SPAMP:
            if urls:   # if url is passed in the public
                kick = True
                spamlevel = 1.5

        if len(msg) > 120:
            spamlevel = 2.0  # body of message is longer than 120 characters

        for word in chat_words:
            if word in self.general:
                spamlevel += 0.1 # word is a greeting
            else:
                if self.config.B_SPAMP:

                    if len(word) > 15:
                        spamlevel += 0.5 # word is longer than 15 characters

                    if len(word) > 100:
                        spammer = True
                        ban = True
                        # kenny

                    if not words.isword(word): # english only, comment out if needed.
                        spamlevel += 0.25  # for everyword that isn't english word

                    if word.isupper():
                        spamlevel += 0.25  # Uppercase word

                lword = word.lower()
                if self.tinybot.buddy_db.find_db_word_bans(lword):
                    ban = True
                    spammer = True

        if self.config.B_SPAMP:

            for m in self.msgs:

                if msg == m and m not in self.general:
                    totalcopies += 1
                    oldmsg = self.msgs[msg]
                    msgdiff = msg_time - oldmsg['ts']

                    if msgdiff < 4:
                        spamlevel += 0.35 # message repeated faster than 4 seconds

                    if not words.isword(chatr_user):  # user has wack nick
                        spamlevel += 0.7
                        spammer = True

                    if totalcopies > 0: # repeated message
                        spamlevel += 1.5

                        if oldmsg['nick'] == chatr_user:  # same nick as last spam
                            spamlevel += 1.0
                            spammer = True

                        if totalcopies > 1: # if copy exists more than 2 times
                            #self.autoban_time = time.time()
                            #self.do_lockdown(1)
                            ban = True

        mpkg = {'score': spamlevel, 'account': chatr_account, 'nick': chatr_user, 'msg': msg}

        self.msgs.update({'%s' % msg_time: mpkg})
        if len(self.msgs) > 12:  # store last 8 messages
            self.msgs.clear()

        if self.tinybot.active_user.user_level > 5:
            if spamlevel > 2.3:
                kick = True

            if spamlevel > 3.2:
                ban = True

        if ban:
            time.sleep(0.7)

            if self.tinybot.active_user.user_level > 5:
                if spammer and self.tinybot.active_user.user_level == 6:
                    self.tinybot.buddy_db.add_bad_account(self.tinybot.active_user.account)

                if self.lockdown:
                    self.tinybot.process_ban(self.tinybot.active_user.id)
                else:
                    self.tinybot.send_ban_msg(self.tinybot.active_user.id)

                if self.config.B_VERBOSE:
                    self.tinybot.handle_msg(
                        '\n %s %s was banned for spamming.' % (self.tinybot.boticon, self.tinybot.active_user.nick))
                spamlevel = 10

        if kick:
            if self.tinybot.active_user.user_level > 3:
                if self.lockdown:
                    self.tinybot.process_kick(self.tinybot.active_user.id)
                else:
                    self.tinybot.send_kick_msg(self.tinybot.active_user.id)

                if self.config.B_VERBOSE:
                    self.tinybot.handle_msg(
                        '\n %s %s was kicked for spamming.' % (self.tinybot.boticon, self.tinybot.active_user.nick))
                spamlevel = 10

        return spamlevel
