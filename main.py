from kivy import platform
from kivy.config import Config

WIDTH = 1170
HEIGHT = 540
BLUE = (0.05, 0.3, 0.8, 1)

if platform == "android":
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.READ_EXTERNAL_STORAGE])
else:
    Config.set("graphics", "width", str(WIDTH))
    Config.set("graphics", "height", str(HEIGHT))

from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.properties import NumericProperty, BooleanProperty, Clock, StringProperty
from kivy.core.audio import SoundLoader
from kivy.graphics.context_instructions import PushMatrix, PopMatrix
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from random import choice, randint, random, randrange


class Main(RelativeLayout):
    FPS = 60
    timeCounter = 0
    timeCounterEnemy = 0
    difficultyCounter = 0
    animationCounter = 0

    animationX = NumericProperty(0.3)
    animationY = NumericProperty(0.4)
    ANIMATION_DURATION = 1.5
    FLASH_RATE = 0.12
    ANIMATION_MIN_X, ANIMATION_MAX_X = 0.2, 0.4
    ANIMATION_MIN_Y, ANIMATION_MAX_Y = 0.3, 0.5
    moveX = choice([-1, 1]) * randint(4, 10) / 200
    moveY = choice([-1, 1]) * randint(4, 10) / 200
    ANIMATION_UPDATE = 3  # How many seconds to generate random number
    ANIMATION_CHANCE = 0.7  # Chance of changing direction

    currentEvent = None
    previousEvent = None
    bgMusicEvent = None
    playingGame = False
    inPosition = False
    gifShown = False
    howToPlayMenu = False
    howToPlayReturn = False
    homeBtnDisabled = BooleanProperty(False)
    inGameBtnDisabled = BooleanProperty(True)

    FONT_SIZE = NumericProperty(Window.width * 0.032)

    planeHeight = NumericProperty(1)
    PLANE_WIDTH = 0.3
    PLANE_HEIGHT = 0.3 / 2.5

    PLANE_HOR_SPEED = 0.008
    PLANE_VER_SPEED = 0.01
    PLANE_ANGLE_SPEED = 0.1
    planeHorSpeed = PLANE_HOR_SPEED
    planeVerSpeed = PLANE_VER_SPEED
    angleSpeed = PLANE_ANGLE_SPEED

    PLANE_SENSITIVITY = 2
    planeRelX = NumericProperty(0.5)
    planeRelY = NumericProperty(Window.width * PLANE_HEIGHT / Window.height)
    planeAngle = NumericProperty(0)
    deckHeight = NumericProperty(0.1)
    endPlaneX = NumericProperty(0.2)

    SHOOT_DELAY = 0.2
    BULLET_SIZE = 0.06
    BULLET_SPEED = 0.2
    BULLET_UPTHRUST = 0.01
    shootCounter = 0
    planeShots = []

    propellerAngle = NumericProperty(0)
    propellerSpeed = 1
    PROPELLER_ACCELERATION = 0.001

    PILOT_HEIGHT = 0.7
    PILOT_JUMP_HEIGHT = 0.001
    PILOT_ITEM_AREA = 0.05
    getInPosition = False

    ITEM_CHANCE = 0.8
    itemSpawnRate = 4
    ITEM_SPAWN_RATE = 4
    increaseRate = 0.02
    itemMultiplier = -1
    rateOfChange = 0.005  # Linear increase every 10 secs
    itemMinSize = 0.17
    itemMaxSize = 0.27
    ITEM_X_RANGE = [i / 10 for i in range(1, 10, 1)]
    ITEM_Y_RANGE = [i / 10 for i in range(3, 10, 1)]
    itemList = []

    ENEMY_CHANCE = 0.8
    ENEMY_SHOOT_RATE = 3
    ENEMY_BULLET_SPEED = 0.03
    ENEMY_BULLET_SIZE = 0.04
    CLOUD_CHANCE = 0.7
    enemyList = []
    shotEnemies = []
    enemyBullets = []
    enemyMinSize = 0.10
    enemyMaxSize = 0.25

    JOURNEY_SIZE = 10000

    howToImagePath = StringProperty("images/howToPlayImageMobile.png")

    distanceTravelled = 0
    distanceText = StringProperty("Distance Travelled: 0 m")

    totalScore = 0
    scoreText = StringProperty("Score: 0")

    MAX_ALTITUDE = 1000
    altText = StringProperty("Altitude: 500 m")

    CLOUDS = {"images/cloud.png": 0.7, "images/thunderCloud.png": 0.1,
              "images/rainCloud.png": 0.1, "images/windCloud.png": 0.1}
    TOOLS = {"images/fuel.png": 0.5, "images/healthPack.png": 0.2,
             "images/tnt.png": 0.15, "images/bomb.png": 0.15}

    ITEM_CHOICES = [{"item": CLOUDS, "goodAudio": SoundLoader.load("audio/swoosh.ogg"),
                     "badAudio": SoundLoader.load("audio/zapOuch.ogg"),
                     "shotGoodAudio": SoundLoader.load("audio/notGood.ogg"),
                     "shotBadAudio": SoundLoader.load("audio/puff.ogg")},

                    {"item": TOOLS, "goodAudio": SoundLoader.load("audio/veryNice.ogg"),
                     "badAudio": SoundLoader.load("audio/explosionOuch.ogg"),
                     "shotGoodAudio": SoundLoader.load("audio/notGood.ogg"),
                     "shotBadAudio": SoundLoader.load("audio/explosion.ogg")}]

    ENEMY_CHOICES = [("images/enemyA10.png", "images/deadA10.png", True),
                     ("images/enemySpitfire.png", "images/deadSpitfire.png", True),
                     ("images/balloonRed.png", "images/balloonRedPop.png", False),
                     ("images/balloonYellow.png", "images/balloonYellowPop.png", False),
                     ("images/balloonGreen.png", "images/balloonGreenPop.png", False)]

    keyboard = None
    keys = []
    prevPosX = None
    prevPosY = None

    def __init__(self, **kwargs):
        super(Main, self).__init__(**kwargs)
        self.init_sound()
        self.mainTheme.play()

        if platform in ("win", "macosx", "linux"):  # If on PC
            self.howToImagePath = "images/howToPlayImagePC.png"

        self.currentEvent = Clock.schedule_interval(self.updateMenu, 1 / self.FPS)

    def init_sound(self):
        self.mainTheme = SoundLoader.load("audio/mainTheme.ogg")
        self.propellerStartUp = SoundLoader.load("audio/propellerStartUp.ogg")
        self.propellerStartUp.volume = 0.1
        self.propellerFlying = SoundLoader.load("audio/propellerFlying.ogg")
        self.propellerFlying.volume = 0.1
        self.startSound = SoundLoader.load("audio/start.ogg")
        self.shootSound = SoundLoader.load("audio/shoot.ogg")
        self.crashSound = SoundLoader.load("audio/crash.ogg")
        self.resultsTheme = SoundLoader.load("audio/results.ogg")
        self.resultsTheme.volume = 0.2
        self.winTheme = SoundLoader.load("audio/winTheme.ogg")
        self.enemyShot = SoundLoader.load("audio/enemyShot.ogg")
        self.planeFall = SoundLoader.load("audio/planeFall.ogg")
        self.planeFall.volume = 0.3
        self.bulletHit = SoundLoader.load("audio/bulletHit.ogg")
        self.balloonHit = SoundLoader.load("audio/pop.ogg")

    def updateMenu(self, dt):
        # Move plane
        if self.ANIMATION_MIN_X <= self.animationX + self.moveX <= self.ANIMATION_MAX_X:
            self.animationX += self.moveX * dt
        else:
            if self.animationX < self.ANIMATION_MIN_X:
                self.animationX = self.ANIMATION_MIN_X
            elif self.animationX > self.ANIMATION_MAX_X:
                self.animationX = self.ANIMATION_MAX_X

            self.moveX = choice([-1, 1]) * randint(4, 10) / 200

        if self.ANIMATION_MIN_Y <= self.animationY + self.moveY <= self.ANIMATION_MAX_Y:
            self.animationY += self.moveY * dt
        else:
            if self.animationY < self.ANIMATION_MIN_Y:
                self.animationY = self.ANIMATION_MIN_Y
            elif self.animationY > self.ANIMATION_MAX_Y:
                self.animationY = self.ANIMATION_MAX_Y

            self.moveY = choice([-1, 1]) * randint(4, 10) / 200

        if self.timeCounter >= self.ANIMATION_UPDATE:
            animationNo = str(randint(1, 3))
            self.ids.flyingPlane.source = "images/planeFront" + animationNo + ".png"
            if random() < self.ANIMATION_CHANCE:
                self.moveX = choice([-1, 1]) * randint(4, 10) / 200
                self.moveY = choice([-1, 1]) * randint(4, 10) / 200
            self.timeCounter = 0

        self.timeCounter += dt

    def moveToFront(self, widget, color=(1, 1, 1, 1)):
        self.remove_widget(widget)
        self.add_widget(widget)
        widget.color = color

    def playGame(self):
        self.homeBtnDisabled = True
        self.currentEvent.cancel()
        # Make widgets invisible
        self.timeCounter = 0
        for child in self.children:
            child.color = (0, 0, 0, 0)
            child.background_color = (0, 0, 0, 0)

        self.mainTheme.stop()

        # Create images
        self.moveToFront(self.ids.bg)
        self.moveToFront(self.ids.islandOutline, color=(1, 1, 1, 1))
        self.moveToFront(self.ids.island, color=(1, 1, 1, 0.2))
        self.moveToFront(self.ids.deck)
        self.moveToFront(self.ids.propeller)
        self.moveToFront(self.ids.planeSprite)

        self.pilot = Image(source="images/pilotWalk1.png", allow_stretch=True, size_hint=(1, None),
                           height=self.height * self.PILOT_HEIGHT, pos_hint={"center_x": 1, "center_y": 0.2})
        self.add_widget(self.pilot)

        self.inGameBtnDisabled = False
        self.ids.pauseImg.color = (1, 1, 1, 1)
        self.moveToFront(self.ids.pauseBtn)

        self.previousEvent = self.preFlyAnimation
        self.currentEvent = Clock.schedule_interval(self.previousEvent, 1 / self.FPS)

    def playFlyingSound(self, dt):
        self.propellerFlying.play()

    def preFlyAnimation(self, dt):
        self.timeCounter += dt
        # Spin propeller
        if 550 < self.propellerAngle < 600:
            # Play propeller sound
            self.propellerStartUp.play()

        if 0 <= self.propellerAngle < 3000:  # First Half

            angle = (self.PROPELLER_ACCELERATION * self.propellerAngle ** 2 + 100) * dt
            if angle < 1:
                angle = 1

            self.propellerSpeed = angle
            self.propellerAngle += self.propellerSpeed

            # Pilot walking animation
            if self.pilot.pos_hint["center_x"] > 0.52:
                self.pilot.pos_hint["center_x"] = 1 - self.timeCounter / 10
            else:
                self.propellerAngle = 3001

            self.pilot.height = self.height * (self.PILOT_HEIGHT - self.timeCounter / 15)
            animationNo = str(-(int(self.pilot.pos_hint["center_x"] * 10) % 2) + 2)
            self.pilot.source = "images/pilotWalk" + animationNo + ".png"
            jumpHeight = ((-2 * int(animationNo) + 3) * self.PILOT_JUMP_HEIGHT) * self.pilot.pos_hint["center_x"]
            self.pilot.pos_hint["center_y"] += jumpHeight

        elif self.propellerAngle >= 3000:  # Stop spinning
            self.propellerFlying.play()
            self.bgMusicEvent = Clock.schedule_interval(self.playFlyingSound, 10)
            self.ids.propeller.color = (0, 0, 0, 0)
            self.propellerAngle = -1
            self.remove_widget(self.pilot)
            self.ids.planeSprite.source = "images/behindFlying.png"
            self.getInPosition = True

        if self.getInPosition:
            # Once pilot is in plane
            if self.planeRelY < 0.5:
                self.planeRelY += 0.12 * dt
                self.deckHeight -= 0.24 * dt
                self.planeHeight -= 0.18 * dt
            else:
                if self.propellerAngle == -1:
                    # Show start on screen
                    self.moveToFront(self.ids.startImg)
                    self.startSound.play()
                    self.propellerAngle = -2
                    self.timeCounter = 0

                if self.timeCounter > 2:
                    # Start game
                    self.ids.startImg.color = (0, 0, 0, 0)
                    self.currentEvent.cancel()

                    if platform in ("win", "macosx", "linux"):  # If on PC
                        self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
                        self.keyboard.bind(on_key_down=self.on_keyboard_down)
                        self.keyboard.bind(on_key_up=self.on_keyboard_up)

                    self.playingGame = True
                    self.moveToFront(self.ids.distanceLabel, BLUE)
                    self.moveToFront(self.ids.scoreLabel, BLUE)
                    self.moveToFront(self.ids.altLabel, BLUE)
                    self.ids.deck.color = (0, 0, 0, 0)
                    self.ids.islandOutline.size_hint = (0.2, 0.2)
                    self.ids.island.size_hint = (0.2, 0.2)
                    self.moveToFront(self.ids.heightBar)
                    self.moveToFront(self.ids.arrowHead)
                    self.timeCounter = self.itemSpawnRate
                    self.previousEvent = self.mainGame
                    self.currentEvent = Clock.schedule_interval(self.previousEvent, 1 / self.FPS)

    def mainGame(self, dt):
        self.shootCounter -= dt
        self.timeCounter += dt
        self.timeCounterEnemy += dt
        self.difficultyCounter += dt
        self.animationCounter -= dt

        if ("left" in self.keys or "a" in self.keys) and self.planeRelX > self.PLANE_WIDTH / 4:
            self.planeRelX -= self.planeHorSpeed
            self.planeAngle -= self.angleSpeed

        if ("right" in self.keys or "d" in self.keys) and self.planeRelX < 1 - self.PLANE_WIDTH / 4:
            self.planeRelX += self.planeHorSpeed
            self.planeAngle += self.angleSpeed

        if ("up" in self.keys or "w" in self.keys) and self.planeRelY < 1 - self.PLANE_HEIGHT / 2:
            self.planeRelY += self.planeVerSpeed

        if ("down" in self.keys or "s" in self.keys) and self.planeRelY > self.PLANE_HEIGHT / 2:
            self.planeRelY -= self.planeVerSpeed

        if "spacebar" in self.keys and self.shootCounter <= 0:
            self.shootCounter = self.SHOOT_DELAY
            self.planeShoot()

        if self.timeCounter >= self.itemSpawnRate and random() < self.ITEM_CHANCE:
            self.spawnItem()
            self.timeCounter = 0

        if self.timeCounterEnemy >= self.itemSpawnRate and random() < self.ITEM_CHANCE:
            if random() < self.ENEMY_CHANCE and self.increaseRate >= 0.03:
                self.spawnEnemy()

            self.timeCounterEnemy = 0

        if self.difficultyCounter >= 10:
            self.increaseRate += self.rateOfChange
            self.itemSpawnRate = self.ITEM_SPAWN_RATE - self.increaseRate * 20
            if self.itemSpawnRate < 1:
                self.itemSpawnRate = 1
            self.difficultyCounter = 0

        fallRate = 0
        if self.animationCounter < 0:
            self.ids.planeSprite.source = "images/behindFlying.png"
            fallRate = self.increaseRate / 2 * dt
            self.planeHorSpeed = self.PLANE_HOR_SPEED
            self.planeVerSpeed = self.PLANE_VER_SPEED
            self.angleSpeed = self.PLANE_HOR_SPEED
            self.ids.planeSprite.color = (1, 1, 1, 1)
        else:
            if self.itemMultiplier == -1:
                fallRate = -self.increaseRate / 50 - dt / 25
            elif self.itemMultiplier == 1:
                fallRate = self.increaseRate * dt
            elif self.itemMultiplier == -2:
                fallRate = self.increaseRate / 2 * dt
                state = (self.animationCounter * 100) // (self.FLASH_RATE * 100) % 2
                if state == 0:
                    self.ids.planeSprite.source = "images/nothing.png"
                else:
                    self.ids.planeSprite.source = "images/behindFlying.png"

        if self.planeHeight + fallRate > 0:
            self.planeHeight += fallRate
        if self.planeHeight > 1:
            # Game over
            self.playingGame = False
            self.inPosition = False
            self.animationCounter = 0
            self.planeAngle = 0
            self.currentEvent.cancel()

            # Remove all items
            for item in self.itemList:
                self.itemList.remove(item)
                self.remove_widget(item[0])

            for item in self.enemyList:
                self.enemyList.remove(item)
                self.remove_widget(item[0])

            # Remove all bullets
            for bullet in self.planeShots:
                self.planeShots.remove(bullet)
                self.remove_widget(bullet)

            self.previousEvent = self.lossAnimation
            self.currentEvent = Clock.schedule_interval(self.previousEvent, 1 / self.FPS)

        alt = round((-self.planeHeight + 1) * self.MAX_ALTITUDE)

        if alt < 0:
            alt = 0
        elif alt >= self.MAX_ALTITUDE * 0.996:
            alt = self.MAX_ALTITUDE

        self.altText = "Altitude: " + str(alt) + " m"
        self.moveBullets(dt)
        self.moveEnemyBullets(dt, fallRate)
        self.moveItems(dt, fallRate)
        self.moveEnemies(dt, fallRate)
        self.enemyAnimation(dt, fallRate)
        self.updateDistance(dt)
        self.moveToFront(self.ids.planeSprite)

    def enemyAnimation(self, dt, fallRate):
        for e in self.shotEnemies:
            enemy = e[0]

            if e[4] is False:
                e[4] = dt

            if isinstance(e[4], float):
                e[4] += dt
                enemy.pos_hint["center_y"] += fallRate
                if e[4] > 2:
                    self.shotEnemies.remove(e)
                    self.remove_widget(enemy)

            else:
                enemy.pos_hint["center_y"] += (-0.5 - enemy.pos_hint["center_y"]) * dt * 0.5
                if enemy.pos_hint["center_y"] < -0.25:
                    self.shotEnemies.remove(e)
                    self.remove_widget(enemy)

    def spawnEnemy(self):
        itemSource, shotSource, doesShoot = choice(self.ENEMY_CHOICES)  # Selects item type

        xRange = self.ITEM_X_RANGE.copy()
        for x in xRange:
            if x < 0.3 or x > 0.7:
                xRange.remove(x)
        x = choice(xRange)
        self.ITEM_X_RANGE.remove(x)

        yRange = self.ITEM_Y_RANGE.copy()
        for y in yRange:
            if y < 0.4 or y > 0.8:
                yRange.remove(y)

        y = choice(self.ITEM_Y_RANGE)
        self.ITEM_Y_RANGE.remove(y)

        self.enemyList.append([Image(source=itemSource, allow_stretch=True, size_hint=(0.02, 0.02),
                                     color=(1, 1, 1, 0.5), pos_hint={"center_x": x, "center_y": y}),
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], shotSource, self.increaseRate * 50,
                               doesShoot])
        self.add_widget(self.enemyList[-1][0])

    def moveEnemyBullets(self, dt, fallRate):
        for bullet in self.enemyBullets:
            curSize = bullet.size_hint[0]
            bullet.size_hint = (curSize + self.ENEMY_BULLET_SPEED * dt, curSize + self.ENEMY_BULLET_SPEED * dt)
            bullet.pos_hint["center_y"] += fallRate
            x, y = bullet.pos_hint["center_x"] * self.width, bullet.pos_hint["center_y"] * self.height
            bulletHit = False

            minX = (self.planeRelX - self.PLANE_WIDTH / 2) * self.width
            minY = (self.planeRelY - self.PLANE_HEIGHT / 3) * self.height
            maxX = (self.planeRelX + self.PLANE_WIDTH / 2) * self.width
            maxY = (self.planeRelY + self.PLANE_HEIGHT / 3) * self.height

            if minX <= x <= maxX and minY <= y <= maxY:
                # Player Plane has been shot
                bulletHit = True
                self.enemyBullets.remove(bullet)
                self.remove_widget(bullet)
                self.itemMultiplier = -2
                self.animationCounter = self.ANIMATION_DURATION

                self.planeHorSpeed = self.PLANE_HOR_SPEED / 4
                self.planeVerSpeed = self.PLANE_VER_SPEED / 4
                self.angleSpeed = self.PLANE_HOR_SPEED / 4

                self.totalScore -= 50 * (1 + self.increaseRate)
                self.scoreText = "Score: " + str((int(self.totalScore) // 5) * 5)
                self.bulletHit.play()

            if curSize >= self.ENEMY_BULLET_SIZE and not bulletHit:
                self.enemyBullets.remove(bullet)
                self.remove_widget(bullet)

    def moveEnemies(self, dt, fallRate):
        for e in self.enemyList:
            item = e[0]
            w, h = item.size_hint
            if w > self.enemyMaxSize:
                self.enemyList.remove(e)
                self.remove_widget(item)
                self.ITEM_X_RANGE.append(item.pos_hint["center_x"])
                self.ITEM_Y_RANGE.append(item.pos_hint["center_y"])
            else:
                item.size_hint = (w + self.increaseRate * dt * 0.25, h + self.increaseRate * dt * 0.25)
                item.pos_hint["center_y"] += fallRate
                alpha = w / self.enemyMinSize / 1.5
                oldW = w

                if w > self.enemyMinSize:
                    alpha = 1

                item.color = (1, 1, 1, alpha)

                x, y = self.width * (item.pos_hint["center_x"] - w / 4), self.height * (
                            item.pos_hint["center_y"] - h / 2)
                w, h = self.width * w / 2, self.height * h
                e[1] = [x, y, x + w, y, x + w, y + h, x, y + h, x, y]

                e[3] += dt
                if e[3] > self.ENEMY_SHOOT_RATE and e[4]:
                    # Enemy shoots
                    self.enemyShot.play()
                    self.enemyBullets.append(Image(source="images/enemyBullet.png", allow_stretch=True,
                                                   size_hint=(0.01, 0.01),
                                                   pos_hint={"center_x": item.pos_hint["center_x"] + 0.33 * oldW,
                                                             "center_y": item.pos_hint["center_y"]}))
                    self.add_widget(self.enemyBullets[-1])
                    self.enemyBullets.append(Image(source="images/enemyBullet.png", allow_stretch=True,
                                                   size_hint=(0.01, 0.01),
                                                   pos_hint={"center_x": item.pos_hint["center_x"] - 0.33 * oldW,
                                                             "center_y": item.pos_hint["center_y"]}))
                    self.add_widget(self.enemyBullets[-1])
                    e[3] = 0

    def updateDistance(self, dt):
        self.distanceTravelled += dt * 10 * ((1 + self.increaseRate * 10) ** 2)
        if self.distanceTravelled > 1000:
            shownDistance = round(self.distanceTravelled / 1000, 1)
            unit = " km"
        else:
            shownDistance = int(self.distanceTravelled)
            unit = " m"

        alpha = self.distanceTravelled / self.JOURNEY_SIZE * 1.25 + 0.2
        self.ids.island.size_hint = (alpha, alpha)
        self.ids.islandOutline.size_hint = (alpha, alpha)
        self.ids.island.color = (1, 1, 1, alpha)
        self.distanceText = "Distance Travelled: " + str(shownDistance) + unit
        if self.distanceTravelled >= self.JOURNEY_SIZE:
            # Game won
            self.playingGame = False
            self.inPosition = False
            self.animationCounter = 0
            self.planeAngle = 0
            self.currentEvent.cancel()

            # Remove all items
            for item in self.itemList:
                self.itemList.remove(item)
                self.remove_widget(item[0])

            for item in self.enemyList:
                self.enemyList.remove(item)
                self.remove_widget(item[0])

            # Remove all bullets
            for bullet in self.planeShots:
                self.planeShots.remove(bullet)
                self.remove_widget(bullet)

            self.previousEvent = self.wonAnimation
            self.currentEvent = Clock.schedule_interval(self.previousEvent, 1 / self.FPS)

    def moveItems(self, dt, fallRate):
        for e in self.itemList:
            item = e[0]
            w, h = item.size_hint
            if w > self.itemMaxSize:
                self.itemList.remove(e)
                self.remove_widget(item)
                self.ITEM_X_RANGE.append(item.pos_hint["center_x"])
                self.ITEM_Y_RANGE.append(item.pos_hint["center_y"])
            else:
                item.size_hint = (w + self.increaseRate * dt, h + self.increaseRate * dt)
                item.pos_hint["center_y"] += fallRate
                alpha = w / self.itemMinSize / 1.5

                if w > self.itemMinSize:
                    alpha = 1

                item.color = (1, 1, 1, alpha)
                oldW = w

                x, y = self.width * (item.pos_hint["center_x"] - w / 4), self.height * (
                            item.pos_hint["center_y"] - h / 2)
                w, h = self.width * w / 2, self.height * h
                e[1] = [x, y, x + w, y, x + w, y + h, x, y + h, x, y]

                # Check if plane has collided into item
                x1, y1 = self.planeRelX * self.width, self.planeRelY * self.height
                t = self.PILOT_ITEM_AREA * self.height

                if (oldW > self.itemMinSize) and \
                        ((x < (x1 - t) < x + w) or (x < (x1 + t) < x + w)) and \
                        ((y < (y1 - t) < y + h) or (y < (y1 + t) < y + h)):
                    # Plane has collided
                    self.itemList.remove(e)
                    self.remove_widget(item)
                    self.ITEM_X_RANGE.append(item.pos_hint["center_x"])
                    self.ITEM_Y_RANGE.append(item.pos_hint["center_y"])
                    self.itemCollected(item.source, action="collided")

    def itemCollected(self, itemName, action):
        # Find item spawn rate
        itemGood = True
        index = 0
        itemInfo = [e["item"] for e in self.ITEM_CHOICES]
        for itemType in itemInfo:
            for item in itemType:
                if item == itemName:
                    index = itemInfo.index(itemType)
                    if action == "collided":
                        itemGood = itemType[item] >= 0.2
                    elif action == "shot":
                        itemGood = itemType[item] < 0.2
                    break
        # Show appropriate action depending on item collected
        itemAudios = self.ITEM_CHOICES[index]

        if itemGood:
            self.totalScore += 50 * (1 + self.increaseRate)
            self.ids.planeSprite.source = "images/behindGood.png"
            self.itemMultiplier = -1

            if action == "collided":
                itemAudios["goodAudio"].play()
            elif action == "shot":
                itemAudios["shotBadAudio"].play()
        else:
            self.totalScore -= 50 * (1 + self.increaseRate)
            self.ids.planeSprite.source = "images/behindBad.png"
            self.itemMultiplier = 1

            if action == "collided":
                itemAudios["badAudio"].play()
            elif action == "shot":
                itemAudios["shotGoodAudio"].play()

        self.animationCounter = self.ANIMATION_DURATION
        self.scoreText = "Score: " + str((int(self.totalScore) // 5) * 5)

    def spawnItem(self):
        if random() < self.CLOUD_CHANCE:
            itemType = self.CLOUDS  # Selects item type
        else:
            itemType = self.TOOLS

        selectList = []
        for item in itemType:
            for i in range(int(itemType[item] * 100)):
                selectList.append(item)

        itemSource = choice(selectList)  # Returns selected item
        x = choice(self.ITEM_X_RANGE)
        self.ITEM_X_RANGE.remove(x)

        y = choice(self.ITEM_Y_RANGE)
        self.ITEM_Y_RANGE.remove(y)

        self.itemList.append([Image(source=itemSource, allow_stretch=True, size_hint=(0.02, 0.02), color=(1, 1, 1, 0.5),
                                    pos_hint={"center_x": x, "center_y": y}), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        self.add_widget(self.itemList[-1][0])

    def planeShoot(self):
        self.shootSound.play()
        self.planeShots.append(Image(source="images/playerBullet.png", allow_stretch=True,
                                     size_hint=(self.BULLET_SIZE, self.BULLET_SIZE),
                                     pos_hint={"center_x": self.planeRelX, "center_y": self.planeRelY}))
        self.add_widget(self.planeShots[-1])

    def moveBullets(self, dt):
        for bullet in self.planeShots:
            curSize = bullet.size_hint[0]
            bullet.size_hint = (curSize - self.BULLET_SPEED * dt, curSize - self.BULLET_SPEED * dt)
            bullet.pos_hint["center_y"] += self.BULLET_UPTHRUST
            x, y = bullet.pos_hint["center_x"] * self.width, bullet.pos_hint["center_y"] * self.height
            bulletHit = False

            for e in self.itemList:
                minX, minY, maxX, maxY = e[1][0], e[1][1], e[1][4], e[1][5]

                if minX <= x <= maxX and minY <= y <= maxY:
                    bulletHit = True
                    self.planeShots.remove(bullet)
                    self.remove_widget(bullet)
                    self.itemList.remove(e)
                    self.remove_widget(e[0])
                    self.ITEM_X_RANGE.append(e[0].pos_hint["center_x"])
                    self.ITEM_Y_RANGE.append(e[0].pos_hint["center_y"])
                    self.itemCollected(e[0].source, "shot")

            for e in self.enemyList:
                minX, minY, maxX, maxY = e[1][0], e[1][1], e[1][4], e[1][5]

                if minX <= x <= maxX and minY <= y <= maxY:
                    bulletHit = True
                    self.planeShots.remove(bullet)
                    self.remove_widget(bullet)
                    self.enemyList.remove(e)
                    self.ITEM_X_RANGE.append(e[0].pos_hint["center_x"])
                    self.ITEM_Y_RANGE.append(e[0].pos_hint["center_y"])
                    e[0].source = e[2]
                    e[0].color = (1, 1, 1, 1)
                    self.totalScore += 200 * (1 + self.increaseRate)
                    self.scoreText = "Score: " + str((int(self.totalScore) // 5) * 5)
                    self.itemMultiplier = -1
                    self.animationCounter = self.ANIMATION_DURATION
                    self.shotEnemies.append(e)
                    if e[4]:
                        self.planeFall.play()
                    else:
                        self.balloonHit.play()

            if curSize <= 0 and not bulletHit:
                self.planeShots.remove(bullet)
                self.remove_widget(bullet)

    def wonAnimation(self, dt):
        if not self.inPosition:
            if 0.49 < self.planeRelX < 0.51 and 0.49 < self.planeRelY < 0.51 and 0.49 < self.planeHeight < 0.51:
                self.animationCounter += dt
                if self.animationCounter > 0.5:
                    self.inPosition = True
                    self.gifShown = False
                    self.animationCounter = 0
                    # Clear screen
                    self.propellerFlying.stop()
                    self.propellerStartUp.stop()

                    if self.bgMusicEvent:
                        self.bgMusicEvent.cancel()

                    for child in self.children:
                        child.color = (0, 0, 0, 0)
                        child.background_color = (0, 0, 0, 0)

                    self.moveToFront(self.ids.waterBG)
                    self.moveToFront(self.ids.bigPlane)
                    self.winTheme.play()
            else:
                # Move plane towards the centre
                self.planeRelX += (0.5 - self.planeRelX) * dt * 2
                self.planeRelY += (0.5 - self.planeRelY) * dt * 2
                self.planeHeight += (0.5 - self.planeHeight) * dt * 2
        else:
            if self.endPlaneX < 0.9:
                self.endPlaneX += dt * 0.1
                if self.endPlaneX > 0.4 and not self.gifShown:
                    self.gifShown = True
                    self.moveToFront(self.ids.youWinImg)
                if self.endPlaneX > 0.7 and self.gifShown:
                    self.ids.youWinImg.color = (0, 0, 0, 0)
            else:
                self.ids.bigPlane.color = (0, 0, 0, 0)
                # Show end screen
                self.showEndScreen()

    def lossAnimation(self, dt):
        self.animationCounter += dt
        if not self.inPosition:
            if 0.49 < self.planeRelX < 0.51 and self.planeRelY < self.PLANE_HEIGHT + 0.01:
                self.crashSound.play()
                self.inPosition = True
                self.ids.planeSprite.source = "images/behindEmpty.png"
                self.y = self.planeRelY + self.PLANE_HEIGHT
                self.pilot = Image(source="images/pilotFalling.png", allow_stretch=True, size_hint=(1, None),
                                   height=self.height * self.PILOT_HEIGHT * 0.8,
                                   pos_hint={"center_x": self.planeRelX, "center_y": self.y})
                self.add_widget(self.pilot)
            else:
                # Move plane towards the centre
                self.planeRelX += (0.5 - self.planeRelX) * dt * 4
                self.planeRelY += (self.PLANE_HEIGHT - self.planeRelY) * dt * 4
        else:
            # Move pilot upwards
            if self.y < 0.7 and self.pilot.source == "images/pilotFalling.png":
                self.remove_widget(self.pilot)
                self.y += dt * 0.5
                self.pilot = Image(source="images/pilotFalling.png", allow_stretch=True, size_hint=(1, None),
                                   height=self.height * self.PILOT_HEIGHT * 0.8,
                                   pos_hint={"center_x": self.planeRelX, "center_y": self.y})
                self.add_widget(self.pilot)
                self.animationCounter = 0
            elif self.animationCounter < 6:
                self.y -= dt * 0.03
                self.remove_widget(self.pilot)
                self.pilot = Image(source="images/pilotGliding.png", allow_stretch=True, size_hint=(1, None),
                                   height=self.height * self.PILOT_HEIGHT,
                                   pos_hint={"center_x": self.planeRelX, "center_y": self.y})
                self.add_widget(self.pilot)
                if self.animationCounter > 3:
                    self.moveToFront(self.ids.finishImg)
            else:
                # Clear screen
                self.propellerFlying.stop()
                self.propellerStartUp.stop()

                if self.bgMusicEvent:
                    self.bgMusicEvent.cancel()

                self.showEndScreen()

                self.resultsTheme.play()

    def showEndScreen(self):
        for child in self.children:
            child.color = (0, 0, 0, 0)
            child.background_color = (0, 0, 0, 0)

        self.moveToFront(self.ids.homeBG)

        with self.canvas:
            Color(0.9, 0.9, 0.9, 0.6)
            self.grayOut = Rectangle(pos=(0, 0), size=(self.width, self.height))

        self.add_widget(Label(text="Game Summary", font_size=self.FONT_SIZE * 2,
                              font_name="fonts/LeagueSpartan-Bold.otf", color=BLUE,
                              pos_hint={"center_x": 0.5, "center_y": 0.87}, size_hint=(0.2, 0.12)))

        self.distanceTravelled = round(self.distanceTravelled / 1000, 1)
        distance = "Distance Travelled: " + str(self.distanceTravelled) + " km"
        self.add_widget(Label(text=distance, font_size=self.FONT_SIZE,
                              font_name="fonts/Sackers-Gothic-Std-Light.ttf", color=BLUE,
                              pos_hint={"center_x": 0.5, "center_y": 0.7}, size_hint=(0.2, 0.12)))

        self.totalScore = (int(self.totalScore) // 5) * 5
        score = "Score: " + str(self.totalScore)
        self.add_widget(Label(text=score, font_size=self.FONT_SIZE,
                              font_name="fonts/Sackers-Gothic-Std-Light.ttf", color=BLUE,
                              pos_hint={"center_x": 0.5, "center_y": 0.58}, size_hint=(0.2, 0.12)))

        bonusPoints = int(self.distanceTravelled * self.totalScore)
        if bonusPoints < 0:
            bonusPoints = 0
        self.add_widget(Label(text="Bonus Points: " + str(bonusPoints), font_size=self.FONT_SIZE,
                              font_name="fonts/Sackers-Gothic-Std-Light.ttf", color=BLUE,
                              pos_hint={"center_x": 0.5, "center_y": 0.46}, size_hint=(0.2, 0.12)))

        self.totalScore += bonusPoints
        self.add_widget(Label(text="Total Score: " + str(self.totalScore), font_size=self.FONT_SIZE,
                              font_name="fonts/Sackers-Gothic-Std-Light.ttf", color=BLUE,
                              pos_hint={"center_x": 0.5, "center_y": 0.34}, size_hint=(0.2, 0.12)))

        self.add_widget(Button(text="Play Again", font_size=self.FONT_SIZE * 0.8,
                               font_name="fonts/LeagueSpartan-Bold.otf", background_normal="",
                               background_color=BLUE, on_press=self.restartGame,
                               pos_hint={"center_x": 0.3, "center_y": 0.15}, size_hint=(0.3, 0.12)))

        self.add_widget(Button(text="Return to Menu", font_size=self.FONT_SIZE * 0.8,
                               font_name="fonts/LeagueSpartan-Bold.otf", background_normal="",
                               background_color=BLUE, on_press=self.quitGame,
                               pos_hint={"center_x": 0.7, "center_y": 0.15}, size_hint=(0.3, 0.12)))

        self.currentEvent.cancel()

    def resetValues(self):
        # Reset values
        self.homeBtnDisabled = False
        self.animationCounter = 0
        self.timeCounter = 0
        self.timeCounterEnemy = 0
        self.propellerAngle = 0
        self.planeRelY = (Window.width * self.PLANE_HEIGHT) / Window.height
        self.deckHeight = 0.1
        self.planeHeight = 1
        self.getInPosition = False
        self.ids.planeSprite.source = "images/behindEmpty.png"
        self.planeRelX = 0.5
        self.planeAngle = 0
        self.planeHorSpeed = self.PLANE_HOR_SPEED
        self.planeVerSpeed = self.PLANE_VER_SPEED
        self.angleSpeed = self.PLANE_HOR_SPEED
        self.increaseRate = 0.02
        self.distanceTravelled = 0
        self.ids.islandOutline.size_hint = (0.2, 0.2)
        self.ids.island.size_hint = (0.2, 0.2)
        self.JOURNEY_SIZE = 10000
        self.distanceTravelled = 0

    def restartGame(self, *args):
        for child in self.children:
            try:
                child.text
            except AttributeError:
                pass
            else:
                if child.text in ["Play Again", "Return to Menu"]:
                    child.disabled = True

        self.resultsTheme.stop()
        self.winTheme.stop()
        self.resetValues()
        self.playGame()

    def on_touch_down(self, touch):
        if self.playingGame:
            if touch.spos[0] > 0.6:
                self.keys.append("spacebar")
            elif touch.spos[0] < 0.4:
                self.keys.append("arrows")
        return super(Main, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.playingGame:
            if "spacebar" in self.keys:
                self.keys.remove("spacebar")
            if "arrows" in self.keys:
                self.keys.remove("arrows")
            self.prevPosX = None
            self.prevPosY = None

        if self.howToPlayReturn:
            self.ids.howToBG.color = (0, 0, 0, 0)
            self.howToPlayMenu = False
            self.howToPlayReturn = False
            self.homeBtnDisabled = False

        if self.howToPlayMenu:
            self.howToPlayReturn = True

    def on_touch_move(self, touch):
        if self.playingGame and "arrows" in self.keys and touch.spos[0] < 0.4:
            if self.prevPosX and self.prevPosY:

                dX = touch.spos[0] - self.prevPosX
                dY = touch.spos[1] - self.prevPosY

                if (self.PLANE_WIDTH / 4) < (self.planeRelX + dX * self.PLANE_SENSITIVITY) < (1 - self.PLANE_WIDTH / 4):
                    self.planeRelX += dX * self.PLANE_SENSITIVITY * (self.planeHorSpeed / self.PLANE_HOR_SPEED)
                    self.planeAngle += dX * self.PLANE_SENSITIVITY * 20 * (self.angleSpeed / self.PLANE_ANGLE_SPEED)

                if (self.PLANE_HEIGHT / 2) < (self.planeRelY + dY * self.PLANE_SENSITIVITY) < (
                        1 - self.PLANE_HEIGHT / 2):
                    self.planeRelY += dY * self.PLANE_SENSITIVITY * (self.planeVerSpeed / self.PLANE_VER_SPEED)

                self.prevPosX = touch.spos[0]
                self.prevPosY = touch.spos[1]

            else:
                self.prevPosX = touch.spos[0]
                self.prevPosY = touch.spos[1]

    def pauseGame(self):
        self.inGameBtnDisabled = True
        self.keys = []
        self.ids.pauseImg.color = (0, 0, 0, 0)
        self.currentEvent.cancel()
        self.playingGame = False

        with self.canvas:
            Color(0.5, 0.5, 0.5, 0.7)
            self.grayOut = Rectangle(pos=(0, 0), size=(self.width, self.height))

        self.pauseLabel = Label(text="Game  Paused", font_size=self.FONT_SIZE * 2,
                                font_name="fonts/Sackers-Gothic-Std-Light.ttf", color=(0.05, 0.3, 0.8, 1),
                                pos_hint={"center_x": 0.5, "center_y": 0.7}, size_hint=(0.2, 0.12))
        self.add_widget(self.pauseLabel)

        self.resumeBtn = Button(text="Resume", font_size=self.FONT_SIZE * 0.8, font_name="fonts/LeagueSpartan-Bold.otf",
                                background_normal="", background_color=(0.05, 0.3, 0.8, 1), on_press=self.unPauseGame,
                                pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint=(0.2, 0.12))
        self.add_widget(self.resumeBtn)

        self.quitBtn = Button(text="Quit", font_size=self.FONT_SIZE * 0.8, font_name="fonts/LeagueSpartan-Bold.otf",
                              background_normal="", background_color=(0.05, 0.3, 0.8, 1), on_press=self.quitGame,
                              pos_hint={"center_x": 0.5, "center_y": 0.32}, size_hint=(0.2, 0.12))
        self.add_widget(self.quitBtn)

    def unPauseGame(self, *args):
        self.canvas.remove(self.grayOut)
        for widget in [self.pauseLabel, self.resumeBtn, self.quitBtn]:
            self.remove_widget(widget)

        self.inGameBtnDisabled = False
        self.playingGame = True
        self.ids.pauseImg.color = (1, 1, 1, 1)

        self.currentEvent = Clock.schedule_interval(self.previousEvent, 1 / self.FPS)

    def quitGame(self, *args):
        self.propellerFlying.stop()
        self.propellerStartUp.stop()
        self.resultsTheme.stop()
        self.winTheme.stop()

        if self.bgMusicEvent:
            self.bgMusicEvent.cancel()

        for child in self.children:
            child.color = (0, 0, 0, 0)
            child.background_color = (0, 0, 0, 0)
            try:
                child.text
            except AttributeError:
                pass
            else:
                if child.text in ["Play Again", "Return to Menu"]:
                    child.disabled = True

        for widget in [self.ids.homeBG, self.ids.title, self.ids.subTitle,
                       self.ids.playBtn, self.ids.infoBtn, self.ids.flyingPlane]:
            self.moveToFront(widget)

        self.ids.title.color = BLUE
        self.ids.subTitle.color = BLUE
        self.ids.playBtn.background_color = BLUE
        self.ids.infoBtn.background_color = BLUE

        self.resetValues()

        self.mainTheme.play()
        self.currentEvent = Clock.schedule_interval(self.updateMenu, 1 / self.FPS)

    def keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard.unbind(on_key_dup=self.on_keyboard_up)
        self.keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] not in self.keys:
            self.keys.append(keycode[1])

        return True

    def on_keyboard_up(self, keyboard, keycode):
        if keycode[1] in self.keys:
            self.keys.remove(keycode[1])

        return True

    def howToPlay(self):
        self.howToPlayMenu = True
        self.homeBtnDisabled = True
        self.moveToFront(self.ids.howToBG)


class PlaneManiaApp(App):
    def build(self):
        return Main()


PlaneManiaApp().run()
