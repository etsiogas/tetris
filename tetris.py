#!/usr/bin/env python3

"""

KEY BINDINGS

up -> rotate block
down -> move block down at a faster rate
left -> move block to the left
right -> move block to the right
space -> move block to its lowest possible position
p -> pause
r -> restart
escape -> quit

"""

from __future__ import division
from color_constants import *
from random import randint
import pygame, os, random, math, sys, time, collections

# Constants
image = pygame.image.load('tiles.png')
TILE = image.get_height()
WIN_SIZE = (18 * TILE, 25 * TILE) # Window size
SIZE = (12 * TILE, 25 * TILE) # Game area
WIDTH_CONST = SIZE[0] + (WIN_SIZE[0] - SIZE[0]) // 2
ALPHA = 40
MAX_DELAY = 20

# Tile positioning
# *********
# * 0 * 4 *
# *********
# * 1 * 5 *
# *********
# * 2 * 6 *
# *********
# * 3 *****
# *********

tiles = {
	0: (0, 0),
	1: (0, TILE),
	2: (0, 2 * TILE),
	3: (0, 3 * TILE),
	4: (TILE, 0),
	5: (TILE, TILE),
	6: (TILE, 2 * TILE),
}

# Tile codes to form blocks
codes = {
	0: [0, 4, 1, 5], # O-block
	1: [0, 1, 2, 3], # I-block
	2: [0, 1, 5, 6], # S-block
	3: [4, 5, 1, 2], # Z-block
	4: [4, 5, 6, 2], # J-block
	5: [0, 1, 2, 6], # L-block
	6: [0, 1, 5, 2]  # T-block
}

# Functions
def blit_alpha(target, source, location, opacity):
	x = location[0]
	y = location[1]
	temp = pygame.Surface( ( source.get_width(), source.get_height() ) ).convert()
	temp.blit(target, (-x, -y))
	temp.blit(source, (0, 0))
	temp.set_alpha(opacity)
	target.blit(temp, location)
	
def get_surface(id):
	width = height = 0
	
	if id == 0:
		width = 2
		height = 2
	elif id == 1:
		width = 1
		height = 4
	else:
		width = 2
		height = 3
		
	surface = pygame.Surface([width * TILE, height * TILE], pygame.SRCALPHA, 32)
	code = codes[id]
	
	# Visualize tiles that form the block
	for item in code:
		surface.blit( image, tiles[item], (id * TILE, 0, TILE, TILE) )
		
	# Random initial rotation
	if(1 <= id <= 3):
		surface = pygame.transform.rotate(surface, random.choice([0, 90]))
	elif(id > 3):
		surface = pygame.transform.rotate(surface, random.choice([0, 90, 180, 270]))
		
	return surface
	
def rotate():
	global block, blocks
	
	if(block.id > 0):
		block.surface = pygame.transform.rotate(block.surface, 90)
		block.x = min(SIZE[0] - block.surface.get_width(), block.x)
		block.y = min(SIZE[1] - block.surface.get_height(), block.y)
		
		mask1 = pygame.mask.from_surface(block.surface)
		mask2 = pygame.mask.from_surface(blocks)
		
		if mask1.overlap(mask2, (-block.x, -block.y)):
			block.surface = pygame.transform.rotate(block.surface, -90)
			
def events():
	global running, left, right, down, bottom, paused, screen, block, blocks,\
		delay, next_blocks, points, max_delay, right_start, left_start
	for event in pygame.event.get():
		if event.type == pygame.QUIT or\
			(event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): # Quit
				running = False
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_r: # Restart
			init()
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_p: # Pause
			paused = not paused
		elif not paused and event.type == pygame.KEYDOWN: # Action
			if event.key == pygame.K_LEFT:
				left = True
			elif event.key == pygame.K_RIGHT:
				right = True
			elif event.key == pygame.K_DOWN:
				down = True
			elif event.key == pygame.K_UP:
				rotate()
			elif event.key == pygame.K_SPACE:
				bottom = True
		elif not paused and event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT:
				left_start = 0
				left = False
			elif event.key == pygame.K_RIGHT:
				right_start = 0
				right = False
			elif event.key == pygame.K_DOWN:
				down = False
				
