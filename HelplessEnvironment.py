import random
import copy
import sys
from Observation import *
from Reward import *
from Action import *
from Environment import *

class HelplessEnvironment(Environment):

	# Get the name of the action
	def actionToString(self, act):
		if act == 0:
			return "GoUp"
		elif act == 1:
			return "GoDown"
		elif act == 2:
			return "GoLeft"
		elif act == 3:
			return "GoRight"
		elif act == 4:
			return "no-op"

	# Agent executes an action, update the state
	def executeAction(self, theAction):
		newpos = [self.currentState[0], self.currentState[1]]
		if (theAction == 0):#Move Up
			if self.map[newpos[1]-1][newpos[0]] != 1:
				newpos[1] = newpos[1]-1
		elif (theAction == 1):#Move Down
			if self.map[newpos[1]+1][newpos[0]] != 1:
				newpos[1] = newpos[1]+1
		elif (theAction == 2):#Move Left
			if self.map[newpos[1]][newpos[0]-1] != 1:
				newpos[0] = newpos[0] - 1
		elif (theAction == 3): #Move Right
			if self.map[newpos[1]][newpos[0]+1] != 1:
				newpos[0] = newpos[0] + 1
		self.currentState[0] = newpos[0]
		self.currentState[1] = newpos[1]
	
##########################################

if __name__=="__main__":
	EnvironmentLoader.loadEnvironment(environment())