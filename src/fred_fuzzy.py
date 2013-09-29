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


import random


######################################################################
## fuzzy logic support
######################################################################

class FuzzyUnion (object):
    def __init__ (self):
        self.rule_set = {}


    def add_rule (self, rule, weight):
        if rule.name not in self.rule_set:
            self.rule_set[rule.name] = [rule, weight]
        else:
            r, prev_weight = self.rule_set[rule.name]
            self.rule_set[rule.name] = [rule, prev_weight + weight]


    def select_rule (self):
        rule_name = random.choice(list(self.rule_set.keys()))
        rule, weight = self.rule_set[rule_name]
        return rule, weight


    def is_empty (self):
        return len(self.rule_set) == 0


if __name__=='__main__':
    fuzzy = Fuzzy()
    print fuzzy
