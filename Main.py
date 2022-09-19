from audioop import cross
import pygame #pip install pygame
import pygame_gui #pip install pygame_gui
from pygame.math import Vector2
import math
import random
import numpy as np
import torch #pip3 install torch torchvision torchaudio

from Model import LinearQNN, QTrainer
from TrainMovement import TrainMovement
from Plot import Plot
from collections import deque

from Agent import Agent, AgentTurret, AgentHealthSprite, AgentReloadBar120mm, AgentReloadBarSmall, AgentCrosshair
from Enemy import Enemy, EnemyTurret, EnemyHealthSprite

from TrainMovement import TrainMovement
from TrainAim import TrainAim

class GameModel():
	def __init__(self):
		#All sprite groups
		self.allSprites = pygame.sprite.Group()
		self.enemies = pygame.sprite.Group()
		self.enemyTurrets = pygame.sprite.Group()
		self.players = pygame.sprite.Group()
		self.playerTurrets = pygame.sprite.Group()
		self.enemyProjectiles = pygame.sprite.Group()
		self.playerProjectiles = pygame.sprite.Group()
		self.bars = pygame.sprite.Group()
		self.destroyedEntities = pygame.sprite.Group()
		self.animations = pygame.sprite.Group()

		#All objects for training - Enemies, Crates, enviroment
		self.allEnemies = []
		self.allEnemyTurrets = []
		self.allCrates = []
		self.allEnviroment = []

		#Defining an agent
		self.agent = Agent((400, 300), self.allSprites, self.players, self.destroyedEntities)
		self.agentTurret = AgentTurret(self.agent, self.allSprites, self.playerTurrets, self.playerProjectiles)
		self.agentCrosshair = AgentCrosshair(self.agentTurret, self.allSprites, self.playerTurrets)

		self.agentHealthBar = AgentHealthSprite(self.agent, self.bars)
		self.agentReloadBar = AgentReloadBar120mm(self.agent, self.agentTurret, self.bars)
		self.agentReloadBar2 = AgentReloadBarSmall(self.agent, self.agentTurret, self.bars)

		#Enemy/Round controllers
		self.roundStart = 0
		self.enemyNum = 1
		self.score = 0

		#Theme controllers: 0 = "Grass"; 1 = "Desert"; 2 = "Snow";
		self.theme = 0

		#Misc
		self.clock = pygame.time.Clock()
		self.deltaTime = 0

	def GameEnemySpawner(self):
		if(len(self.enemies) <= 0):
			self.roundStart += 5
		else:
			self.roundStart = 0

		if(self.roundStart >= 5):
			self.allEnemies = []
			self.allEnemyTurrets = []

			for i in range(self.enemyNum):
				x = random.choice([0, 800])
				y = random.choice([0, 600])

				newX = random.randint(0, 800)
				newY = random.randint(0, 600)

				fireTiming = random.randint(1, 6)

				#Generate enemies
				enemy = Enemy((x, y), (newX, newY), self.agent, self.allSprites, self.enemies, self.destroyedEntities, self.animations)
				enemyTurret = EnemyTurret(enemy, self.agent, fireTiming, self.allSprites, self.enemyTurrets, self.enemyProjectiles)
				enemyHealthBar = EnemyHealthSprite(enemy, self.bars)

				self.allEnemies.append(enemy)
				self.allEnemyTurrets.append(enemyTurret)


	def GameLogic(self):
		self.playerToEnemyHitList = pygame.sprite.groupcollide(self.enemies, self.playerProjectiles, False, True)
		self.enemyToPlayerHitList = pygame.sprite.groupcollide(self.players, self.enemyProjectiles, False, True)

		for enemy, projectileList in self.playerToEnemyHitList.items():
			for projectile in projectileList:
				enemy.health -= projectile.damage
				self.score += 1

		for player, projectileList in self.enemyToPlayerHitList.items():
			for projectile in projectileList:
				player.health -= projectile.damage
				#self.score -= 1
			


	def GameDraw(self, view):
		self.allSprites.update()
		self.bars.update()	
		view.screen.fill((255, 255, 255))
		view.screen.blit(view.background, (0, 0))

		#Layered drawing (top = last drawn; bottom = first drawn)
		self.destroyedEntities.draw(view.screen)		
		self.enemies.draw(view.screen)
		self.enemyTurrets.draw(view.screen)
		self.players.draw(view.screen)
		self.playerTurrets.draw(view.screen)
		self.enemyProjectiles.draw(view.screen)
		self.playerProjectiles.draw(view.screen)
		self.bars.draw(view.screen)
		self.animations.draw(view.screen)

		pygame.display.flip()
		self.clock.tick(60)

