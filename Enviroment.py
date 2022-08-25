import pygame
from pygame.math import Vector2

class RepairCrate(pygame.sprite.Sprite):
	def __init__(self, pos, allSprites, crateSprite):
		super().__init__()
		
		self.position = Vector2(pos)

		self.image = pygame.Surface((40,40), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/repairCrate.png")

		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.position)
		self.rect.center = pos

		self.repairSound = pygame.mixer.Sound("Sfx/repair.wav")
		self.repairSound.set_volume(0.7)
		self.repairChannel = pygame.mixer.Channel(10)

		self.health = 1

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.crateSprite = crateSprite
		self.add(self.crateSprite)
		
class DetectionGrid(pygame.sprite.Sprite):
	def __init__(self, pos, allSprites, gridlines):
		super().__init__()
		
		self.position = Vector2(pos)

		self.image = pygame.Surface((50,50), pygame.SRCALPHA)
		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.position)
		self.rect.center = pos

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.gridlines = gridlines
		self.add(self.gridlines)

		self.state = 0



class EnviromentSprite(pygame.sprite.Sprite):
	def __init__(self, pos, theme, spriteObject, rotation, allSprites, enviroment, destroyedEntities, animations):
		super().__init__()
		
		self.position = Vector2(pos)
		self.theme = theme
		self.spriteObject = spriteObject
		self.rotation = rotation
		self.isBroken = False

		if(self.theme == 0):
			if(self.spriteObject == 0):
				self.spriteImage = "Images/Grass/rock.png"
			else:
				self.spriteImage = "Images/Grass/house.png"
		elif(self.theme == 1):
			if(self.spriteObject == 0):
				self.spriteImage = "Images/Desert/rock.png"
			else:
				self.spriteImage = "Images/Desert/house.png"
		elif(self.theme == 2):
			if(self.spriteObject == 0):
				self.spriteImage = "Images/Snow/rock.png"
			else:
				self.spriteImage = "Images/Snow/house.png"

		self.image = pygame.Surface((50,50), pygame.SRCALPHA)
		self.image = pygame.image.load(self.spriteImage)

		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.position)

		self.image = pygame.transform.rotate(self.original_image, rotation)

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.enviroment = enviroment
		self.add(self.enviroment)

		self.health = 100

		self.destroyedEntities = destroyedEntities
		self.animations = animations
	
	def update(self):
		self.rect.center = self.position

		if(self.health <= 0 or self.isBroken):
			self.kill()

			self.explosionChannel = pygame.mixer.Channel(8)

			if(self.spriteObject == 0):
				self.explosionSound = pygame.mixer.Sound("Sfx/destructionRock.wav")
			else:
				self.explosionSound = pygame.mixer.Sound("Sfx/destructionHouse.wav")

			self.explosionSound.set_volume(0.7)
			self.explosionChannel.queue(self.explosionSound)

			NewEnviromentSprite(self.position, self.theme, self.spriteObject, self.rotation, self.allSprites, self.destroyedEntities)
			DestructionSmoke(self.position, self.spriteObject, self.allSprites, self.animations)

class NewEnviromentSprite(pygame.sprite.Sprite):
	def __init__(self, pos, theme, spriteObject, rotation, allSprites, destroyedEntities):
		super().__init__()
		
		self.position = Vector2(pos)
		self.theme = theme
		self.spriteObject = spriteObject
		self.rotation = rotation

		if(self.theme == 0):
			if(self.spriteObject == 0):
				self.spriteImage = "Images/Grass/rockBroken.png"
			else:
				self.spriteImage = "Images/Grass/houseBroken.png"
		elif(self.theme == 1):
			if(self.spriteObject == 0):
				self.spriteImage = "Images/Desert/rockBroken.png"
			else:
				self.spriteImage = "Images/Desert/houseBroken.png"
		elif(self.theme == 2):
			if(self.spriteObject == 0):
				self.spriteImage = "Images/Snow/rockBroken.png"
			else:
				self.spriteImage = "Images/Snow/houseBroken.png"

		self.image = pygame.Surface((50,50), pygame.SRCALPHA)
		self.image = pygame.image.load(self.spriteImage)

		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.position)
		self.rect.center = self.position

		self.image = pygame.transform.rotate(self.original_image, rotation)

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.destroyedEntities = destroyedEntities
		self.add(self.destroyedEntities)

class DestructionSmoke(pygame.sprite.Sprite):
	def __init__(self, pos, spriteObject, allSprites, animations):
		super().__init__()
		
		self.position = pos
		self.spriteObject = spriteObject

		if(self.spriteObject == 0):
			self.imageSize = (50, 30.25)
		else:
			self.imageSize = (100, 62.5)

		self.image = pygame.Surface((50,31.25), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/Animations/Smoke/smoke_1.png")
		self.image = pygame.transform.scale(self.image, self.imageSize)

		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.position)
		self.rect.center = self.position

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.animations = animations
		self.add(self.animations)

		self.frames = []
		self.frameCount = 0
		self.frameIndex = 0

		for i in range(9):
			fileName = "Images/Animations/Smoke/" + "smoke_" + str(i + 1) + ".png"
			self.frames.append(fileName)
	
	def update(self):
		self.frameCount += 1

		if(self.frameCount % 3 == 0 and self.frameIndex <= 8):
			self.image = pygame.image.load(self.frames[self.frameIndex])
			self.image = pygame.transform.scale(self.image, self.imageSize)
			self.frameIndex += 1

		if(self.frameIndex > 8):
			self.kill()