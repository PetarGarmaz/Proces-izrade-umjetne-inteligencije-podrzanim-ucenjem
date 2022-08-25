from matplotlib.style import available
import pygame
from pygame.math import Vector2
import math
import random

class AgentHealthSprite(pygame.sprite.Sprite):
	def __init__(self, player, sprite):
		super().__init__()

		self.player = player
		self.playerPos = self.player.position

		self.image = pygame.Surface((10,10), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/healthBar.png")

		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.playerPos)		

		self.sprite = sprite
		self.add(self.sprite)

		self.position = Vector2(self.playerPos.x, self.playerPos.y + 30)

	def update(self):
		self.health = self.player.health
		self.maxHealth = self.player.maxHealth

		self.position = Vector2(self.playerPos.x, self.playerPos.y + 30)
		self.rect.center = self.position

		self.image = pygame.transform.scale(self.original_image, (int(self.health/self.maxHealth * 100), 10))
		self.rect = self.image.get_rect(center=self.rect.center)
        
		if(self.player.alive() == False):
			self.kill()

class AgentReloadBar120mm(pygame.sprite.Sprite):
	def __init__(self, player, turret, sprite):
		super().__init__()

		self.player = player
		self.playerPos = self.player.position

		self.turret = turret

		self.image = pygame.Surface((10,10), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/reloadBar.png")

		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.playerPos)

		self.sprite = sprite
		self.add(self.sprite)

		self.position = Vector2(self.playerPos.x, self.playerPos.y + 45)

	def update(self):
		self.cooldown = self.turret.cooldown

		self.position = Vector2(self.playerPos.x, self.playerPos.y + 45)
		self.rect.center = self.position

		self.image = pygame.transform.scale(self.original_image, (int(self.cooldown/7 * 100), 10))
		self.rect = self.image.get_rect(center=self.rect.center)

		if(self.player.alive() == False):
			self.kill()

