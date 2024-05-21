import time, os, math 
import random
import numpy as np

class None_Strategy():

    def __init__(self):
        self.state = [0.0,0.0]
        self.action = 0

    def update_state(self, state):
        self.state = state
 
    def update_action(self):
       
        return self.action

class Static_Strategy():

    def __init__(self, static_pattern = 1):
        self.state = [0.0,0.0]
        self.action = static_pattern

    def update_state(self, state):
        self.state = state
    
    def update_action(self):
       
        return self.action

class Random_Strategy():

    def __init__(self, action_size = 2):
        self.state = [0.0,0.0]
        self.action = 0
        self.action_size = action_size

    def update_state(self, state):
        self.state = state
             
    def random_action(self):
        return np.random.randint(0,self.action_size)
    
    def update_action(self):
        self.action = self.random_action()
       
        return self.action    

class Rule_Strategy_Binary():
    def __init__(self, config):
        self.feedback_change_direction = 0 # 0 - keep recent feedback; 1 - feedback could get strengthened; -1: feedback should be weakened

        self.params = config

        self.RecentAccuracyList = []
        self.RecentResponseTimeList = []
        for bi in range(self.params['BufferSize']):
            self.RecentAccuracyList.append(0.0)
            self.RecentResponseTimeList.append(0.0)

        self.LastMeanResponseTime = 0.0
        self.RecentMeanResponseTime = 0.0
        self.RecentMeanAccuracy = 0.0

        self.action = 0
        self.state = [0.0,0.0]

        self.PushNum = 0
        self.KeepNum = 0

    def update_state(self, new_state):
        self.state = new_state
    
    def update_action(self):
        tempList = self.RecentAccuracyList[1:]
        tempList.append(self.state[0])
        self.RecentAccuracyList = tempList

        tempList = self.RecentResponseTimeList[1:]
        tempList.append(self.state[1])
        self.RecentResponseTimeList = tempList

        self.RecentMeanResponseTime = np.mean(np.array(self.RecentResponseTimeList))
        self.RecentMeanAccuracy = np.mean(np.array(self.RecentAccuracyList))

        self.feedback_change_direction = self.feedback_direction_decision()

        self.LastMeanResponseTime = self.RecentMeanResponseTime

        self.action = self.feedback_switch()

        print('*'*80)
        print('self.RecentAccuracyList: ', self.RecentAccuracyList)
        print('self.RecentResponseTimeList: ', self.RecentResponseTimeList)

        print('self.feedback_change_direction: ', self.feedback_change_direction)
        print('Rule-base Strategy Generate New Action: ', self.action)
        print('*'*80)

        return self.action

    def feedback_direction_decision(self):
        if self.RecentMeanResponseTime > self.params['ThresholdResponseTimeUpper'] or self.RecentMeanResponseTime - self.LastMeanResponseTime > self.params['ThresholdResponseTimeDelta']:
            if self.RecentMeanAccuracy >= self.params['ThresholdAccuracyUpper']:
                
                if self.PushNum < self.params['ThresholdPushNum']:
                    if self.KeepNum < self.params['ThresholdPushNum']:
                        self.KeepNum += 1
                        print('Keep Action, self.KeepNum: ', self.KeepNum)
                        return 0
                    else:
                        self.PushNum += 1
                        self.KeepNum = 0
                        print('Push Action, self.PushNum: ', self.PushNum, ', self.KeepNum: ', self.KeepNum)
                        return 1
                else:
                    self.PushNum = 0
                    return -1
            else:
                return -1
        else:
            return -1
    
    def feedback_switch(self):
        return max(0,min(self.action + self.feedback_change_direction, 1))

class Rule_Strategy_Quarter():
    def __init__(self, config):
        self.feedback_change_direction = 0 # 0 - keep recent feedback; 1 - feedback could get strengthened; -1: feedback should be weakened

        self.params = config

        self.RecentAccuracyList = []
        self.RecentResponseTimeList = []
        for bi in range(self.params['BufferSize']):
            self.RecentAccuracyList.append(0.0)
            self.RecentResponseTimeList.append(0.0)

        self.LastMeanResponseTime = 0.0
        self.RecentMeanResponseTime = 0.0
        self.RecentMeanAccuracy = 0.0

        self.action = 0
        self.state = [0.0,0.0]

        self.PushNum = 0
        self.KeepNum = 0

    def update_state(self, new_state):
        self.state = new_state

    
    def update_action(self):
        tempList = self.RecentAccuracyList[1:]
        tempList.append(self.state[0])
        self.RecentAccuracyList = tempList

        tempList = self.RecentResponseTimeList[1:]
        tempList.append(self.state[1])
        self.RecentResponseTimeList = tempList

        self.RecentMeanResponseTime = np.mean(np.array(self.RecentResponseTimeList))
        self.RecentMeanAccuracy = np.mean(np.array(self.RecentAccuracyList))

        self.feedback_change_direction = self.feedback_direction_decision()

        self.LastMeanResponseTime = self.RecentMeanResponseTime

        self.action = self.feedback_switch()


        print('*'*80)
        print('Rule-base Strategy Generate New Action: ', self.action)
        print('self.feedback_change_direction: ', self.feedback_change_direction)

        print('self.RecentAccuracyList: ', self.RecentAccuracyList)
        print('self.RecentResponseTimeList: ', self.RecentResponseTimeList)
        print('*'*80)

        return self.action

    def feedback_direction_decision(self):
        if self.RecentMeanResponseTime > self.params['ThresholdResponseTimeUpper'] or self.RecentMeanResponseTime - self.LastMeanResponseTime > self.params['ThresholdResponseTimeDelta']:
            if self.RecentMeanAccuracy >= self.params['ThresholdAccuracyUpper']:
                
                if self.PushNum < self.params['ThresholdPushNum']:
                    if self.KeepNum < self.params['ThresholdPushNum']:
                        self.KeepNum += 1
                        print('Keep Action, self.KeepNum: ', self.KeepNum)
                        return 0
                    else:
                        self.PushNum += 1
                        self.KeepNum = 0
                        print('Push Action, self.PushNum: ', self.PushNum, ', self.KeepNum: ', self.KeepNum)
                        return 1
                else:
                    self.PushNum = 0
                    return -3
            else:
                return -1
        else:
            return -1
    
    def feedback_switch(self):
        return max(0,min(self.action + self.feedback_change_direction, 3))

