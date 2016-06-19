import sys
from Observation import *
from Reward import *
from Action import *
from Agent import *
from Environment import *
from MatrixEnvironment import *
import numpy

# Set up environment
gridEnvironment = MatrixEnvironment()
gridEnvironment.randomStart = False
gridEnvironment.humanWander = False

# Set up agent
gridAgent = Agent(gridEnvironment)

# Training episodes
episodes = 5000

for i in range(episodes):
	gridAgent.qLearn(gridAgent.initialObs)
	
	if i%1000 == 0:
		print i

# Use this to prompt user for the initial state (agent x,y and human x,y)
'''
print "agent x?"
ax = sys.stdin.readline()
ax = eval(ax.rstrip())
print "agent y?"
ay = sys.stdin.readline()
ay = eval(ay.rstrip())
print "human x?"
hx = sys.stdin.readline()
hx = eval(hx.rstrip())
print "human y?"
hy = sys.stdin.readline()
hy = eval(hy.rstrip())
'''

# Reset the environment for policy execution
gridEnvironment.verbose = True
gridEnvironment.randomStart = False
gridEnvironment.humanWander = False
# Comment the next line in to use the intial state from the prompts
# gridEnvironment.startState = [ax, ay, False, hx, hy, False]
gridAgent.agent_reset()

print "Execute Policy"
gridAgent.executePolicy(gridAgent.initialObs)
print "total reward", gridAgent.totalReward