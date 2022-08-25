import pygame
from pygame.math import Vector2
import random
import math

class EnemyHealthSprite(pygame.sprite.Sprite):
	def __init__(self, enemy, sprite):
		super().__init__()

		self.enemy = enemy
		self.enemyPos = self.enemy.position

		self.image = pygame.Surface((10,10), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/healthBar.png")

		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.enemyPos)		

		self.sprite = sprite
		self.add(self.sprite)

		self.position = Vector2(self.enemyPos.x, self.enemyPos.y + 30)

	def update(self):
		self.health = self.enemy.health

		self.position = Vector2(self.enemyPos.x, self.enemyPos.y + 30)
		self.rect.center = self.position

		self.image = pygame.transform.scale(self.original_image, (self.health, 10))
		self.rect = self.image.get_rect(center=self.rect.center)

		if(self.enemy.alive() == False):
			self.kill()

class EnemyProjectile(pygame.sprite.Sprite):
	def __init__(self, startPos, angle, allSprites, projectiles):
		super().__init__()
		self.image = pygame.Surface((10,10), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/projectile.png")
		
		self.shootSound = pygame.mixer.Sound("Sfx/enemyShot.wav")
		self.shootSound.set_volume(0.3)
		self.shootChannel = pygame.mixer.Channel(4)

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
			self.shootChannel.play(self.shootSound)
			self.hasFired = False
		
		self.range -= 1/60

		self.position += self.direction * self.velocity
		self.rect.center = self.position

		if(self.range <= 0):
			self.kill()	

class Enemy(pygame.sprite.Sprite):
	def __init__(self, pos, newPos, player, allSprites, enemies):
		super().__init__()	

		self.player = player

		self.image = pygame.Surface((50,50), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/enemyTankHull.png")

		self.idleSound = pygame.mixer.Sound("Sfx/tankIdle.wav")
		self.moveSound = pygame.mixer.Sound("Sfx/tankMove.wav")

		self.idleSound.set_volume(0.3)
		self.moveSound.set_volume(0.3)

		self.idleChannel = pygame.mixer.Channel(5)
		self.moveChannel = pygame.mixer.Channel(6)

		self.original_image = self.image
		self.rect = self.image.get_rect(center=pos)

		self.health = 100
		self.movementSpeed = 2
		self.rotationSpeed = 0
		self.isColliding = False

		self.position = Vector2(pos)
		self.newPosition = Vector2(newPos)
		
		self.currentAngle = math.atan2((self.newPosition.y - self.position.y), (self.newPosition.x - self.position.x))
		self.currentAngle = math.degrees(self.currentAngle)
		self.currentAngle += 180

		self.dir = Vector2(0, -1)
		self.dir.rotate_ip(self.currentAngle - 90)

		self.allSprites = allSprites
		self.add(self.allSprites)

		self.enemies = enemies
		self.add(self.enemies)


	def update(self):
		self.Movement()
		self.PlaySound()
		self.EnemyStats()

	def Movement(self):
		distance = math.hypot(self.newPosition.x - self.position.x, self.newPosition.y - self.position.y)
		
		self.AdjustAngle()

		self.targetAngle = math.atan2((self.newPosition.y - self.position.y), (self.newPosition.x - self.position.x))
		self.targetAngle = math.degrees(self.targetAngle)
		self.targetAngle += 180

		if(self.player.health > 0):
			#Step 1: Rotate to face the new position
			if(distance > 10 and abs(self.currentAngle - self.targetAngle) >= 1):
				if(self.currentAngle - self.targetAngle <= 0 and self.currentAngle - self.targetAngle > -180):
					self.rotationSpeed = 2
				else:
					self.rotationSpeed = -2

				self.currentAngle += self.rotationSpeed

			#Step 2: Move to new position
			elif(distance > 10 and abs(self.currentAngle - self.targetAngle) < 1):
				self.movementSpeed = 2

				self.dir = Vector2(0, -1)
				self.dir.rotate_ip(self.targetAngle - 90)			

				self.position += self.dir * self.movementSpeed
				self.rect.center = self.position

			#Step 3: Stop
			elif(distance <= 10 or not self.isColliding):
				x = random.randint(0, 800)
				y = random.randint(0, 600)

				self.newPosition = Vector2(x,y)

		self.image = pygame.transform.rotate(self.original_image, -self.currentAngle + 90)
		self.rect = self.image.get_rect(center=self.rect.center)

	#Adjust angle to be min 0 and max 360			
	def AdjustAngle(self):
		if(self.currentAngle >= 360):	
			self.currentAngle = 0
		elif(self.currentAngle < 0):
			self.currentAngle = 360

	def PlaySound(self):
		if(self.movementSpeed == 0):
			self.moveChannel.stop()
			self.idleChannel.queue(self.idleSound)	
		else:
			self.idleChannel.stop()
			self.moveChannel.queue(self.moveSound)

	def EnemyStats(self):
		if(self.health <= 0):
			self.health = 0

			self.idleChannel.stop()
			self.moveChannel.stop()
			self.kill()


class EnemyTurret(pygame.sprite.Sprite):
	def __init__(self, enemy, player, fireTiming, allSprites, turretSprite, projectiles):
		super().__init__()	
		self.hull = enemy
		self.hullPos = enemy.position

		self.player = player
		self.playerPos = player.position

		self.image = pygame.Surface((75,75), pygame.SRCALPHA)
		self.image = pygame.image.load("Images/enemyTankTurret.png")

		self.original_image = self.image
		self.rect = self.image.get_rect(center=self.hullPos)

		self.currentAngle = 0
		self.cooldown = 7
		self.fireTiming = fireTiming
		self.timer = 0
		self.doReload = False

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
		self.EnemyTurretStats()

	def CooldownTimer(self):
		self.cooldown += 1/60

		if (self.cooldown > 7):
			self.cooldown = 0
			self.doReload = False

	def UpdatePosition(self):
		self.position = self.hullPos
		self.rect.center = self.position

	def Rotate(self):
		x, y = self.playerPos

		self.currentAngle = math.atan2((y - self.hullPos.y), (x - self.hullPos.x))
		self.currentAngle = math.degrees(self.currentAngle)

		self.image = pygame.transform.rotate(self.original_image, - self.currentAngle - 90)
		self.rect = self.image.get_rect(center=self.rect.center)

	def Fire(self):
		if(self.doReload == False and int(self.cooldown) == self.fireTiming and self.player.health > 0):
			self.doReload = True
			EnemyProjectile(self.position, self.currentAngle, self.allSprites, self.projectiles)

	def EnemyTurretStats(self):
		if(self.hull.alive() == False):
			self.kill()