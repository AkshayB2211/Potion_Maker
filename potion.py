
import random, time, pygame, sys, copy
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 600       # width of the program's window, in pixels
WINDOWHEIGHT = 600      # height in pixels

BOARDWIDTH = 6          # how many columns in the board
BOARDHEIGHT = 6         # how many rows in the board
GEMIMAGESIZE = 64       # width & height of each space in pixels

NUMGEMIMAGES = 7
GEMOFFSET = 3

# NUMMATCHSOUNDS is the number of different sounds to choose from when
# a match is made. The .wav files are named match0.wav, match1.wav, etc.
NUMMATCHSOUNDS = 6

MOVERATE = 25 # 1 to 100, larger num means faster animations
DEDUCTSPEED = 0.8 # reduces score by 1 point every DEDUCTSPEED seconds.

EMPTY_SPACE = -1        # an arbitrary, nonpositive value
ROWABOVEBOARD = 'row above board' # an arbitrary, noninteger value

# constants for direction values
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

PURPLE    = (255,   0, 255)
LIGHTBLUE = (170, 190, 255)
BLUE      = (  0,   0, 255)
RED       = (255, 100, 100)
BLACK     = (  0,   0,   0)
BROWN     = ( 85,  65,   0)
HIGHLIGHTCOLOR = PURPLE         # color of the selected gem's border
BGCOLOR = LIGHTBLUE             # background color on the screen
GRIDCOLOR = BLUE                # color of the game board
GAMEOVERCOLOR = RED             # color of the "Game over" text.
GAMEOVERBGCOLOR = BLACK         # background color of the "Game over" text.
SCORECOLOR = BROWN              # color of the text for the player's score

XMARGIN = int((WINDOWWIDTH - GEMIMAGESIZE * BOARDWIDTH) / 2)
YMARGIN = int((WINDOWHEIGHT - GEMIMAGESIZE * BOARDHEIGHT) / 2)

def main():
	global FPSCLOCK, DISPLAYSURF, GEMIMAGES, GAMESOUNDS, BASICFONT, BOARDRECTS, LISTRECTS

	# Initial set up.
	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	pygame.display.set_caption('Potion Maker')
	BASICFONT = pygame.font.Font('freesansbold.ttf', 36)

	# Load the images
	GEMIMAGES = []
	for i in range(1, NUMGEMIMAGES+1):
		gemImage = pygame.image.load('gem%s.png' % i)
		if gemImage.get_size() != (GEMIMAGESIZE, GEMIMAGESIZE):
			gemImage = pygame.transform.smoothscale(gemImage, (GEMIMAGESIZE, GEMIMAGESIZE))
		GEMIMAGES.append(gemImage)

	# Load the sounds.
	GAMESOUNDS = {}
	GAMESOUNDS['bad swap'] = pygame.mixer.Sound('badswap.wav')
	GAMESOUNDS['match'] = []
	for i in range(NUMMATCHSOUNDS):
		GAMESOUNDS['match'].append(pygame.mixer.Sound('match%s.wav' % i))

	# Create pygame.Rect objects for each board space to
	# do board-coordinate-to-pixel-coordinate conversions.
	BOARDRECTS = []
	for x in range(BOARDWIDTH):
		BOARDRECTS.append([])
		for y in range(BOARDHEIGHT):
			r = pygame.Rect((XMARGIN + (x * GEMIMAGESIZE),
							 YMARGIN + (y * GEMIMAGESIZE),
							 GEMIMAGESIZE,
							 GEMIMAGESIZE))
			BOARDRECTS[x].append(r)

	LISTRECTS = []
	for i in range(NUMGEMIMAGES):
		offset  = WINDOWWIDTH / 2  -  NUMGEMIMAGES * GEMIMAGESIZE / 2
		r = pygame.Rect(offset + i*GEMIMAGESIZE, WINDOWHEIGHT-GEMIMAGESIZE-4,
						GEMIMAGESIZE, GEMIMAGESIZE)
		LISTRECTS.append(r)

	while True:
		runGame()


