# lamer 1.0
# meklin
# 06.24.2014

import time
import re

import pinylib
from util import words


class Lame:

    def __init__(self, tinybot, conf):
        self.tinybot = tinybot
        self.config = conf
        self.general = ["tokes"]
        self.msgs = {}

    def lame(self, msg, uid):
            if _user is not None:
                if _user.user_level == 8 or self.tinybot.active_user.account
in self.lamers:

self.tinybot.active_user.account


    def check_msg(self, msg):

        lamer = False
        ban = False
        kick = False

        urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', msg)
        lamerz = 

        msg = words.removenonascii(msg)
        chat_words = msg.split(' ')

        chatr_user = self.tinybot.active_user.nick
        chatr_account = self.tinybot.active_user.account

        msg_time = int(time.time())
        totalcopies = 0

        spamlevel = 0.1 
        if self.config.B_SPAMP:
            if urls:
                kick = True
                spamlevel = 1.5

        if len(msg) > 120:
            spamlevel = 2.0

        for word in chat_words:
            if self.config.B_LAMERZ:
            lword = word.lower()
            if self.tinybot.buddy_db.find_db_lamers(lword):
                kick = True
                spammer = True

        mpkg = {'score': spamlevel, 'account': chatr_account, 'nick': chatr_user, 'msg': msg}



        if kick:
            if self.tinybot.active_user.user_level > 3:
                if self.lockdown:
                    self.tinybot.process_kick(self.tinybot.active_user.id)
                else:
                    self.tinybot.send_kick_msg(self.tinybot.active_user.id)

                if self.config.B_VERBOSE:
                    self.tinybot.handle_msg(
                        '\n%s(llama): Bleeat! Oorgle!' % (self.tinybot.active_user.nick))
                spamlevel = 10

        return spamlevel
