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
import sys


######################################################################
## rule classes
######################################################################

class ParseError (Exception):
    def __init__ (self, value):
        self.value = value

    def __str__ (self):
        return repr(self.value)


class Rule (object):
    rule_pat = re.compile("(\S+)\:\s+(\S+)")

    def __init__ (self):
        self.name = None
        self.vector = None

    def parse (self, name, vector, attrib):
        self.name = name.lower()
        self.vector = vector

        return self


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
        read a JFRED rule file, return a rule dictionary
        """

        rule_dict = {}

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
                            print rule_lines
                            break
                        else:
                            rule_dict[rule.name] = rule

                    rule_lines = []
                else:
                    rule_lines.append(line)

        return rule_dict


class IntroRule (Rule):
    def __init__ (self):
        pass

    def parse (self, name, vector, attrib):
        super(IntroRule, self).parse(name, vector, attrib)

        if len(attrib) > 0:
            raise ParseError("unrecognized rule element: " + str(attrib))

        return self


class ActionRule (Rule):
    def __init__ (self):
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
        pass

    def parse (self, name, vector, attrib):
        super(ResponseRule, self).parse(name, vector, attrib)

        if len(attrib) > 0:
            raise ParseError("unrecognized rule element: " + str(attrib))

        return self


class RegexRule (Rule):
    def __init__ (self):
        self.invokes = None

    def parse (self, name, vector, attrib):
        super(RegexRule, self).parse(name, vector, attrib)

        if "invokes" in attrib:
            self.invokes = attrib["invokes"].lower()
            del attrib["invokes"]

        if len(attrib) > 0:
            raise ParseError("unrecognized rule element: " + str(attrib))

        return self


class FuzzyRule (Rule):
    def __init__ (self):
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
    rule_dict = Rule.parse_file(sys.argv[1])
    print len(rule_dict)