class GameView():
	def __init__(self):
		self.model = GameModel()

		#Setting up game screen and UI managers
		self.screen = pygame.display.set_mode((800, 600))
		self.guiManager = pygame_gui.UIManager((800, 600))
		
		#Setting up backgrounds and icon
		self.background = None

		self.grassBG = pygame.image.load("Images/Grass/background.png")
		self.desertBG = pygame.image.load("Images/Desert/background.png")
		self.snowBG = pygame.image.load("Images/Snow/background.png")

		self.mainMenuBackground = pygame.image.load("Images/UI/mainMenuBG.png")
		self.optionsBackground = pygame.image.load("Images/UI/optionsBG.png")

		self.menuBackground = self.mainMenuBackground

		self.gameIcon = pygame.Surface((75,75))
		self.gameIcon.set_colorkey((0,0,0))
		self.gameIcon = pygame.image.load("Images/gameIcon.png")

		#Some window settings
		pygame.display.set_caption("Thunder Run")
		pygame.display.set_icon(self.gameIcon)

		#Buttons - Main Menu
		self.playButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, 125),(300, 75)), text="Test Agent", manager=self.guiManager)
		self.trainButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, 225),(300, 75)), text="Train Agent", manager=self.guiManager)
		self.optionsButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, 325),(300, 75)), text="Options", manager=self.guiManager)
		self.quitButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, 425),(300, 75)), text="Quit Game", manager=self.guiManager)

		#Buttons/Sliders - Options
		self.healthSlider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((125, 200), (250, 25)), start_value=200, value_range=[50, 500], manager=self.guiManager)
		self.movementSlider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((425, 200), (250, 25)), start_value=3, value_range=[1, 5], manager=self.guiManager)
		self.themeSlider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((275, 355), (250, 25)), start_value=0, value_range=[0, 2], manager=self.guiManager)

		self.healthSliderText = self.healthSlider.get_current_value()
		self.movementSliderText = self.movementSlider.get_current_value()
		self.themeSliderText = "Grass"

		self.healthSliderNumber = pygame_gui.elements.UITextBox(html_text="<font face=’Agency FB’>{}</font>".format(self.healthSliderText), relative_rect=pygame.Rect((210, 230), (80, 35)), manager=self.guiManager)
		self.movementSliderNumber = pygame_gui.elements.UITextBox(html_text="<font face=’Agency FB’>{}</font>".format(self.movementSliderText), relative_rect=pygame.Rect((510, 230), (80, 35)), manager=self.guiManager)
		self.themeSliderNumber = pygame_gui.elements.UITextBox(html_text="<font face=’Agency FB’>{}</font>".format(self.themeSliderText), relative_rect=pygame.Rect((350, 385), (100, 35)), manager=self.guiManager)

		self.backToMenuButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((275, 450),(250, 50)), text="Back", manager=self.guiManager)

		self.healthSliderNumber.hide()
		self.movementSliderNumber.hide()
		self.themeSliderNumber.hide()

		self.healthSlider.hide()
		self.movementSlider.hide()
		self.themeSlider.hide()

		self.backToMenuButton.hide()

	def MenuDraw(self):
		self.guiManager.update(self.model.deltaTime)
		self.screen.fill((255, 255, 255))
		self.screen.blit(self.menuBackground, (0,0))
		self.guiManager.draw_ui(self.screen)

		pygame.display.update()

