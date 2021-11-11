import os
import random
import time
import random
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pygame
import pygame.freetype
from psychopy import gui, core
from pygame.locals import *
from Maze_practice_mapTheme import *



### Session information GUI
correctSubj = False
while not correctSubj:
    dialog = gui.Dlg(title="") #task title ("Sherlock Spacebar Task)
    dialog.addField("Participant Number:")
    dialog.show()
    if gui.OK:
        if dialog.data[0][1].isdigit():
            subjectID = int(dialog.data[0])
            correctSubj = True

# Set up a global clock for keeping time
globalClock = core.Clock()

# define experiment structure & parameters
nRepeat = 1
ITI = 1 # pause before launching the next maze in second
# hard-set features: do not change lines below
pygame.display.init()
map_dimension = [7, 9]
nSet = 3 # 3 sets of 8 mazes, counterbalanced for goal location
screen_length = 288
screen_width = 224
info = pygame.display.Info()
width, height = info.current_w, info.current_h
start_x, start_y = int((width/2)-screen_length), int((height/2)-screen_width)
screen = pygame.Surface((screen_length, screen_width))

# record mouse click map
mouse_x_map = [range(0,64),range(64,128),range(128,192),range(192,256),range(256,320),range(320,384),range(384,448),range(448,512),range(512,576)]
mouse_y_map = [range(0,64),range(64,128),range(128,192),range(192,256),range(256,320),range(320,384),range(384,448)]

