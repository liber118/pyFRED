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
import re
import sys


######################################################################
## rule classes
######################################################################

class ParseError (Exception):
    def __init__ (self, value):
        self.value = value

    def __str__ (self):
        return repr(self.value)


class Rules (object):
    def __init__ (self, rule_dict, first_action):
        self.rule_dict = rule_dict
        self.first_action = first_action

        # 1. create an inverted index for the fuzzy rules

        self.fuzzy_sets = {}

        for (name, r) in self.rule_dict.items():
            if isinstance(r, FuzzyRule):
                self.fuzzy_sets[name] = map(lambda x: (self.rule_dict[r.members[x]], r.weights[x]), range(0, len(r.members)))

        # 2. randomly shuffle the order of responses within all the
        # action rules, and establish priority rankings

        self.action_rules = [r for r in self.rule_dict.values() if isinstance(r, ActionRule) and (r.repeat or r.count < 1)]

        # 3. randomly shuffle the intro rule(s)

        self.intro_rules = [r for r in self.rule_dict.values() if isinstance(r, IntroRule)]

        # 4. create an inverted index for the regex rules

        self.regex_phrases = {}

        for r in self.rule_dict.values():
            if isinstance(r, RegexRule):
                try:
                    invoked = set(map(lambda x: self.rule_dict[x], r.invokes.split(" ")))

                    for phrase in r.vector:
                        self.regex_phrases[phrase] = invoked

                except KeyError, e:
                    print "ERROR: references unknown action rule", e
                    sys.exit(1)


    def fire_first (self):
        return self.first_action.fire()


    def choose_rule (self, stimulus):
        stimulus_phrase = " ".join(stimulus)
        rule_set = set([])
        response = ""

        # 1. select an optional introduction (p <= 0.03)

        if random.random < 0.03:
            response = choice(self.intro_rules).fire()

        # 2. "Fred.chooseReply()" select a target response template
        # based on key words from the input stream
        #   2.1 regex matches => invoked action rules r=100

        for (phrase, rules) in self.regex_phrases.items():
            if phrase in stimulus_phrase:
                rule_set = rule_set.union(rules)

        #   2.2 fuzzy rules => invoked action rules

        for (fuzzy, rules) in self.fuzzy_sets.items():
            if fuzzy in stimulus_phrase:
                print "FOUND!", fuzzy, rules

        #   2.3 action rules r=100

        if len(rule_set) > 0:
            selected_rule = random.choice(list(rule_set))
        else:
            selected_rule = random.choice(self.action_rules)

        # 3. test for insertion points in the selected response
        # template

        # 4. map the input verb tense and possessives/contractions...
        # NB: some kind of context-free grammar might work better here

        # 5. decide whether the current query differs from the
        # previous one...

        # 6. "Fred.logChat()" keep track of what's been said

        response += selected_rule.fire()

        return response


class Rule (object):
    rule_pat = re.compile("(\S+)\:\s+(\S+)")

    def __init__ (self):
        self.name = None
        self.vector = None
        self.count = 0

    def parse (self, name, vector, attrib):
        self.name = name.lower()
        self.vector = vector
        return self

    def fire (self):
        self.count += 1
        return random.choice(self.vector)


    @staticmethod
    def parse_lines (rule_lines):
        """
        parse the raw text lines for one JFRED rule
        """

        first_line = rule_lines.pop(0)
        m = Rule.rule_pat.match(first_line)

        if not m:
            raise ParseError("unrecognized rule format: " + first_line)

        (kind, name) = m.group(1).lower().strip(), m.group(2).lower().strip()

        if not kind in ["intro", "action", "response", "regex", "fuzzy"]:
            raise ParseError("bad rule type: " + kind)

        vector = []
        attrib = {}

        for line in rule_lines:
            m = Rule.rule_pat.match(line)

            if m:
                (elem, value) = m.group(1).lower().strip(), m.group(2).strip()

                if not elem in ["priority", "requires", "equals", "bind", "invokes", "url", "next", "repeat", "expect"]:
                    raise ParseError("bad rule elem: " + elem)
                else:
                    attrib[elem] = value
            else:
                vector.append(line)

        rule = None

        if kind == "intro":
            rule = IntroRule().parse(name, vector, attrib)
        elif kind == "action":
            rule = ActionRule().parse(name, vector, attrib)
        elif kind == "response":
            rule = ResponseRule().parse(name, vector, attrib)
        elif kind == "regex":
            rule = RegexRule().parse(name, vector, attrib)
        elif kind == "fuzzy":
            rule = FuzzyRule().parse(name, vector, attrib)

        return rule
    

    @staticmethod
    def parse_file (filename):
        """
        read a JFRED rule file, return a Rules object 
        """

        rule_dict = {}
        first_action = None

        with open(filename, "r") as f:
            rule_lines = []

            for line in f:
                line = line.strip()

                if line.startswith("#"):
                    pass
                elif len(line) == 0:
                    if len(rule_lines) > 0:
                        try:
                            rule = Rule.parse_lines(rule_lines)
                        except ParseError:
                            print "ERROR: cannot parse rule description", rule_lines
                            sys.exit(1)
                        else:
                            if not first_action and isinstance(rule, ActionRule):
                                first_action = rule

                            rule_dict[rule.name] = rule

                    rule_lines = []
                else:
                    rule_lines.append(line)

        return Rules(rule_dict, first_action)