class GameController():
	def __init__(self):
		#Initializing pygame and pygame sound settings
		pygame.init()
		pygame.mixer.init(frequency = 44100, size = 32, channels = 2, buffer = 512)
		pygame.mixer.set_num_channels(16)

		self.model = GameModel()
		self.view = GameView()

		#Misc
		self.done = False
		self.menuDone = False
		self.paused = False

		self.frameIteration = 0
		self.steps = 0
		self.gameNum = 1
		
		self.isTraining = False
		self.isNewModel = True
		self.roundOver = False

		self.movementTrainerObject = TrainMovement()
		self.aimTrainerObject = TrainAim()

		#Plot
		self.plotScores = [0]
		self.plotMeanScores = [0]
		self.totalScore = 0
		self.record = 0

		#Start with main menu
		self.UpdateMainMenu()

	def MainMenuEventHandler(self):
		self.model.deltaTime = self.model.clock.tick(60)/1000

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.menuDone = True
				self.done = True

			if event.type == pygame.USEREVENT:
				if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
					if event.ui_element == self.view.playButton:
						self.model.theme = self.view.themeSlider.get_current_value()

						if(self.model.theme == 0):
							self.view.background = self.view.grassBG
						elif(self.model.theme == 1):
							self.view.background = self.view.desertBG
						elif(self.model.theme == 2):
							self.view.background = self.view.snowBG

						self.model.agent.maxHealth = self.view.healthSlider.get_current_value()
						self.model.agent.health = self.model.agent.maxHealth

						self.menuDone = True
						self.isTraining = False
						self.UpdateGame()
					
					elif event.ui_element == self.view.trainButton:
						self.model.theme = self.view.themeSlider.get_current_value()

						if(self.model.theme == 0):
							self.view.background = self.view.grassBG
						elif(self.model.theme == 1):
							self.view.background = self.view.desertBG
						elif(self.model.theme == 2):
							self.view.background = self.view.snowBG

						self.model.agent.maxHealth = self.view.healthSlider.get_current_value()
						self.model.agent.health = self.model.agent.maxHealth

						self.menuDone = True
						self.isTraining = True
						self.UpdateGame()
	
					elif event.ui_element == self.view.optionsButton:
						self.view.menuBackground = self.view.optionsBackground
						self.view.playButton.hide()
						self.view.trainButton.hide()
						self.view.optionsButton.hide()
						self.view.quitButton.hide()

						self.view.healthSliderNumber.show()
						self.view.movementSliderNumber.show()
						self.view.themeSliderNumber.show()

						self.view.healthSlider.show()
						self.view.movementSlider.show()
						self.view.themeSlider.show()

						self.view.backToMenuButton.show()

					elif event.ui_element == self.view.quitButton:
						self.done = True

					if event.ui_element == self.view.backToMenuButton:
						self.view.menuBackground = self.view.mainMenuBackground

						self.view.playButton.show()
						self.view.trainButton.show()
						self.view.optionsButton.show()
						self.view.quitButton.show()

						self.view.healthSliderNumber.hide()
						self.view.movementSliderNumber.hide()
						self.view.themeSliderNumber.hide()

						self.view.healthSlider.hide()
						self.view.movementSlider.hide()
						self.view.themeSlider.hide()

						self.view.backToMenuButton.hide()						
				
				if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
					if event.ui_element == self.view.healthSlider:
						self.view.healthSliderText = self.view.healthSlider.get_current_value()
						self.view.healthSliderNumber.kill()
						self.view.healthSliderNumber = pygame_gui.elements.UITextBox(html_text="<font face=’Agency FB’>{}</font>".format(self.view.healthSliderText), relative_rect=pygame.Rect((210, 230), (80, 35)), manager=self.view.guiManager)
					elif event.ui_element == self.view.movementSlider:
						self.view.movementSliderText = self.view.movementSlider.get_current_value()
						self.view.movementSliderNumber.kill()
						self.view.movementSliderNumber = pygame_gui.elements.UITextBox(html_text="<font face=’Agency FB’>{}</font>".format(self.view.movementSliderText), relative_rect=pygame.Rect((510, 230), (80, 35)), manager=self.view.guiManager)
					elif event.ui_element == self.view.themeSlider:
						val = self.view.themeSlider.get_current_value()
						self.view.themeSliderText = self.NumToString(val)

						self.view.themeSliderNumber.kill()
						self.view.themeSliderNumber = pygame_gui.elements.UITextBox(html_text="<font face=’Agency FB’>{}</font>".format(self.view.themeSliderText), relative_rect=pygame.Rect((350, 385), (100, 35)), manager=self.view.guiManager)

			self.view.guiManager.process_events(event)

	def GameEventHandler(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.menuDone = True
				self.done = True

	def UpdateMainMenu(self):
		while not self.done and not self.menuDone:
			self.MainMenuEventHandler()
			self.view.MenuDraw()

	def UpdateGame(self):
		self.UpdatePlot()

		movementLoaded = self.movementTrainerObject.Load()
		aimLoaded = self.aimTrainerObject.Load()

		if(movementLoaded and aimLoaded):
			self.isNewModel = False

		while not self.done and self.menuDone:
			self.GameEventHandler()

			if(self.model.agent.health <= 0):
				self.roundOver = True
				self.ResetGame()

			if(not self.paused):
				self.model.GameEnemySpawner()
				self.model.GameLogic()
				self.model.GameDraw(self.view)

				if(self.frameIteration % 10 == 0):
					if(self.isTraining):
						self.movementTrainerObject.Train(self.steps, self.gameNum, self.roundOver, self.model.enemies, self.model.agent, self.isNewModel)
						self.aimTrainerObject.Train(self.steps, self.gameNum, self.roundOver, self.model.enemies, self.model.agentCrosshair, self.model.agentTurret, self.isNewModel)
					else:
						self.movementTrainerObject.Test(self.steps, self.gameNum, self.model.enemies, self.model.agent)
						self.aimTrainerObject.Test(self.steps, self.gameNum, self.model.enemies, self.model.agentCrosshair, self.model.agentTurret)
					
					self.steps += 1

				self.frameIteration += 1

	def ResetGame(self):
		self.gameNum += 1
		self.frameIteration = 0
		self.steps = 0

		if(self.isTraining):
			self.movementTrainerObject.TrainLongMemory()
			self.aimTrainerObject.TrainLongMemory()

			if self.model.score > self.record:
				self.record = self.model.score
				self.movementTrainerObject.Save()
				self.aimTrainerObject.Save()
	
		self.UpdatePlot()

		self.model.__init__()
		self.model.agent.maxHealth = self.view.healthSlider.get_current_value()
		self.model.agent.health = self.model.agent.maxHealth
		self.roundOver = False

	def UpdatePlot(self):
		self.plotScores.append(self.model.score)
		self.totalScore += self.model.score
		meanScore = self.totalScore / self.gameNum
		self.plotMeanScores.append(meanScore)

		Plot(self.plotScores, self.plotMeanScores)

	def NumToString(self, num):
		strng = ""

		if num == 0:
			strng = "Grass"
		elif num == 1:
			strng = "Desert"
		elif num == 2:
			strng = "Snow"
		
		return strng

GameController()
pygame.quit()