def runGame():
	# initalize the board
	gameBoard = getShuffledBoard()

	# initialize variables for the start of a new game
	firstSelectedGem = None
	lastMouseDownX = None
	lastMouseDownY = None
	prevGemPos = None
	boardX = None
	boardY = None
	selected = []
	gameIsOver = False

	while True:
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
				
			elif event.type == MOUSEBUTTONUP:
				firstSelectedGem = None
				#print(selected)
				removeGems(gameBoard, selected)
				selected = []
				prevGemPos = None
				
			elif event.type == MOUSEBUTTONDOWN:
				p = checkForGemClick(event.pos)
				if(p != None):
					prevGemPos = p
					selected.append(p)
					firstSelectedGem = getGemAt(gameBoard,p[0],p[1])
					
			if event.type == MOUSEMOTION:
				if event.buttons[0] == 1 and firstSelectedGem != None:
					p = checkForGemClick(event.pos)
					if(p != None and p != prevGemPos and 
					(abs(p[0] - prevGemPos[0]) + abs(p[1] - prevGemPos[1]) <= 2) and
					getGemAt(gameBoard,p[0],p[1]) == firstSelectedGem):
						prevGemPos = p
						selected.append(p)

				#~ mousex, mousey = event.pos
				#~ for x in range(BOARDWIDTH):
					#~ for y in range(BOARDHEIGHT):
						#~ r = BOARDRECTS[x][y]
						#~ if(pygame.Rect(r).collidepoint(mousex, mousey)):
							#~ if(gameBoard[x][y] >= 0):
								#~ gameBoard[x][y]-=1


		DISPLAYSURF.fill(BGCOLOR)
		drawBoard(gameBoard)
		drawOrder()
		fillBoardAndAnimate(gameBoard)

		mousex, mousey = pygame.mouse.get_pos()
		for r in LISTRECTS:
			if(r.collidepoint(mousex,mousey)):
				highlightCell(r)

		for x in range(BOARDWIDTH):
			for y in range(BOARDHEIGHT):
				if(BOARDRECTS[x][y].collidepoint(mousex, mousey)):
					highlightCell(BOARDRECTS[x][y])

		if gameIsOver:
			pass

		pygame.display.update()
		FPSCLOCK.tick(FPS)

def getBlankBoard():
	# Create and return a blank board data structure.
	board = []
	for x in range(BOARDWIDTH):
		board.append([EMPTY_SPACE] * BOARDHEIGHT)
	return board

def getShuffledBoard():
	board = []
	for x in range(BOARDWIDTH):
		board.append([])
		for y in range(BOARDHEIGHT):
			board[x].append(random.choice([0,1]))
	return board

def selectCell(board):
	pass

def highlightCell(r):
	pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, r, 4)

def drawBoard(board):
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			pygame.draw.rect(DISPLAYSURF, GRIDCOLOR, BOARDRECTS[x][y], 1)
			gemToDraw = board[x][y]
			if gemToDraw != EMPTY_SPACE:
				DISPLAYSURF.blit(GEMIMAGES[gemToDraw], BOARDRECTS[x][y])

def drawOrder():
	for i in range(NUMGEMIMAGES):
		pygame.draw.rect(DISPLAYSURF, GRIDCOLOR, LISTRECTS[i], 1)
		DISPLAYSURF.blit(GEMIMAGES[i], LISTRECTS[i])

def checkForGemClick(pos):
	# See if the mouse click was on the board
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			if BOARDRECTS[x][y].collidepoint(pos[0], pos[1]):
				return x, y
	return None # Click was not on the board.

def getGemAt(board, x, y):
	if x < 0 or y < 0 or x >= BOARDWIDTH or y >= BOARDHEIGHT:
		return None
	else:
		return board[x][y]

def removeGems(board, sel):
	if(len(sel) > 2):
		s = sel[len(sel)-1]
		board[s[0]][s[1]] += 1
		sel.remove(s)
		for s in sel:
			board[s[0]][s[1]] = -1
		

def drawMovingGem(gem):
	# Draw a gem sliding in the direction that its 'direction' key
	# indicates. The progress parameter is a number from 0 (just
	# starting) to 100 (slide complete).
	movex = 0
	movey = 0

	if gem['direction'] == UP:
		movey = -int(GEMIMAGESIZE)
	elif gem['direction'] == DOWN:
		movey = int(GEMIMAGESIZE)
	elif gem['direction'] == RIGHT:
		movex = int(GEMIMAGESIZE)
	elif gem['direction'] == LEFT:
		movex = -int(GEMIMAGESIZE)

	basex = gem['x']
	basey = gem['y']
	if basey == ROWABOVEBOARD:
		basey = -1

	pixelx = XMARGIN + (basex * GEMIMAGESIZE)
	pixely = YMARGIN + (basey * GEMIMAGESIZE)
	r = pygame.Rect( (pixelx + movex, pixely + movey, GEMIMAGESIZE, GEMIMAGESIZE) )
	DISPLAYSURF.blit(GEMIMAGES[gem['imageNum']], r)