def init():
	global screen, blocks, next_blocks, block, paused, points, max_delay,\
	running, left_start, right_start, left, right, down, bottom, delay, paused,\
	active, game_over
	
	screen.fill(GRAY)
	blocks = pygame.Surface(SIZE, pygame.SRCALPHA, 32)
	next_blocks = collections.deque()
	block = Block( randint(0, 6) )
	for i in range(3): next_blocks.append( Block( randint(0, 6) ) )
	left = right = down = bottom = paused = game_over = False
	running = active = True
	points = delay = right_start = left_start = 0
	max_delay = MAX_DELAY
	
class Block():
	def __init__(self, id):
		self.id = id
		self.surface = get_surface(id)
		self.x = SIZE[0] // 2 - (self.surface.get_width() // (2 * TILE) ) * TILE
		self.y = 0
		
# Initialization
os.environ['SDL_VIDEO_WINDOW_POS'] = \
	"%d,%d" % (960 - WIN_SIZE[0] // 2, 540 - WIN_SIZE[1] // 2 )
pygame.init()
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
screen = pygame.display.set_mode(WIN_SIZE)
font = pygame.font.SysFont('Comic Sans MS', 30)
SCORE = font.render('Score:', True, BLACK)
NEXT = font.render('Next:', True, BLACK)
GAME = font.render('GAME', True, RED3)
OVER = font.render('OVER', True, RED3)
init()

left_delay = 0
right_delay = 0

# Game loop
while running:
	events()
	
	if paused or game_over: continue
	
	# Create masks of pile of blocks and current block
	mask1 = pygame.mask.from_surface(block.surface)
	mask2 = pygame.mask.from_surface(blocks)
	
	check_left = check_right = False
	
	MSECS = 100
	
	if left_start == 0 or int( round(time.time() * 1000) ) - left_start > MSECS:
		check_left = True
		
	if right_start == 0 or int( round(time.time() * 1000) ) - right_start > MSECS:
		check_right = True
		
	# Width checks
	if check_left and left and block.x >= TILE:
		if left_start == 0:
			left_start = int( round(time.time() * 1000) )
			block.x -= TILE
		elif left_delay >= 2:
			left_delay = 0
			block.x -= TILE
			
		left_delay += 1
		
		if mask1.overlap( mask2, (-block.x, -block.y) ): block.x += TILE
		
	if check_right and right and block.x + block.surface.get_width() < SIZE[0]:
		if right_start == 0:
			right_start = int( round(time.time() * 1000) )
			block.x += TILE
		elif right_delay >= 2:
			right_delay = 0
			block.x += TILE
			
		right_delay += 1
		
		if mask1.overlap( mask2, (-block.x, -block.y) ): block.x -= TILE
		
	# Height checks
	if bottom:
		bottom = False
		
		while block.y + block.surface.get_height() < SIZE[1]:
			block.y += TILE
			
			if mask1.overlap(mask2, (-block.x, -block.y)):
				block.y -= TILE
				break
				
		active = False
	elif down:
		if block.y + block.surface.get_height() < SIZE[1]:
			block.y += TILE
			
			while mask1.overlap(mask2, (-block.x, -block.y)):
				block.y -= TILE
				active = False
		else: active = False
	else:
		if delay >= max_delay:
			delay = 0
			
			if block.y + block.surface.get_height() < SIZE[1]:
				block.y += TILE
				
				while mask1.overlap(mask2, (-block.x, -block.y)):
					block.y -= TILE
					active = False
			else: active = False
			
	delay += 1
	
	# Final check
	if block.y + block.surface.get_height() > SIZE[1]:
		block.y = SIZE[1] - block.surface.get_height()
		active = False
		
	screen.fill(GRAY)
	
	# Get new block
	if not active:
		active = True
		
		blocks.blit( block.surface, (block.x, block.y) )
		block = next_blocks[0]
		next_blocks.popleft()
		next_blocks.append( Block( randint(0, 6) ) )
		
		mask1 = pygame.mask.from_surface(block.surface)
		mask2 = pygame.mask.from_surface(blocks)
		
		# Check if new block collides with the pile
		while mask1.overlap( mask2, (-block.x, -block.y) ):
			block.y -= TILE
			game_over = True
			
		# Check for complete rows
		if not game_over:
			for row in range(TILE // 2, SIZE[1], TILE):
				counter = 0
				
				for col in range(TILE // 2, SIZE[0], TILE):
					if blocks.get_at((col, row))[3] == 255:
						counter += 1
						
				if counter == SIZE[0] // TILE:
					points += counter
					
					# Increase speed of falling blocks
					if max_delay > 1 and points % (5 * counter) == 0:
						max_delay -= 1
						
					upper = pygame.Surface(
						(SIZE[0], row - TILE // 2), pygame.SRCALPHA, 32 )
					lower = pygame.Surface(
						(SIZE[0], SIZE[1] - (row + TILE // 2)), pygame.SRCALPHA, 32)
					upper.blit( blocks, (0, 0),  (0, 0, SIZE[0], row - TILE // 2) )
					lower.blit( blocks, (0, 0),  (0, row + TILE // 2, SIZE[0], SIZE[1]) )
					
					blocks = pygame.Surface(SIZE, pygame.SRCALPHA, 32)
					blocks.blit( upper, (0, TILE) )
					blocks.blit( lower, (0, row + TILE // 2) )
		else:
			screen.blit( block.surface, (block.x, block.y) )
	else:
		screen.blit( block.surface, (block.x, block.y) )
		
	screen.blit( blocks, (0, 0) )
	
	score = font.render(str(points), True, BLACK)
	pygame.draw.line( screen, BLACK, (SIZE[0], 0), SIZE)
	pygame.draw.line( screen, BLACK, (SIZE[0], 90), (WIN_SIZE[0], 90 ) )
	
	score_x = WIDTH_CONST - score.get_width() // 2
	SCORE_x = WIDTH_CONST - SCORE.get_width() // 2
	
	screen.blit( SCORE, (SCORE_x, 20) )
	screen.blit( score, (score_x, 50) )
	
	if(not game_over):
		# Display reflection of block (always?)
		# mask1 = pygame.mask.from_surface(block.surface)
		# mask2 = pygame.mask.from_surface(blocks)
		
		for y in range(block.y, SIZE[1]):
			if y + block.surface.get_height() > SIZE[1] or\
				mask1.overlap(mask2, (-block.x, -y)):
					blit_alpha(screen, block.surface, (block.x, y - 1), ALPHA)
					break
					
		NEXT_x = WIDTH_CONST - NEXT.get_width() // 2
		screen.blit( NEXT, (NEXT_x, 110) )
		
		sum_height = 0
		
		# Display upcoming blocks
		for i in range( len(next_blocks) ):
			next_x = WIDTH_CONST - next_blocks[i].surface.get_width() // 2
			screen.blit( next_blocks[i].surface, (next_x, 160 + sum_height) )
			sum_height += next_blocks[i].surface.get_height() + 2 * TILE
	else:
		GAME_x = WIDTH_CONST - GAME.get_width() // 2
		screen.blit( GAME, (GAME_x, 110) )
		OVER_x = WIDTH_CONST - OVER.get_width() // 2
		screen.blit( OVER, (OVER_x, 135) )
		
	pygame.display.update()
	
	# Increase frame rate till events have zero latency
	clock.tick(32)
	