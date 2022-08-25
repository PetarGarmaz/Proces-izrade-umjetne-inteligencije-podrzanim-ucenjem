import pygame
from pygame.math import Vector2
import math

class PlayerHealthSprite(pygame.sprite.Sprite):
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

class PlayerReloadBar120mm(pygame.sprite.Sprite):
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

class PlayerReloadBar30mm(pygame.sprite.Sprite):
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

		self.image = pygame.transform.scale(self.original_image, (int(self.cooldown/0.5 * 100), 10))
		self.rect = self.image.get_rect(center=self.rect.center)

		if(self.player.alive() == False):
			self.kill()

class PlayerProjectile120mm(pygame.sprite.Sprite):
	def __init__(self, startPos, angle, allSprites, projectiles):
		super().__init__()
		self.image = pygame.Surface((10,10), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/projectile.png")
		
		self.shootSound = pygame.mixer.Sound("Sfx/playerShot.wav")
		self.shootChannel1 = pygame.mixer.Channel(2)

		self.original_image = self.image
		self.rect = self.image.get_rect(center=startPos)

		self.position = Vector2(startPos)
		self.velocity = 10
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
			self.direction.rotate_ip(self.angle - 90)
			self.shootChannel1.play(self.shootSound)
			self.hasFired = False
		
		self.range -= 1/60

		self.position += self.direction * self.velocity
		self.rect.center = self.position

		if(self.range <= 0):
			self.kill()

class PlayerProjectile30mm(pygame.sprite.Sprite):
	def __init__(self, startPos, angle, allSprites, projectiles):
		super().__init__()
		self.image = pygame.Surface((10,10), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/projectile.png")
		
		self.shootSound = pygame.mixer.Sound("Sfx/playerShot30mm.wav")
		self.shootChannel2 = pygame.mixer.Channel(3)

		self.original_image = self.image
		self.rect = self.image.get_rect(center=startPos)

		self.position = Vector2(startPos)
		self.velocity = 25
		self.damage = 10
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
			self.direction.rotate_ip(self.angle - 90)
			self.shootChannel2.play(self.shootSound)
			self.hasFired = False
		
		self.range -= 1/60

		self.position += self.direction * self.velocity
		self.rect.center = self.position

		if(self.range <= 0):
			self.kill()

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, allSprites, players):
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
		
		self.movementSpeed = 0
		self.rotationSpeed = 0
		self.currentAngle = 0

		self.position = Vector2(pos)
		self.dir = Vector2(0, 1)

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.players = players
		self.add(self.players)

	def update(self):
		self.Movement()
		self.PlaySound()
		self.PlayerStats()

	def Movement(self):
		self.dir.rotate_ip(self.rotationSpeed)
		self.currentAngle += self.rotationSpeed

		self.image = pygame.transform.rotate(self.original_image, -self.currentAngle)
		self.rect = self.image.get_rect(center=self.rect.center)

		newPosition = self.position + self.dir * self.movementSpeed

		if(newPosition.x > 0 and newPosition.x < 800 and newPosition.y > 0 and newPosition.y < 600):
			self.position += self.dir * self.movementSpeed
			self.rect.center = self.position
		
	def PlaySound(self):
		if(self.movementSpeed == 0 and self.rotationSpeed == 0):
			self.moveChannel.stop()
			self.idleChannel.queue(self.idleSound)	
		else:
			self.idleChannel.stop()
			self.moveChannel.queue(self.moveSound)

	def PlayerStats(self):
		if(self.health <= 0):
			self.idleChannel.stop()
			self.moveChannel.stop()
			self.kill()

class PlayerTurret(pygame.sprite.Sprite):
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
		self.cooldown2 = 1

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.turretSprite = turretSprite
		self.add(self.turretSprite)

		self.projectiles = projectiles
		
		self.position = Vector2(self.hullPos)
		self.dir = Vector2(0, 1)
	
	def update(self):
		self.CooldownTimer()
		self.UpdatePosition()	
		self.Rotate()
		self.Fire()
		self.PlayerStats()

	def CooldownTimer(self):
		if self.cooldown < 7:
			self.cooldown += 1/60
		else:
			self.cooldown = 7

		if self.cooldown2 < 0.5:
			self.cooldown2 += 1/60
		else:
			self.cooldown2 = 0.5

	def UpdatePosition(self):
		self.position = self.hullPos
		self.rect.center = self.hull.rect.center

	def Rotate(self):
		x, y = pygame.mouse.get_pos()

		self.currentAngle = math.atan2((y - self.hullPos.y), (x - self.hullPos.x))
		self.currentAngle = math.degrees(self.currentAngle)

		self.image = pygame.transform.rotate(self.original_image, - self.currentAngle - 90)
		self.rect = self.image.get_rect(center=self.rect.center)

	def Fire(self):
		mouse_pressed = pygame.mouse.get_pressed()

		if(mouse_pressed[0] and self.cooldown == 7):
			self.cooldown = 0
			PlayerProjectile120mm(self.position, self.currentAngle, self.allSprites, self.projectiles)

		if(mouse_pressed[2] and self.cooldown2 == 0.5):
			self.cooldown2 = 0
			PlayerProjectile30mm(self.position, self.currentAngle, self.allSprites, self.projectiles)

	def PlayerStats(self):
		if(self.hull.alive() == False):
			self.kill()

	