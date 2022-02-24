#!/usr/bin/env python3
import re
import argparse
from termcolor import colored

baseRegex = "({} ([A-Za-z0-9_]+)\s*\(([^)]+)\))"
eventRegex = baseRegex.format("event")
emitRegex = baseRegex.format("emit")
doxygenCommentRegex = "(/\*[^;]+?(?=\*/)\*/)\s+event ({})"
doxygenParameterRegex = "@param (\w+) (.+)"

parser = argparse.ArgumentParser(description='Check for correct event parameters')
parser.add_argument('INPUT_FILE', help='Contract to assess')
args = parser.parse_args()

def pullEvEm(inpFile):
    f = open(inpFile)
    c = f.read()
    f.close()
    r = re.findall(eventRegex, c, flags=re.DOTALL)
    events = {}
    for ev in r:
        #events[Name of Event] = [Code, split parameters, param comments from Doxygen comments, OutputStrings for displayEvEm]
        events[ev[1]] = [ev[0], list(map(lambda i: i.strip().split(" ")[-1], ev[2].split(","))), {}, []]

    for ev in events:
        o = re.findall(doxygenCommentRegex.format(ev), c, flags=re.DOTALL)
        if o:
            events[ev][2] = dict(re.findall(doxygenParameterRegex, o[0][0]))

    r = re.findall(emitRegex, c, flags=re.DOTALL)
    emits = []
    for em in r:
        #[Code, Name Of Event, split parameters]
        emits.append((em[0], em[1], list(map(lambda i: i.strip().split(" ")[-1], em[2].split(",")))))
    return (events, emits)


def displayEvEm(events, emits):
    unableDisplay = []
    for em in emits:
        if em[1] not in events:
            unableDisplay.append(em[0])
            continue
        ev = events[em[1]]
        mapping = ""
        for i in range(0, len(ev[1])):
            mapping += "\n"+colored(ev[1][i], "blue")+" => "+colored(em[2][i], "red")+","
            if ev[1][i] in ev[2]:
                mapping += colored("//"+ev[2][ev[1][i]], "green")
        if mapping.endswith(","):
            mapping = mapping[:-1]
        outputString = "Event: {}\nEmit: {}\nMapping: {}({}\n)\n".format(ev[0], em[0], em[1], mapping)
        ev[3].append(outputString)
    for ev in events:
        print("---"+ev+"---")
        if not events[ev][3]: print("***Unused event***")
        for os in events[ev][3]:
            print(os)


def auditContract(inpFile):
    events, emits = pullEvEm(inpFile)
    displayEvEm(events, emits)

if __name__=="__main__":
    r = auditContract(args.INPUT_FILE)
