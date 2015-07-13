from itertools import cycle
import pygame
import random
import sys

from pygame.locals import *

FPS = 30
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

NAME = "Final Project"

# Image paths
SPRITE_ROOT = 'assets/sprites/'

START_SCREEN = SPRITE_ROOT + 'start.png'
GAME_OVER = SPRITE_ROOT + 'game-over.png'
BACKGROUND = SPRITE_ROOT + 'background.png'
BASE = SPRITE_ROOT + 'base.png'
PIPE = SPRITE_ROOT + 'pipe-green.png'

CHARACTER = SPRITE_ROOT + "brick_Anja.png"
DEAD_CHARACTER = SPRITE_ROOT + 'brick_weiss.png'

BASEY = SCREEN_HEIGHT * 0.8

# list of all possible players (tuple of 3 positions of flap)
BIRDS = (
    # red bird
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        # amount by which base can maximum shift to left
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
)

def checkCaught(character, birds):

    birdHitMask = HITMASKS['birds']

    character['w'] = IMAGES['character'].get_width()
    character['h'] = IMAGES['character'].get_height()

    playerRect = pygame.Rect(character['x'], character['y'],
                             character['w'], character['h'])

    count = 0

    for bird in birds:

        birdW = IMAGES['birds'][bird['type']][0].get_width()
        birdH = IMAGES['birds'][bird['type']][0].get_height()

        # item rects
        piperect = pygame.Rect(bird['x'], bird['y'], birdW, birdH)

        # player and upper/lower pipe hitmasks
        characterHitMask = HITMASKS['character']

        collide = pixelCollision(playerRect, piperect, characterHitMask, birdHitMask[0])

        if collide:
            birds.pop(count)
            count += 1


    return {"points": count, "birds": birds}


def checkCrash(character, pipes):
    """returns True if player collders with base or pipes."""
    pipeW = IMAGES['pipe'][0].get_width()
    pipeH = IMAGES['pipe'][0].get_height()

    pipeHitMask = HITMASKS['pipe']

    return checkCrashAll(character, pipeH, pipeW, pipes, pipeHitMask)


def checkCrashAll(character, pipeH, pipeW, list, targetHitMask):
    character['w'] = IMAGES['character'].get_width()
    character['h'] = IMAGES['character'].get_height()

    playerRect = pygame.Rect(character['x'], character['y'],
                             character['w'], character['h'])

    for item in list:
        # item rects
        piperect = pygame.Rect(item['x'], item['y'], pipeW, pipeH)

        # player and upper/lower pipe hitmasks
        characterHitMask = HITMASKS['character']

        collide = pixelCollision(playerRect, piperect, characterHitMask, targetHitMask)

        if collide:
            return True
    return False


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(int(BASEY * 0.5), int(BASEY * 0.8))

    pipeX = SCREEN_WIDTH - 10

    return [{'x': pipeX, 'y': gapY}] # lower pipe

def showScore(score):
    """
    displays score at the to right corner of screen
    """
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = SCREEN_WIDTH * 0.9

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREEN_HEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def getRandomBird():
    print("get random bird")

    birdX = SCREEN_WIDTH - 20
    birdY = random.randrange(int(BASEY * 0.2), int(BASEY * 0.9))

    birdType = random.randrange(0, 3)

    return {'x': birdX, 'y': birdY, 'type': birdType}