# define a function that runs a maze
# Player and Terrain classes are initialized/defined for each maze trial
def run_trial(display, screen, trial_map, spr_player, spr_tiles, background):
    class Player():
        def __init__(self, x, y):
            self.x = x
            self.y = y 
    
        def update(self):
            #print('curr self_x_y {} {}'.format(self.x, self.y))
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.y > 0:
                        if ((self.x/32, (self.y - 32)/32)) not in brick_index:
                            self.y -= 32
                    if event.key == pygame.K_DOWN and self.y < screen_width-32:
                        if ((self.x/32, (self.y + 32)/32)) not in brick_index:
                            self.y += 32
                    if event.key == pygame.K_LEFT and self.x > 0:
                        if ((self.x - 32)/32, self.y/32) not in brick_index:
                            self.x -= 32
                    if event.key == pygame.K_RIGHT and self.x < screen_length-32:
                        if ((self.x + 32)/32, self.y/32) not in brick_index:
                            self.x += 32

        def draw(self):
            screen.blit(spr_player, (int(self.x), int(self.y)))

    class Terrain():
        def __init__(self, x, y, Type):
            self.x = x
            self.y = y
            self.col = False
            self.type = Type

        def update(self):
            right_index = ((player.x+32) / 32, player.y / 32)
            left_index = ((player.x-32) / 32, player.y / 32)
            up_index = (player.x / 32, (player.y-32) / 32)
            down_index = (player.x / 32, (player.y+32) / 32)
            # print('right{} left{} up{} down{}'.format(right_index, left_index, up_index, down_index))
            # print('player_x_y {}'.format((round((player.x/32), round(player.y / 32)))))
            if (self.x // 32, self.y // 32) == right_index:
                if (self.x // 32, self.y // 32) in hidden_block_index:
                    #print('right{} self_x_y {} {}'.format(right_index, self.x, self.y))
                    remove.append(self)
                elif (self.x // 32, self.y // 32) == target:
                    self.type = 2
                        
            if (self.x // 32, self.y // 32) == left_index:
                if (self.x // 32, self.y // 32) in hidden_block_index:
                    #print('left{} self_x_y {} {}'.format(right_index, self.x, self.y))
                    remove.append(self)
                elif (self.x // 32, self.y // 32) == target:
                    self.type = 2

            if (self.x // 32, self.y // 32) == up_index:
                if (self.x // 32, self.y // 32) in hidden_block_index:
                    #print('up{} self_x_y {} {}'.format(up_index, self.x, self.y))
                    remove.append(self)
                elif (self.x // 32, self.y // 32) == target:
                    self.type = 2

            if (self.x // 32, self.y // 32) == down_index: 
                if (self.x // 32, self.y // 32) in hidden_block_index:
                    #print('down{} self_x_y {} {}'.format(down_index, self.x, self.y))
                    remove.append(self)
                elif (self.x // 32, self.y // 32) == target:
                    self.type = 2
                
        def draw(self):
            # this blits the tiles at the position, but starting with 6*32 end ending 32 further
            screen.blit(spr_tiles, (int(self.x), int(self.y)), (self.type * 32, 0, 32, 32))

    load = []
    remove = []
    player = Player(0,0) # initial x y coordinate for a player is always [0 0]
    hidden_block_index = []
    brick_index = []
    target = ()

    for i in range(len(trial_map)):
        for j in range(len(trial_map[i])):
            if trial_map[i][j] == "P":
                player = Player(j * 32, i * 32)
                load.append(player)
            if trial_map[i][j] == "0":
                load.append(Terrain(j * 32, i * 32, 0))
                brick_index.append((j,i))
            if trial_map[i][j] == "1":
                load.append(Terrain(j * 32, i * 32, 1))
                hidden_block_index.append((j, i))
            if trial_map[i][j] == "2":
                load.append(Terrain(j * 32, i * 32, 1))
                target = (j, i)


    alive = True
    while alive:

        screen.blit(background, (0, 0))

        events = pygame.event.get()
        # for event in events:
        #     if event.type == pygame.QUIT:
        #         alive = False

        for obj in load:
            obj.update()
            obj.draw()

        for obj in remove:
            load.remove(obj)
        remove = []

        if (round(player.x / 32), round(player.y / 32)) == target:
            alive = False

        display.blit(pygame.transform.scale(screen, (screen_length*2, screen_width*2)),((width/2)-screen_length, (height/2)-screen_width))  # (0,0)
        pygame.display.flip()

def run_guess(display, screen, trial_map, spr_player, spr_tiles, background):
    # load & display the initial map status
    # ask where the goal would be
    # record the coordinate (from the maze matrix) of mouse click
    class Terrain():
        def __init__(self, x, y, Type):
            self.x = x
            self.y = y
            self.col = False
            self.type = Type
                
        def draw(self):
            # this blits the tiles at the position, but starting with 6*32 end ending 32 further
            screen.blit(spr_tiles, (int(self.x), int(self.y)), (self.type * 32, 0, 32, 32))
        
        def change_color(self, x, y):
            if (self.x / 32) + 1 == x and (self.y / 32) + 1 == y:
                print('after if block x {}, y {}'.format(self.x, self.y))
                self.type = 3

    screen.blit(background, (0, 0))
    load = []
    hidden_coor = []

    for i in range(len(trial_map)):
        for j in range(len(trial_map[i])):
            if trial_map[i][j] == "P":
                load.append(Terrain(j * 32, i * 32, 1))
            if trial_map[i][j] == "0":
                load.append(Terrain(j * 32, i * 32, 0))
            if trial_map[i][j] == "1":
                load.append(Terrain(j * 32, i * 32, 1))
                hidden_coor.append((range(start_x + (j * 64), start_x + ((j+1) * 64)),range(start_y + (i * 64), start_y + ((i+1) * 64))))
            if trial_map[i][j] == "2":
                load.append(Terrain(j * 32, i * 32, 1))
                hidden_coor.append((range(start_x + (j * 64), start_x + ((j+1) * 64)),range(start_y + (i * 64), start_y + ((i+1) * 64))))

    for obj in load:
        obj.draw()
        display.blit(pygame.transform.scale(screen, (screen_length*2, screen_width*2)),((width/2)-screen_length, (height/2)-screen_width))
    pygame.display.flip()

    correctClick = False
    while not correctClick:
        events = pygame.event.get()
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for index in range(len(hidden_coor)):
                    if mouse_x in hidden_coor[index][0] and mouse_y in hidden_coor[index][1]:
                        guess_coor = ((hidden_coor[index][0][-1]+1-start_x) / 64, (hidden_coor[index][1][-1]+1-start_y) / 64) # or do not subtract
                        for obj in load:
                            if (obj.x / 32) + 1 == guess_coor[0] and (obj.y / 32) + 1 == guess_coor[1]:
                                obj.type = 3
                                obj.draw()
                                correctClick = True 
        display.blit(pygame.transform.scale(screen, (screen_length*2, screen_width*2)),((width/2)-screen_length, (height/2)-screen_width))  # (0,0)
        pygame.display.flip()
        time.sleep(1)

def render_text(surface, text, text_size, color):
    surface.fill((196, 196, 196))
    text_rect = font.get_rect(text, size = text_size)
    text_rect.center = surface.get_rect().center
    font.render_to(surface, text_rect, text, color, size = text_size)

def display_message_timed(surface, text, text_color, holdtime):
    render_text(surface, text, 35, text_color)
    pygame.display.flip()
    time.sleep(holdtime)

def display_message_key(surface, text, text_color):
    wait = True
    render_text(surface, text, 35, text_color)
    pygame.display.flip()
    while wait:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                wait = False


############## prepare messages ###########################
instructText = {'inst_nav': "Navigate to find the goal object.",
                'inst_quiz': "Click at the goal object location.",
                'new_set': "You'll now visit new mazes!",
                'start': "Press a key to start.",
                'greatjob': 'Great Job!',
                }
text_color = (10, 10, 10)

pygame.init()
font = pygame.freetype.SysFont("freesansbold", 0)
display = pygame.display.set_mode((0,0,), pygame.FULLSCREEN) # needs to be run before pygame.image.load

# message: starting navigation
display_message_key(display, instructText['inst_nav'], text_color)
display_message_key(display, instructText['start'], text_color)
#pygame.quit()


# define map & agent for this trial
# re-select in a map-specific manner
sequence = [0,1,2]
random.shuffle(sequence)
for i in sequence:
    display = pygame.display.set_mode((0,0,), pygame.FULLSCREEN)  # needs to be run before pygame.image.load
    player_name = maze_theme[layout[i][7]][0]
    tiles_name = maze_theme[layout[i][7]][1]
    background_name = maze_theme[layout[i][7]][2]

    spr_player = pygame.image.load("assets/" + player_name + ".png").convert_alpha()
    spr_tiles = pygame.image.load("assets/" + tiles_name + ".png").convert_alpha()
    background = pygame.image.load("assets/" + background_name + ".jpg").convert()
    trial_map = layout[i]

    # pygame.display.set_caption('Move the agent to find the goal object')
    run_trial(display, screen, trial_map, spr_player, spr_tiles, background)
    time.sleep(ITI)
    #pygame.quit()

display = pygame.display.set_mode((0,0,), pygame.FULLSCREEN)  # needs to be run before pygame.image.load
display_message_key(display, instructText['inst_quiz'], text_color)
display_message_key(display, instructText['start'], text_color)

random.shuffle(sequence)
for i in sequence:
    # pygame.display.set_caption('Click where you think the goal object was in this maze!')
    player_name = maze_theme[layout[i][7]][0]
    tiles_name = maze_theme[layout[i][7]][1]
    background_name = maze_theme[layout[i][7]][2]

    spr_player = pygame.image.load("assets/" + player_name + ".png").convert_alpha()
    spr_tiles = pygame.image.load("assets/" + tiles_name + ".png").convert_alpha()
    background = pygame.image.load("assets/" + background_name + ".jpg").convert()
    trial_map = layout[i]

    run_guess(display, screen, trial_map, spr_player, spr_tiles, background)
    time.sleep(1)
display_message_timed(display, instructText['greatjob'], text_color, 3)



