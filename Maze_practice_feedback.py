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
        subjectID = dialog.data[0]
        correctSubj = True

# Set up a global clock for keeping time
globalClock = core.Clock()

# define experiment structure & parameters
nRepeat = 1
ITI = 0.5 # pause before launching the next maze in second
photodiode_square_size = 3 # choosing from SS_levels
SS_levels = [16, 24, 32, 48, 64, 128]

# hard-set features: do not change lines below
pygame.display.init()
map_dimension = [7, 9]
screen_width = 288
screen_height = 224
info = pygame.display.Info()
width, height = info.current_w, info.current_h
start_x, start_y = int((width/2)-screen_width), int((height/2)-screen_height)
screen = pygame.Surface((screen_width, screen_height))
square_size = SS_levels[photodiode_square_size]

# Player and Terrain classes are initialized/defined for each maze trial
def run_trial(display, screen, trial_map, spr_player, spr_tiles, background):
    class Player():
        def __init__(self, x, y):
            self.x = x
            self.y = y 
    
        def update(self):
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.y > 0:
                        if ((self.x/32, (self.y - 32)/32)) not in brick_index:
                            self.y -= 32
                    if event.key == pygame.K_DOWN and self.y < screen_height-32:
                        if ((self.x/32, (self.y + 32)/32)) not in brick_index:
                            self.y += 32
                    if event.key == pygame.K_LEFT and self.x > 0:
                        if ((self.x - 32)/32, self.y/32) not in brick_index:
                            self.x -= 32
                    if event.key == pygame.K_RIGHT and self.x < screen_width-32:
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
            if (self.x // 32, self.y // 32) == right_index:
                if (self.x // 32, self.y // 32) in hidden_block_index:
                    remove.append(self)
                elif (self.x // 32, self.y // 32) == target:
                    self.type = 2
                        
            if (self.x // 32, self.y // 32) == left_index:
                if (self.x // 32, self.y // 32) in hidden_block_index:
                    remove.append(self)
                elif (self.x // 32, self.y // 32) == target:
                    self.type = 2

            if (self.x // 32, self.y // 32) == up_index:
                if (self.x // 32, self.y // 32) in hidden_block_index:
                    remove.append(self)
                elif (self.x // 32, self.y // 32) == target:
                    self.type = 2

            if (self.x // 32, self.y // 32) == down_index: 
                if (self.x // 32, self.y // 32) in hidden_block_index:
                    remove.append(self)
                elif (self.x // 32, self.y // 32) == target:
                    self.type = 2
                
        def draw(self):
            # this blits the tiles at the position, but starting with 6*32 end ending 32 further
            screen.blit(spr_tiles, (int(self.x), int(self.y)), (self.type * 32, 0, 32, 32))

    pygame.event.clear() # clear events first
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

    # display updates during a trial
    alive = True
    while alive:

        screen.blit(background, (0, 0))
        events = pygame.event.get()

        for obj in load:
            obj.update()
            obj.draw()

        for obj in remove:
            load.remove(obj)
        remove = []

        if (round(player.x / 32), round(player.y / 32)) == target:
            alive = False

        display.blit(pygame.transform.scale(screen, (screen_width*2, screen_height*2)),((width/2)-screen_width, (height/2)-screen_height))  # (0,0)
        pygame.display.flip()
    time.sleep(1) # display stays for 1sec after entering the goal location

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
        

    screen.blit(background, (0, 0))
    load = []
    hidden_coor = []
    target = ()

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
                target = (j+1, i+1)
                hidden_coor.append((range(start_x + (j * 64), start_x + ((j+1) * 64)),range(start_y + (i * 64), start_y + ((i+1) * 64))))

    for obj in load:
        obj.draw()
        display.blit(pygame.transform.scale(screen, (screen_width*2, screen_height*2)),((width/2)-screen_width, (height/2)-screen_height))
    pygame.display.flip()

    # For a valid click, give a visual feedback & log the response
    pygame.event.clear() # clear events first
    correctClick = False
    while not correctClick:
        events = pygame.event.get()
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for index in range(len(hidden_coor)):
                    if mouse_x in hidden_coor[index][0] and mouse_y in hidden_coor[index][1]:
                        guess_coor = (int((hidden_coor[index][0][-1]+1-start_x) / 64), int((hidden_coor[index][1][-1]+1-start_y) / 64)) # or do not subtract
                        for obj in load:
                            if (obj.x / 32) + 1 == guess_coor[0] and (obj.y / 32) + 1 == guess_coor[1]:
                                if guess_coor[0] == target[0] and guess_coor[1] == target[1]:
                                    obj.type = 4
                                    obj.draw()
                                    correctClick = True
                                    break
                                obj.type = 3
                                obj.draw()
                                correctClick = True

        display.blit(pygame.transform.scale(screen, (screen_width*2, screen_height*2)),((width/2)-screen_width, (height/2)-screen_height))  # (0,0)
        pygame.display.flip()
    time.sleep(0.5)  # display stays for 0.5sec after the response

def run_guess_structure(display, screen, trial_map):
    # load & display the initial map status
    # ask where the goal would be
    # record the coordinate (from the maze matrix) of mouse click

    spr_tiles = pygame.image.load("assets/maze_structure.png").convert_alpha()
    background = pygame.image.load("assets/anti-flash-white.jpg").convert()

    class Terrain():
        def __init__(self, x, y, Type):
            self.x = x
            self.y = y
            self.col = False
            self.type = Type
                
        def draw(self):
            # this blits the tiles at the position, but starting with 6*32 end ending 32 further
            screen.blit(spr_tiles, (int(self.x), int(self.y)), (self.type * 32, 0, 32, 32))
        

    load = []
    hidden_coor = []
    target = ()
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
                target = (j+1, i+1)
                hidden_coor.append((range(start_x + (j * 64), start_x + ((j+1) * 64)),range(start_y + (i * 64), start_y + ((i+1) * 64))))

    screen.blit(background, (0, 0))
    for obj in load:
        obj.draw()
        display.blit(pygame.transform.scale(screen, (screen_width * 2, screen_height * 2)), ((width / 2) - screen_width, (height / 2) - screen_height))  # (0,0)
    pygame.display.flip()

    # For a valid click, give a visual feedback & log the response
    pygame.event.clear() # clear events first
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
                                if guess_coor[0] == target[0] and guess_coor[1] == target[1]:
                                    obj.type = 3
                                    obj.draw()
                                    correctClick = True
                                    break
                                obj.type = 2
                                obj.draw()
                                correctClick = True
        display.blit(pygame.transform.scale(screen, (screen_width*2, screen_height*2)),((width/2)-screen_width, (height/2)-screen_height))  # (0,0)
        pygame.display.flip()
    time.sleep(0.5)  # display stays for 0.5sec after the response

def photodiode_square(surface):
    surface.fill((0, 0, 0)) # to offset the maze
    photodiode_square = pygame.image.load("assets/white-square-" + str(square_size) + ".png").convert_alpha()
    surface.blit(photodiode_square, (0, height-square_size))
    pygame.display.flip()
    time.sleep(1)
    surface.fill((0, 0, 0))
    pygame.display.flip()

def render_text(surface, text, text_size, color):
    surface.fill((0, 0, 0))
    text_rect = font.get_rect(text, size = text_size)
    text_rect.center = surface.get_rect().center
    font.render_to(surface, text_rect, text, color, size = text_size)

def display_message_timed(surface, text, text_color, holdtime):
    render_text(surface, text, 35, text_color)
    pygame.display.flip()
    time.sleep(holdtime)

def display_message_key(surface, text, text_color):
    pygame.event.clear() # clear events first
    wait = True
    render_text(surface, text, 35, text_color)
    pygame.display.flip()
    while wait:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                wait = False


############## prepare messages ###########################
instructText = {'inst_nav': "Navigate to find the goal object. Press a key to go proceed.",
                'inst_quiz': "Click at the goal object location. Press a key to go proceed.",
                'new_set': "You'll now visit NEW mazes! Press a key to go proceed.",
                'start': "Press a key to when you are ready to start.",
                'greatjob': 'You finished this block. Great Job!',
                'non_contextual_quiz' : "You'll now see non-contextual quizzes. Press a key to go proceed."
                }
text_color = (255, 255, 255)

pygame.init()
font = pygame.freetype.SysFont("freesansbold", 0)
display = pygame.display.set_mode((0,0,), pygame.FULLSCREEN) 

#-------------- NAVIGATION --------------#
# message: starting navigation
display_message_key(display, instructText['inst_nav'], text_color)
display_message_key(display, instructText['start'], text_color)
display.fill((0, 0, 0))
pygame.mouse.set_visible(False)

# define map & agent for this trial
# re-select in a map-specific manner
sequence = [0,1,2]
random.shuffle(sequence)
for i in sequence:
    # call map & agent for this trial
    player_name = maze_theme[layout[i][7]][0]
    tiles_name = maze_theme[layout[i][7]][1]
    background_name = maze_theme[layout[i][7]][2]

    spr_player = pygame.image.load("assets/" + player_name + ".png").convert_alpha()
    spr_tiles = pygame.image.load("assets/" + tiles_name + ".png").convert_alpha()
    background = pygame.image.load("assets/" + background_name + ".jpg").convert()
    trial_map = layout[i]

    # run a navigation trial
    run_trial(display, screen, trial_map, spr_player, spr_tiles, background)
    photodiode_square(display)

# -------------- CONTEXTUAL QUIZ --------------#
# messages
display_message_key(display, instructText['inst_quiz'], text_color)
display_message_key(display, instructText['start'], text_color)
display.fill((0, 0, 0))
pygame.mouse.set_visible(True)

# randomize maze sequence and run quiz for this set
random.shuffle(sequence)
for i in sequence:
    # call map for this trial
    player_name = maze_theme[layout[i][7]][0]
    tiles_name = maze_theme[layout[i][7]][1]
    background_name = maze_theme[layout[i][7]][2]

    spr_player = pygame.image.load("assets/" + player_name + ".png").convert_alpha()
    spr_tiles = pygame.image.load("assets/" + tiles_name + ".png").convert_alpha()
    background = pygame.image.load("assets/" + background_name + ".jpg").convert()
    trial_map = layout[i]
    # run a quiz trial
    run_guess(display, screen, trial_map, spr_player, spr_tiles, background)
    photodiode_square(display)

# -------------- NON-CONTEXTUAL QUIZ --------------#
# messages
display_message_key(display, instructText['non_contextual_quiz'], text_color)
display_message_key(display, instructText['inst_quiz'], text_color)
display_message_key(display, instructText['start'], text_color)
display.fill((0, 0, 0))
pygame.mouse.set_visible(True)

# randomize maze sequence and run quiz for this set
random.shuffle(sequence)
for i in sequence:
    trial_map = layout[i]
    # run a quiz trial
    run_guess_structure(display, screen, trial_map)
    photodiode_square(display)
display_message_timed(display, instructText['greatjob'], text_color, 3)