def pullDownAllGems(board):
	# pulls down gems on the board to the bottom to fill in any gaps
	for x in range(BOARDWIDTH):
		gemsInColumn = []
		for y in range(BOARDHEIGHT):
			if board[x][y] != EMPTY_SPACE:
				gemsInColumn.append(board[x][y])
		board[x] = ([EMPTY_SPACE] * (BOARDHEIGHT - len(gemsInColumn))) + gemsInColumn


def getDropSlots(board):
	# Creates a "drop slot" for each column and fills the slot with a
	# number of gems that that column is lacking. This function assumes
	# that the gems have been gravity dropped already.
	boardCopy = copy.deepcopy(board)
	pullDownAllGems(boardCopy)

	dropSlots = []
	for i in range(BOARDWIDTH):
		dropSlots.append([])

	# count the number of empty spaces in each column on the board
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT-1, -1, -1): # start from bottom, going up
			if boardCopy[x][y] == EMPTY_SPACE:
				newGem = random.randrange(0,GEMOFFSET,1)
				boardCopy[x][y] = newGem
				dropSlots[x].append(newGem)
	return dropSlots


def getDroppingGems(board):
	# Find all the gems that have an empty space below them
	boardCopy = copy.deepcopy(board)
	droppingGems = []
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT - 2, -1, -1):
			if boardCopy[x][y + 1] == EMPTY_SPACE and boardCopy[x][y] != EMPTY_SPACE:
				# This space drops if not empty but the space below it is
				droppingGems.append( {'imageNum': boardCopy[x][y], 'x': x, 'y': y, 'direction': DOWN} )
				boardCopy[x][y] = EMPTY_SPACE
	return droppingGems

def animateMovingGems(board, gems):
		DISPLAYSURF.fill(BGCOLOR)
		drawBoard(board)
		for gem in gems: # Draw each gem.
			drawMovingGem(gem)

		pygame.display.update()
		FPSCLOCK.tick(FPS)


def moveGems(board, movingGems):
	# movingGems is a list of dicts with keys x, y, direction, imageNum
	for gem in movingGems:
		if gem['y'] != ROWABOVEBOARD:
			board[gem['x']][gem['y']] = EMPTY_SPACE
			movex = 0
			movey = 0
			if gem['direction'] == LEFT:
				movex = -1
			elif gem['direction'] == RIGHT:
				movex = 1
			elif gem['direction'] == DOWN:
				movey = 1
			elif gem['direction'] == UP:
				movey = -1
			board[gem['x'] + movex][gem['y'] + movey] = gem['imageNum']
		else:
			# gem is located above the board (where new gems come from)
			board[gem['x']][0] = gem['imageNum'] # move to top row


def fillBoardAndAnimate(board):
	dropSlots = getDropSlots(board)
	while dropSlots != [[]] * BOARDWIDTH:
		# do the dropping animation as long as there are more gems to drop
		movingGems = getDroppingGems(board)
		for x in range(len(dropSlots)):
			if len(dropSlots[x]) != 0:
				# cause the lowest gem in each slot to begin moving in the DOWN direction
				movingGems.append({'imageNum': dropSlots[x][0], 'x': x, 'y': ROWABOVEBOARD, 'direction': DOWN})

		boardCopy = getBoardCopyMinusGems(board, movingGems)
		animateMovingGems(boardCopy, movingGems)
		moveGems(board, movingGems)

		# Make the next row of gems from the drop slots
		# the lowest by deleting the previous lowest gems.
		for x in range(len(dropSlots)):
			if len(dropSlots[x]) == 0:
				continue
			board[x][0] = dropSlots[x][0]
			del dropSlots[x][0]

def getBoardCopyMinusGems(board, gems):
	# Creates and returns a copy of the passed board data structure,
	# with the gems in the "gems" list removed from it.
	#
	# Gems is a list of dicts, with keys x, y, direction, imageNum

	boardCopy = copy.deepcopy(board)

	# Remove some of the gems from this board data structure copy.
	for gem in gems:
		if gem['y'] != ROWABOVEBOARD:
			boardCopy[gem['x']][gem['y']] = EMPTY_SPACE
	return boardCopy

if __name__ == '__main__':
	main()