def gameloop():
    print("game started")

    # let the bird flap
    idxGen = cycle([0, 1, 2, 1])
    loopIter = 0

    # the character must be standing on the base
    minCharY =  BASEY - IMAGES['character'].get_height()

    # position character in the middle of the screen above the base
    charX = (SCREEN_WIDTH - IMAGES['character'].get_width())/2
    charY = minCharY

    # inital base position x
    basex = 0

    # The base image is a little bit wider than the background image.
    # Calculate the difference in width.
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to pipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of pipes
    pipes = [
        {'x': SCREEN_WIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of birds
    birds = []

    # the speed at which the pipe wanders to the left side
    pipeVelX = -20

    # the speed at which the bird wanders to left side
    birdVelX = -10

    SCREEN.blit(IMAGES['character'], (charX, charY))

    # gravity and up velocity when player is jumping
    gravity = 9.81   # the gravity
    upVel = 0         # the velocity when player is jumping
    jump = False      # True when character jumps

    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # only jump when standing
                if not jump:
                    jump = True

                    # since screen coordinates origin at the top left corner
                    # we actually need a negative velocity to move upwards
                    upVel = -105

        # birdIdx basex change
        if (loopIter + 1) % 3 == 0:
            birdIdx = idxGen.next()
        loopIter = (loopIter + 1) % 30

        # check for crash here
        crashed = checkCrash({'x': charX, 'y': charY}, pipes)

        # check catch bird
        info = checkCaught({'x': charX, 'y': charY}, birds)

        birds = info['birds']

        if info['points'] > 0:
            score += info['points']

        # game over if crashed
        if crashed:
            return charY

        # shift base
        basex = -((-basex + 100) % baseShift)

        # character's movements
        if jump:
            upVel += gravity    # Reduce the up velocity by gravity amount until we reach the ground again

        charY += upVel

        # if our character is below the base, move him back up
        if charY > minCharY:
            charY = minCharY
            jump = False
            upVel = 0

        # move pipes to left
        for pipe in pipes:
            pipe['x'] += pipeVelX

        # move birds to left
        for bird in birds:
            bird['x'] += birdVelX

        # add random birds
        rand = random.random()
        if rand > 0.992:
            newBird = getRandomBird()
            birds.append(newBird)

        # add new pipe when first pipe is about to touch left of screen
        if len(pipes) == 0 or  0 < pipes[0]['x'] < 50:
            rand = random.random()
            if rand > 0.95:
                newPipe = getRandomPipe()
                pipes.append(newPipe[0])

        # remove first pipe if its out of the screen
        if len(pipes) and pipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            pipes.pop(0)

        # repaint the background
        SCREEN.blit(IMAGES['background'], (0, 0))

        for pipe in pipes:
            SCREEN.blit(IMAGES['pipe'][1], (pipe['x'], pipe['y']))

        for bird in birds:
            i = random.randrange(0, 3)
            SCREEN.blit(IMAGES['birds'][bird['type']][birdIdx], (bird['x'], bird['y']))

        SCREEN.blit(IMAGES['base'], (-basex, BASEY))

        # draw the score
        showScore(score)

        SCREEN.blit(IMAGES['character'], (charX, charY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def showStartScreen():
    print("show start screen")

    SCREEN.blit(IMAGES['start screen'], (0, 0))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return


def showGameOver(charY):
    upVel = -100
    gravity = 9.81   # the gravity
    rotation = 0

    scale = 0
    maxX, maxY = (IMAGES['game over'].get_width(), IMAGES['game over'].get_height())

    animDone = False

    # ratio to scale text proportionally
    ratio = maxX / maxY

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                main()

        # Animation finished when game over text is fully scaled and character disappears at the bottom
        if scale >= maxX and charY > SCREEN_HEIGHT:
            animDone = True

        if not animDone:
            upVel += gravity
            rotation += 10

            charX = (SCREEN_WIDTH - IMAGES['dead character'].get_width())/2
            charY += upVel

            dead = pygame.transform.rotate(IMAGES['dead character'], rotation)

            # position game over text in the mid and scaling in
            scale = min (scale + 40, maxX)


            game_over_text = pygame.transform.scale(IMAGES['game over'], (scale, scale * ratio))
            goX = (SCREEN_WIDTH - IMAGES['game over'].get_width()) / 2
            goY = 30

            # repaint the background
            SCREEN.blit(IMAGES['background'], (0, 0))
            SCREEN.blit(IMAGES['base'], (0, BASEY))

            SCREEN.blit(dead, (charX, charY))

            SCREEN.blit(game_over_text, (goX, goY))

            pygame.display.update()
            FPSCLOCK.tick(FPS)




def main():
    global SCREEN, FPSCLOCK
    pygame.init()

    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(NAME)

    IMAGES['start screen'] = pygame.image.load(START_SCREEN)
    IMAGES['game over'] = pygame.image.load(GAME_OVER)
    IMAGES['background'] = pygame.image.load(BACKGROUND)
    IMAGES['base'] = pygame.transform.scale(pygame.image.load(BASE), (1400, 160))
    IMAGES['character'] = pygame.transform.scale(pygame.image.load(CHARACTER), (130, 130))
    IMAGES['dead character'] = pygame.transform.scale(pygame.image.load(DEAD_CHARACTER), (130, 130))

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    # select random player sprites
    IMAGES['birds'] = [
        (
            pygame.transform.scale(pygame.image.load(BIRDS[0][0]).convert_alpha(), (126, 91)),
            pygame.transform.scale(pygame.image.load(BIRDS[0][1]).convert_alpha(), (126, 91)),
            pygame.transform.scale(pygame.image.load(BIRDS[0][2]).convert_alpha(), (126, 91)),
        ),
        (
            pygame.transform.scale(pygame.image.load(BIRDS[1][0]).convert_alpha(), (108, 78)),
            pygame.transform.scale(pygame.image.load(BIRDS[1][1]).convert_alpha(), (108, 78)),
            pygame.transform.scale(pygame.image.load(BIRDS[1][2]).convert_alpha(), (108, 78)),
        ),
        (
            pygame.transform.scale(pygame.image.load(BIRDS[2][0]).convert_alpha(), (72, 52)),
            pygame.transform.scale(pygame.image.load(BIRDS[2][1]).convert_alpha(), (72, 52)),
            pygame.transform.scale(pygame.image.load(BIRDS[2][2]).convert_alpha(), (72, 52)),
        )
    ]

    # select random pipe sprites
    IMAGES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.transform.scale(pygame.image.load(PIPE).convert_alpha(), (100, 400))
    )

    # hitmask for pipes
    HITMASKS['pipe'] = getHitmask(IMAGES['pipe'][1])


    # hitmask for player
    HITMASKS['character'] = getHitmask(IMAGES['character'])

    # hitmask for player
    HITMASKS['birds'] = (
        getHitmask(IMAGES['birds'][0][0]),
        getHitmask(IMAGES['birds'][1][0]),
        getHitmask(IMAGES['birds'][2][0]),
    )


    showStartScreen()
    charY = gameloop()
    showGameOver(charY)



if __name__ == "__main__":
    main();