class IntroRule (Rule):
    def __init__ (self):
        super(IntroRule, self).__init__()

    def parse (self, name, vector, attrib):
        super(IntroRule, self).parse(name, vector, attrib)

        if len(attrib) > 0:
            raise ParseError("unrecognized rule element: " + str(attrib))

        return self


class ActionRule (Rule):
    def __init__ (self):
        super(ActionRule, self).__init__()
        self.priority = 0
        self.repeat = False
        self.requires = None
        self.expect = []
        self.bind = None
        self.next = None
        self.url = None

    def parse (self, name, vector, attrib):
        super(ActionRule, self).parse(name, vector, attrib)

        if "priority" in attrib:
            self.priority = int(attrib["priority"])
            del attrib["priority"]

        if "repeat" in attrib:
            self.repeat = (attrib["repeat"].lower() == "true")
            del attrib["repeat"]

        if "requires" in attrib:
            self.requires = attrib["requires"].lower()
            del attrib["requires"]

        if "expect" in attrib:
            self.expect = attrib["expect"].lower().split(" ")
            del attrib["expect"]

        if "bind" in attrib:
            self.bind = attrib["bind"].lower()
            del attrib["bind"]

        if "next" in attrib:
            self.next = attrib["next"].lower()
            del attrib["next"]

        if "url" in attrib:
            self.url = attrib["url"].lower()
            del attrib["url"]

        if len(attrib) > 0:
            raise ParseError("unrecognized rule element: " + str(attrib))

        return self


class ResponseRule (Rule):
    def __init__ (self):
        super(ResponseRule, self).__init__()

    def parse (self, name, vector, attrib):
        super(ResponseRule, self).parse(name, vector, attrib)

        if len(attrib) > 0:
            raise ParseError("unrecognized rule element: " + str(attrib))

        return self


class RegexRule (Rule):
    def __init__ (self):
        super(RegexRule, self).__init__()
        self.invokes = None

    def parse (self, name, vector, attrib):
        super(RegexRule, self).parse(name, vector, attrib)

        if "invokes" in attrib:
            self.invokes = attrib["invokes"].lower()
            del attrib["invokes"]

        if not self.invokes:
            raise ParseError("regex rule must invoke: " + name)

        if len(attrib) > 0:
            raise ParseError("unrecognized rule element: " + str(attrib))

        return self


class FuzzyRule (Rule):
    def __init__ (self):
        super(FuzzyRule, self).__init__()
        self.weights = []
        self.members = []

    def parse (self, name, vector, attrib):
        super(FuzzyRule, self).parse(name, vector, attrib)

        if len(attrib) > 0:
            raise ParseError("unrecognized rule element: " + str(attrib))

        for line in self.vector:
            weight, rule = line.split("\t")
            weight = float(int(weight))

            self.members.append(rule.lower())
            self.weights.append(weight)

        sum_weight = sum(self.weights)
        self.weights = map(lambda x: x / sum_weight, self.weights)
        self.vector = []

        return self


if __name__=='__main__':
    rule_dict, first_action = Rule.parse_file(sys.argv[1])
    print len(rule_dict)
    print first_action
