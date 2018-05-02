#!/usr/bin/env python

import sys, select, termios, tty
from transitions import Machine
import threading
import time

states = ['alwaysOn', 'normal', 'standby']

transitions = [
    { 'trigger': 'switchToAlwaysOn', 'source': 'normal', 'dest': 'alwaysOn', 'before': 'stopIdleTimer', 'after': 'inAlwaysOn' },
    { 'trigger': 'switchToNormal', 'source': 'alwaysOn', 'dest': 'normal', 'before': 'startIdleTimer', 'after': 'inNormal' },
    { 'trigger': 'idleTimeout', 'source': 'normal', 'dest': 'standby', 'before': 'rosnodeKill', 'after': 'inStandby' },
    { 'trigger': 'newMission', 'source': 'alwaysOn', 'dest': 'alwaysOn', 'before': 'execMission', 'after': 'inAlwaysOn' },
    { 'trigger': 'newMission', 'source': 'normal', 'dest': 'normal', 'before': 'stopIdleTimerAndExecMission', 'after': 'inNormal' },
    { 'trigger': 'newMission', 'source': 'standby', 'dest': 'normal', 'before': 'roslaunchWaitAndExecMission', 'after': 'inNormal' },
    { 'trigger': 'endMission', 'source': 'normal', 'dest': 'normal', 'before': 'startIdleTimer', 'after': 'inNormal' },
    { 'trigger': 'endMission', 'source': 'alwaysOn', 'dest': 'alwaysOn', 'after': 'inAlwaysOn' },
    { 'trigger': 'endMission', 'source': 'standby', 'dest': 'standby', 'after': 'inStandby' }
]


class PowerSaver(object):

    def __init__(self):
        self.startIdleTimer()

    def rosnodeKill(self):
        print 'rosnodeKill()'
        pass

    def execMission(self):
        print 'execMission()'
        pass

    def startIdleTimer(self):
        print 'startIdleTimer()'
        # startIdleTimer
        self.t = threading.Timer(20.0, triggerIdleTimeout)
        self.t.start()
        pass

    def stopIdleTimer(self):
        print 'stopIdleTimer()'
        # stopIdleTimer 
        self.t.cancel()
        pass

    def stopIdleTimerAndExecMission(self):
        # stopIdleTimer and exec mission
        self.stopIdleTimer()
        print 'execMission()'
        pass

    def roslaunchWaitAndExecMission(self):
        print 'roslaunchWaitAndExecMission()'
        time.sleep(5)
        pass


    def inAlwaysOn(self):
        print 'inAlwaysOn()'
        pass

    def inNormal(self):
        print 'inNormal()'
        pass

    def inStandby(self):
        print 'inStandby()'
        pass

    pass


def triggerNewMission():
    ps.newMission()
    pass

def triggerEndMission():
    ps.endMission()
    pass

def triggerSwitchToAlwaysOn():
    ps.switchToAlwaysOn()
    pass

def triggerSwitchToNormal():
    ps.switchToNormal()
    pass

def triggerIdleTimeout():
    ps.idleTimeout()

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

ps = PowerSaver()


pubBindings = {
    '1':triggerNewMission,
    '2':triggerEndMission,
    '3':triggerSwitchToAlwaysOn,
    '4':triggerSwitchToNormal,
}

msg = """
1:triggerNewMission
2:triggerEndMission
3:triggerSwitchToAlwaysOn
4:triggerSwitchToNormal
"""


machine = Machine(model=ps, states=states, transitions=transitions, initial='normal')

if __name__ == '__main__':

    settings = termios.tcgetattr(sys.stdin)

    print 'init: in normal()'
    
    try:
        print msg
        while(1):
            key = getKey()
            if key in pubBindings.keys():
                pubBindings[key]()
            else:
                if(key == '\x03'):
                    break


    except:
        print 'shit happens'


    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

