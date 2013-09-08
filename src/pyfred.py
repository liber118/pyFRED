#!/usr/bin/env python
# encoding: utf-8

## Python impl of JFRED, developed by Robby Garner and Paco Nathan
## See: http://www.robitron.com/JFRED.php
## 
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
## 
##     http://www.apache.org/licenses/LICENSE-2.0
## 
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.


import os
import random
import socket
import sys


MAX_LINE_SIZE = 1024

ANCHOR_RESPONSES = [
    ('no', 'Tell me, why not?'),
    ('you', 'We were talking about you, not me.'),
    ('I', 'Do you always talk about yourself so much?'),
    ('me', 'Do you always talk about yourself so much?')
]
 
RANDOM_RESPONSES = [
    'What do you want to talk about?',
    'Would you like to play a game?',
]


class Convo:
    def converse (self, response):
        return raw_input(response)


class TCPConvo (Convo):
    def __init__ (self, client):
        self.client = client

    def converse (self, response):
        global MAX_LINE_SIZE

        self.client.send(response)
        return self.client.recv(MAX_LINE_SIZE)


def converse (convo, response):
    return convo.converse(response + "\n> ")


def build_response (utterance):
    for pattern, response in ANCHOR_RESPONSES:
        if utterance.find(pattern) != -1:
            return response

    return RANDOM_RESPONSES[
        random.randint(0, len(RANDOM_RESPONSES) - 1)]


def jfred (convo):
    response = 'Buenos nachos. How may I help you?'

    while True:
        try:
            utterance = converse(convo, response)

            if not utterance:
                return

            response = build_response(utterance)
        except EOFError:
            return


if __name__=='__main__':
    random.seed()

    if len(sys.argv) < 2:
        ## test from command line
        jfred(Convo())
    else:
        ## connect through TCP sockets
        host = ''
        port = int(sys.argv[1])
        BACKLOG = 5

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(BACKLOG)

        while True:
            client, address = s.accept() 
            jfred(TCPConvo(client));
            client.close()
