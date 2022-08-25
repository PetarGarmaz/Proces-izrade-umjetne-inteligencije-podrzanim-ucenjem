from Model import LinearQNN, QTrainer
import pygame #pip install pygame
import pygame_gui #pip install pygame_gui
from pygame.math import Vector2
import math
import random
import numpy as np
import torch #pip3 install torch torchvision torchaudio
from collections import deque

class TrainMovement():
	def __init__(self):
		self.oldState = None
		self.newMove = None

		self.batchSize = 10000
		self.maxMemory = 100000
		self.learnRate = 0.001
		self.discountRate = 0.9					#Gamma
		self.memory = deque(maxlen=self.maxMemory)
		self.reward = 0
		
		self.trainerModel = LinearQNN (7, 512, 5)
		self.trainer = QTrainer(self.trainerModel, lr=self.learnRate, gamma=self.discountRate)

	def Train(self, steps, gameNum, roundOver, enemies, entity, isNewModel):
		if(steps % 2 == 0):
			self.oldState = self.GetState(enemies, entity)

			self.newMove = self.GetAction(gameNum, isNewModel)		

			self.PerformMove(entity)

		elif(steps % 2 != 0):
			self.AssignRewards(enemies, entity)

			newState = self.GetState(enemies, entity)

			self.TrainShortMemory(self.oldState, self.newMove, self.reward, newState, roundOver)

			self.Remember(self.oldState, self.newMove, self.reward, newState, roundOver)

	def Test(self, steps, gameNum, enemies, entity):
		if(steps % 2 == 0):
			self.oldState = self.GetState(enemies, entity)

			self.newMove = self.GetAction(gameNum, False)		

			self.PerformMove(entity)

	def GetState(self, enemies, entity):
		vector = entity.movement
		pos = entity.position
		x, y = pos
		vx, vy = vector

		state = [x, y, vx, vy]

		if(len(enemies) > 0):
			for enemy in enemies:
				enemyPos = enemy.position
				ex, ey = enemyPos
				distance = enemyPos.distance_to(pos)
				
				state.append(ex)
				state.append(ey)
				state.append(distance)

		else:
			defaultPos = Vector2(0, 0)
			distance = pos.distance_to(defaultPos)
			state.append(0)
			state.append(0)
			state.append(distance)

		npState = np.array(state, dtype=int)
		return npState

	def GetAction(self, gameNum, isNewModel):
		epsilon = 100 - gameNum
		newMove = [0, 0, 0, 0, 0]
		move = 0

		if (random.randint(0, 100) < epsilon and isNewModel):
			move = random.randint(0, 4)
		else:
			state0 = torch.tensor(self.oldState, dtype=torch.float)
			move = self.trainerModel.forward(state0)
			move = torch.argmax(move).item()

		newMove[move] = 1

		return newMove

	def Remember(self, state, action, reward, nextState, roundOver):
		self.memory.append((state, action, reward, nextState, roundOver))

	def TrainLongMemory(self):
		smallSample = None

		if len(self.memory) > self.batchSize:
			smallSample = random.sample(self.memory, self.batchSize)
		else:
			smallSample = self.memory

		states, actions, rewards, newStates, dones= zip(*smallSample)

		self.trainer.TrainStep(states, actions, rewards, newStates, dones)

	def TrainShortMemory(self, state, action, reward, nextState, roundOver):
		self.trainer.TrainStep(state, action, reward, nextState, roundOver)

	def PerformMove(self, entity):
		#Aim action
		if(self.newMove[0] == 1):
			entity.movement = Vector2(0, -2)
		elif(self.newMove[1] == 1):
			entity.movement = Vector2(2, 0)
		elif(self.newMove[2] == 1):
			entity.movement = Vector2(0, 2)
		elif(self.newMove[3] == 1):
			entity.movement = Vector2(-2, 0)
		elif(self.newMove[4] == 1):
			entity.movement = Vector2(0, 0)

	def AssignRewards(self, enemies, entity):
		self.reward = 0
		pos = entity.position
		x, y = pos

		if(y <= 10 and self.newMove[0] == 1):
			self.reward = -10
		elif(x >= 790 and self.newMove[1] == 1):
			self.reward = -10
		elif(y >= 590 and self.newMove[2] == 1):
			self.reward = -10
		elif(x <= 10 and self.newMove[3] == 1):
			self.reward = -10
		
		for enemy in enemies:
			enemyPos = enemy.position
			distance = enemyPos.distance_to(pos)

			if(distance >= 400):
				self.reward = 10				

	def Save(self):
		self.trainerModel.save("driverBrain.pth")

	def Load(self):
		isLoaded = self.trainerModel.load("driverBrain.pth")
		return isLoaded