import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class LinearQNN(nn.Module):
	def __init__(self, inputSize, hiddenSize_1, outputSize):
		super().__init__()
		self.linear1 = nn.Linear(inputSize, hiddenSize_1)
		self.linear2 = nn.Linear(hiddenSize_1, outputSize)

	def forward(self, x):
		xInput = self.linear1(x)
		xHidden_1 = F.relu(xInput)
		xOutput = self.linear2(xHidden_1)

		return xOutput

	def save(self, fileName):
		folderPath = "./brain"

		if(not os.path.exists(folderPath)):
			os.makedirs(folderPath)

		fileName = os.path.join(folderPath, fileName)
		torch.save(self.state_dict(), fileName)

	def load(self, fileName):
		folderPath = './brain'
		fileName = os.path.join(folderPath, fileName)

		if(os.path.exists(fileName)):
			self.load_state_dict(torch.load(fileName))
			return True
		else:
			return False

class QTrainer:
	def __init__(self, model, lr, gamma):
		self.model = model
		self.lr = lr
		self.gamma = gamma
		self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
		self.criterion = nn.MSELoss()

	def TrainStep(self, state, action, reward, newState, done):
		state = torch.tensor(state, dtype=torch.float)
		newState = torch.tensor(newState, dtype=torch.float)
		action = torch.tensor(action, dtype=torch.float)
		reward = torch.tensor(reward, dtype=torch.float)

		if len(state.shape) == 1:
			state = torch.unsqueeze(state, 0)
			newState = torch.unsqueeze(newState, 0)
			action = torch.unsqueeze(action, 0)
			reward = torch.unsqueeze(reward, 0)
			done = (done, )

		#Predicted Q of current action
		predictions = self.model.forward(state)
		targets = predictions.clone()

		for index in range(len(state)):
			newQ = reward[index]
			
			if(not done[index]):
				newQ = reward[index] + self.gamma * torch.max(self.model.forward(newState[index]))

			targets[index][torch.argmax(action[index]).item()] = newQ
	
		#Get new Q
		self.optimizer.zero_grad()
		loss = self.criterion(targets, predictions)
		loss.backward()

		self.optimizer.step()