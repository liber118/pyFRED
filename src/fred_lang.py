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


import re


######################################################################
## natural language classes
######################################################################

class Language (object):
    word_pat = re.compile("([\w\d]+)")

    def __init__ (self):
        pass

    def parse (self, utterance):
        v = []

        for token in utterance.split(" "):
            m = Language.word_pat.match(token)

            if m:
                v.append(m.group(1).lower().strip())

        return v


if __name__=='__main__':
    lang = Language()
    print lang.parse("Hi there Fred.")