class AgentProjectile120mm(pygame.sprite.Sprite):
	def __init__(self, startPos, angle, allSprites, projectiles):
		super().__init__()
		self.image = pygame.Surface((10,10), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/projectile.png")
		
		self.shootSound = pygame.mixer.Sound("Sfx/playerShot.wav")
		self.shootChannel1 = pygame.mixer.Channel(2)

		self.original_image = self.image
		self.rect = self.image.get_rect(center=startPos)

		self.position = Vector2(startPos)
		self.velocity = 30
		self.damage = 50
		self.range = 2

		self.angle = angle
		self.direction = Vector2(0,1)

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.projectiles = projectiles
		self.add(self.projectiles)

		self.hasFired = True

	def update(self):
		if(self.hasFired == True):
			self.direction.rotate_ip(self.angle + 180)
			self.shootChannel1.play(self.shootSound)
			self.hasFired = False
		
		self.range -= 1/60

		self.position += self.direction * self.velocity
		self.rect.center = self.position

		if(self.range <= 0):
			self.kill()

class AgentReloadBarSmall(pygame.sprite.Sprite):
	def __init__(self, player, turret, sprite):
		super().__init__()

		self.player = player
		self.playerPos = self.player.position

		self.turret = turret

		self.image = pygame.Surface((10,10), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/reloadBar2.png")

		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.playerPos)

		self.sprite = sprite
		self.add(self.sprite)

		self.position = Vector2(self.playerPos.x, self.playerPos.y + 60)

	def update(self):
		self.cooldown = self.turret.cooldown2

		self.position = Vector2(self.playerPos.x, self.playerPos.y + 60)
		self.rect.center = self.position

		self.image = pygame.transform.scale(self.original_image, (int(self.cooldown/0.1 * 100), 10))
		self.rect = self.image.get_rect(center=self.rect.center)

		if(self.player.alive() == False):
			self.kill()

class AgentProjectileSmall(pygame.sprite.Sprite):
	def __init__(self, startPos, angle, allSprites, projectiles):
		super().__init__()
		self.image = pygame.Surface((10,10), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/tracer.png")
		
		randomShootSound = ["Sfx/playerShotM2_1.wav", "Sfx/playerShotM2_2.wav", "Sfx/playerShotM2_3.wav"]
		self.shootSound = pygame.mixer.Sound(random.choice(randomShootSound))
		self.shootChannel = pygame.mixer.Channel(3)
		
		self.original_image = self.image
		self.rect = self.image.get_rect(center=startPos)

		self.position = Vector2(startPos)
		self.velocity = 25
		self.damage = 4
		self.range = 2

		self.angle = angle
		self.direction = Vector2(0,1)

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.projectiles = projectiles
		self.add(self.projectiles)

		self.hasFired = True
		self.image = pygame.transform.rotate(self.original_image, random.randint(0, 360))

	def update(self):
		if(self.hasFired == True):
			self.direction.rotate_ip(self.angle + 180)
			self.shootChannel.play(self.shootSound)
			self.hasFired = False
		
		self.range -= 1/60

		self.position += self.direction * self.velocity
		self.rect.center = self.position

		if(self.range <= 0):
			self.kill()

class Agent(pygame.sprite.Sprite):
	def __init__(self, pos, allSprites, players, destroyedEntities):
		super().__init__()	

		self.image = pygame.Surface((30,30), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/tankHull.png")

		self.idleSound = pygame.mixer.Sound("Sfx/tankIdle.wav")
		self.moveSound = pygame.mixer.Sound("Sfx/tankMove.wav")

		self.idleChannel = pygame.mixer.Channel(0)
		self.moveChannel = pygame.mixer.Channel(1)

		self.original_image = self.image
		self.rect = self.image.get_rect(center=pos)

		self.maxHealth = 100
		self.health = self.maxHealth
		
		self.movement = Vector2(0, 0)
		self.currentAngle = 0
		self.targetAngle = 0

		self.position = Vector2(pos)
		self.newPosition = Vector2(pos)
		self.dir = Vector2(0, -1)

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.players = players
		self.add(self.players)

		self.destroyedEntities = destroyedEntities

	def update(self):
		self.Movement()
		self.PlaySound()
		self.Stats()

	def Movement(self):
		newPosition = self.position + self.movement

		if(self.movement.x > 0 or self.movement.y > 0 or self.movement.x < 0 or self.movement.y < 0):
			defaultVector = Vector2(0, 0)
			self.currentAngle = defaultVector.angle_to(self.movement) + 90
			self.dir.rotate_ip(self.currentAngle)

			self.image = pygame.transform.rotate(self.original_image, -self.currentAngle)
			self.rect = self.image.get_rect(center=self.rect.center)

			if(newPosition.x > 0 and newPosition.x < 800 and newPosition.y > 0 and newPosition.y < 600):
				self.position += self.movement
				self.rect.center = self.position

	def PlaySound(self):
		if(self.movement.x == 0 and self.movement.y == 0):
			self.moveChannel.stop()
			self.idleChannel.queue(self.idleSound)	
		else:
			self.idleChannel.stop()
			self.moveChannel.queue(self.moveSound)

	def Stats(self):
		if(self.health <= 0):
			self.health = 0
			self.idleChannel.stop()
			self.moveChannel.stop()
			self.kill()
			DestroyedTank(self.position, self.currentAngle, self.allSprites, self.destroyedEntities)

class AgentTurret(pygame.sprite.Sprite):
	def __init__(self, player, allSprites, turretSprite, projectiles):
		super().__init__()	
		self.hull = player
		self.hullPos = player.position

		self.image = pygame.Surface((75,75), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/tankTurret.png")

		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.hullPos)

		self.currentAngle = 0
		self.cooldown = 7
		self.cooldown2 = 0.1

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.turretSprite = turretSprite
		self.add(self.turretSprite)

		self.projectiles = projectiles
		
		self.position = Vector2(self.hullPos)
		self.newPosition = Vector2(self.hullPos)
		self.dir = Vector2(1, 0)
		self.movement = Vector2(0, 0)

		self.doFireMain = False
		self.doFireSecondary = False
	
	def update(self):
		self.CooldownTimer()
		self.UpdatePosition()	
		self.Rotate()
		self.Fire()
		self.Stats()

	def CooldownTimer(self):
		if self.cooldown < 7:
			self.cooldown += 1/60
		else:
			self.cooldown = 7

		if self.cooldown2 < 0.1:
			self.cooldown2 += 1/60
		else:
			self.cooldown2 = 0.1

	def UpdatePosition(self):
		newPosition = self.newPosition + self.movement

		if(newPosition.x > 0 and newPosition.x < 800 and newPosition.y > 0 and newPosition.y < 600):
			self.newPosition += self.movement

		self.position = self.hullPos
		self.rect.center = self.hull.rect.center

	def Rotate(self):
		x, y = self.newPosition

		self.currentAngle = math.atan2((y - self.hullPos.y), (x - self.hullPos.x))
		self.currentAngle = math.degrees(self.currentAngle)
		self.currentAngle += 90

		self.image = pygame.transform.rotate(self.original_image, -self.currentAngle)
		self.rect = self.image.get_rect(center=self.rect.center)

	def Fire(self):
		if(self.doFireMain and self.cooldown == 7):
			self.cooldown = 0
			AgentProjectile120mm(self.position, self.currentAngle, self.allSprites, self.projectiles)

		if(self.doFireSecondary and self.cooldown2 == 0.1):
			self.cooldown2 = 0
			AgentProjectileSmall(self.position, self.currentAngle, self.allSprites, self.projectiles)

	def Stats(self):
		if(self.hull.alive() == False):
			self.kill()

class AgentCrosshair(pygame.sprite.Sprite):
	def __init__(self, turret, allSprites, playerTurrets):
		super().__init__()	
		self.turret = turret
		self.pos = self.turret.newPosition

		self.image = pygame.Surface((50,50), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/crosshair.png")

		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.pos)

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.playerTurrets = playerTurrets
		self.add(self.playerTurrets)
	
	def update(self):
		self.UpdatePosition()	

	def UpdatePosition(self):
		self.position = self.turret.newPosition
		self.rect.center = self.position


class DestroyedTank(pygame.sprite.Sprite):
	def __init__(self, pos, rotation, allSprites, destroyedEntities):
		super().__init__()
		
		self.position = pos
		self.rotation = rotation

		self.image = pygame.Surface((100,100), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/enemyTankDestroyed.png")

		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.position)

		self.image = pygame.transform.rotate(self.original_image, rotation)

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.destroyedEntities = destroyedEntities
		self.add(self.destroyedEntities)
	
	def update(self):
		self.rect.center = self.position