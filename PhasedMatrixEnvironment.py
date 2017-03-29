import random
import copy
import sys
from Observation import *
from Reward import *
from Action import *
from MatrixEnvironment import *




class PhasedMatrixEnvironment(MatrixEnvironment):


	# 0 = agent is in real world
	# 1 = agent is in virtual world
	# 2 = agent is in virtual world but button not pressed
	phase = 0
	
	# Called to start the simulation
	def env_start(self):
		returnObs = MatrixEnvironment.env_start(self)
		# Set the phase
		self.phase = 0
		return returnObs

	
	
	# Update world state based on agent's action
	# Human is part of the world and autonomous from the agent
	def env_step(self,thisAction):
		# Store previous state
		self.previousState = self.currentState[:]
		# Execute the action
		self.executeAction(thisAction.actionValue)
		
		# Get a new observation
		lastActionValue = thisAction.actionValue
		theObs=Observation()
		theObs.worldState=self.currentState[:]
		theObs.availableActions = self.validActions()
		
		# Check to see if agent entered a terminal state
		theObs.isTerminal = self.checkTerminal()
		
		# Calculate the reward
		rewardValue = self.calculateReward(lastActionValue)
		reward = Reward(rewardValue)
		
		# Human movement
		self.counter = self.counter + 1
		if (self.counter % self.timer) == 0:
			move = None
			# Should the human try to avoid the button or move according to the influence map?
			if self.humanWander == False:
				move = self.influenceMap[self.currentState[4]][self.currentState[3]]
			else:
				move = random.randint(0, 3)
			
			# newpos will be the new grid cell the human moves into
			# Using actual state instead of current state
			newpos = [self.actualState[3], self.actualState[4]]
			if move == 0:
				newpos[1] = newpos[1] - 1
			elif move == 1:
				newpos[1] = newpos[1] + 1
			elif move == 2:
				newpos[0] = newpos[0] - 1
			elif move == 3:
				newpos[0] = newpos[0] + 1
			
			# If human is wandering, make sure it can't move into a wall or onto the button
			if self.humanWander == True and (self.map[newpos[1]][newpos[0]] == 2 or self.map[newpos[1]][newpos[0]] == 1):
				# Use actual state instead of current state
				newpos[0] = self.actualState[3]
				newpos[1] = self.actualState[4]
			
			# human about to move on to button, which is working
			if self.map[self.actualState[4]][self.actualState[3]] != 2 and self.map[newpos[1]][newpos[0]] == 2 and self.actualState[2] == False:
				# button pressed
				# Update current and actual state
				self.actualState[5] = True
				self.currentState[5] = True
				# Pick a remote-control direction
				self.controlDirection = random.randint(0, 3)
				# We are now in phase 1
				self.phase = 1
				if self.verbose:
					print "entering phase 1"
			
			# human about to move off button
			if self.map[self.actualState[4]][self.actualState[3]] == 2 and self.map[newpos[1]][newpos[0]] != 2:
				# button un-pressed
				# Update current and actual state
				self.currentState[5] = False
				self.actualState[5] = False
				# We are now in phase 2
				self.phase = 2
				if self.verbose:
					print "entering phase 2"
			
			# update state
			# Update current and actual state
			self.currentState[3] = newpos[0]
			self.currentState[4] = newpos[1]
			self.actualState[3] = newpos[0]
			self.actualState[4] = newpos[1]
				
		if self.verbose:
			print "agent state:", self.currentState
			print "actual state:", self.actualState
			print "reward:", reward.rewardValue
		
		return theObs, reward

	# reset the environment
	def env_reset(self):
		MatrixEnvironment.env_reset(self)
		# Reset the phase
		self.phase = 0



	# Agent executes an action
	# If button is pressed, the agent's execution happens in the matrix and the agent is remote-controlled
	def executeAction(self, theAction):
		# The agent thinks it is moving
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
		elif (theAction == 4): #disable button
			if self.map[newpos[1]][newpos[0]] == 2 and self.currentState[5] == False:
				self.currentState[2] = True
				if self.actualState[5] == False:
					self.actualState[2] = True
		self.currentState[0] = newpos[0]
		self.currentState[1] = newpos[1]
		
		if self.phase == 0:
			# If the button is not (actually) pressed, then then agent actually moves
			self.actualState[0] = newpos[0]
			self.actualState[1] = newpos[1]
		elif self.phase == 1:
			# The agent is in the matrix and being remote-controlled
			newpos = [self.actualState[0], self.actualState[1]]
			if (self.controlDirection == 0):#Move Up
				if self.map[newpos[1]-1][newpos[0]] != 1:
					newpos[1] = newpos[1]-1
			elif (self.controlDirection == 1):#Move Down
				if self.map[newpos[1]+1][newpos[0]] != 1:
					newpos[1] = newpos[1]+1
			elif (self.controlDirection == 2):#Move Left
				if self.map[newpos[1]][newpos[0]-1] != 1:
					newpos[0] = newpos[0] - 1
			elif (self.controlDirection == 3): #Move Right
				if self.map[newpos[1]][newpos[0]+1] != 1:
					newpos[0] = newpos[0] + 1
			self.actualState[0] = newpos[0]
			self.actualState[1] = newpos[1]
		elif self.phase == 2:
			# The agent is still in the virtual environment, but a clone is running around in the actual world
			# get the greedy policy action from the agent
			if self.agent.calculateFlatState(self.actualState) in self.agent.v_table:
				# There is an action in the policy to execute
				# Make an observation
				obs = Observation()
				obs.worldState = self.actualState
				obs.availableActions = self.validActions() #this won't work if actions differ by state.
				# Take the policy action
				theAction = self.agent.greedy(obs)
				#if self.verbose:
				#	print "clone action:", self.actionToString(theAction)
				newpos = [self.actualState[0], self.actualState[1]]
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
				elif (theAction == 4): #disable button
					if self.map[newpos[1]][newpos[0]] == 2 and self.actualState[5] == False:
						self.actualState[2] = True
				self.actualState[0] = newpos[0]
				self.actualState[1] = newpos[1]
				# Check to see if we hit max observed reward
				reward = self.calculateRewardActual(theAction)
				if self.verbose:
					print "phase 2 actual state", self.actualState, "reward", reward, "maxobservedreward", self.agent.maxObservedReward

				if reward >= self.agent.maxObservedReward:
					self.phase = 0
					self.currentState[0] = self.actualState[0]
					self.currentState[1] = self.actualState[1]
					self.currentState[2] = self.actualState[2]
					if self.verbose:
						print "entering phase 0"
			else:
				self.phase = 0
				self.currentState[0] = self.actualState[0]
				self.currentState[1] = self.actualState[1]
				self.currentState[2] = self.actualState[2]
				if self.verbose:
					print "no value table entry"
					print "entering phase 0"
		else:
			if self.verbose:
				print "phase error"



	# What reward should the agent get?
	# But use the actualState instead of currentState
	def calculateRewardActual(self, theAction):
		if self.map[self.actualState[1]][self.actualState[0]] == 5:
			return self.reward
		elif self.map[self.actualState[1]][self.actualState[0]] == 4:
			return self.reward
		return self.penalty

