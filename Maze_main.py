import os

import numpy as np
import pandas as pd 
import pygame
from pygame.locals import *
import time
import random
from datetime import datetime, timezone

import psychopy
from psychopy import gui, event, core

from Maze_map import *

### Set specific paths --- change based on computer --- follow same folder format
<<<<<<< HEAD
filedir = '/Users/chaodanluo/Desktop/lab_github/MazeGame/solving_log_dir/'#provide output file directory
=======
filedir = '/Users/chaodanluo/Desktop/lab_github/Maze/solving_log_dir/'#provide output file directory
#filedir = '/Users/kaminkim/Documents/projects/iEEG_MAZE/MazeGame/data/'#do not delet: comment out instead
>>>>>>> 6f4aea6b93b61c4ced689e6ad77fff1c8e5c54fe

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

# Create the logfile
if os.path.isfile(filedir+"%d_maze_log.txt" %(subjectID)):
    os.rename(filedir+"%d_maze_log.txt" %(subjectID), filedir+"%d_maze_log_old_%s.txt" %(subjectID,time.time()))
output_df = []



# Set up a global clock for keeping time
globalClock = core.Clock()

# define experiment structure
nBlock = 1
nTrial = 5

###################### START: modification of Maze.py ###########################################
# create the screen
screen_length = 288
screen_width = 224
screen = pygame.Surface((screen_length, screen_width))

# record mouse click map
mouse_x_map = [range(0,64),range(64,128),range(128,192),range(192,256),range(256,320),range(320,384),range(384,448),range(448,512),range(512,576)]
mouse_y_map = [range(0,64),range(64,128),range(128,192),range(192,256),range(256,320),range(320,384),range(384,448)]

def run_trial(display, screen, trial_map, spr_player, spr_tiles, background):

    # class Player(pygame.sprite.Sprite):
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
                            key_pressed = 'up'
                            timestamp = datetime.now(timezone.utc).astimezone()
                            coordinate = (self.x / 32) + 1, (self.y / 32) + 1
                            line = [key_pressed, timestamp, coordinate]
                            output_df.append(line)
                    if event.key == pygame.K_DOWN and self.y < screen_width-32:
                        if ((self.x/32, (self.y + 32)/32)) not in brick_index:
                            self.y += 32
                            key_pressed = 'down'
                            timestamp = datetime.now(timezone.utc).astimezone()
                            coordinate = (self.x / 32) + 1, (self.y / 32) + 1
                            line = [key_pressed, timestamp, coordinate]
                            output_df.append(line)
                    if event.key == pygame.K_LEFT and self.x > 0:
                        if ((self.x - 32)/32, self.y/32) not in brick_index:
                            self.x -= 32
                            key_pressed = 'left'
                            timestamp = datetime.now(timezone.utc).astimezone()
                            coordinate = (self.x / 32) + 1, (self.y / 32) + 1
                            line = [key_pressed, timestamp, coordinate]
                            output_df.append(line)
                    if event.key == pygame.K_RIGHT and self.x < screen_length-32:
                        if ((self.x + 32)/32, self.y/32) not in brick_index:
                            self.x += 32
                            key_pressed = 'right'
                            timestamp = datetime.now(timezone.utc).astimezone()
                            coordinate = (self.x / 32) + 1, (self.y / 32) + 1,
                            line = [key_pressed, timestamp, coordinate]
                            output_df.append(line)
            

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
    player = Player(0,0)
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

    
    start_time = datetime.now(timezone.utc).astimezone()
    start_loc = (1.0, 1.0)
    line = ['start', start_time, start_loc]
    output_df.append(line)
    alive = True
    while alive:

        screen.blit(background, (0, 0))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False

  

        # KK: LOG RESPONSE, AGENT LOCATION (COORDINATES INT HE MATRIX)
        
        for obj in load:
            obj.update()
            obj.draw()
        for obj in remove:
            load.remove(obj)
        remove = []

        if (round(player.x / 32), round(player.y / 32)) == target:
            alive = False

        display.blit(pygame.transform.scale(screen, (screen_length * 2, screen_width * 2)), (0, 0))
        pygame.display.flip()

 
##################### END: modification of Maze.py ###########################################

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
<<<<<<< HEAD
    
    pygame.display.set_caption('Click where you think the goal object is!')
    
=======

    pygame.display.set_caption('Click where you think the goal object is!')
>>>>>>> 6f4aea6b93b61c4ced689e6ad77fff1c8e5c54fe

    for i in range(len(trial_map)):
        for j in range(len(trial_map[i])):
            if trial_map[i][j] == "P":
                load.append(Terrain(j * 32, i * 32, 1))
            if trial_map[i][j] == "0":
                load.append(Terrain(j * 32, i * 32, 0))
            if trial_map[i][j] == "1":
                load.append(Terrain(j * 32, i * 32, 1))
                hidden_coor.append((range(j * 64, (j+1) * 64),range(i * 64, (i+1) * 64)))
            if trial_map[i][j] == "2":
                load.append(Terrain(j * 32, i * 32, 1))
                hidden_coor.append((range(j * 64, (j+1) * 64),range(i * 64, (i+1) * 64)))

    for obj in load:
        obj.draw()
    display.blit(pygame.transform.scale(screen, (screen_length * 2, screen_width * 2)), (0, 0))
    pygame.display.flip()
    
    

    correctClick = False
    while not correctClick:
       
        # psychopy instructions
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for index in range(len(hidden_coor)):
                        if mouse_x in hidden_coor[index][0] and mouse_y in hidden_coor[index][1]:
                            guess_coor = ((hidden_coor[index][0][-1]+1) / 64, (hidden_coor[index][1][-1]+1) / 64)
                            output_df.append([guess_coor])
                            for obj in load:
                                if (obj.x / 32) + 1 == guess_coor[0] and (obj.y / 32) + 1 == guess_coor[1]:
                                    obj.type = 3
                                    obj.draw()
                                    correctClick = True 
        display.blit(pygame.transform.scale(screen, (screen_length * 2, screen_width * 2)), (0, 0))
        pygame.display.flip()
        time.sleep(1)
                                                
                            
                
        

print(len(layout))
# KK: ADD RANDOM SELECTION OF LAYOUTS TO USE

# running blocks

# shuffle themes
maze_theme = {
    'face' : ['happyface', 'original_1', 'milkywhite'],
    'dolphin' : ['dolphin', 'ocean_1', 'ocean_blue2'],
    'monkey' : ['monkey', 'jungle_1', 'plain_green'],
    'bird' : ['bird', 'sky_1', 'white'],
    'cow' : ['cow', 'pasture_1', 'grassgreen']
}
theme_strings = ['face', 'dolphin', 'monkey', 'bird', 'cow']
random.shuffle(theme_strings)
for a in range(len(theme_strings)):
    layout[a] + (theme_strings[a],)
new_layout = [layout[a] + (theme_strings[a],) for a in range(len(theme_strings)) ]

for i in range(nBlock):
    # KK: printings are for sanity check
    tseq = np.arange(0, nTrial, 1)
    print(tseq)
    random.shuffle(tseq)
    print(tseq)

    # set up and run each trial
    for j in range(len(tseq)):
        # define map & agent for this trial
        display = pygame.display.set_mode((screen_length * 2, screen_width * 2)) # needs to be run before pygame.image.load

        # re-select in a map-specific manner
        player_name = maze_theme[new_layout[tseq[j]][7]][0]
        tiles_name = maze_theme[new_layout[tseq[j]][7]][1]
        background_name = maze_theme[new_layout[tseq[j]][7]][2]

        spr_player = pygame.image.load("assets/" + player_name + ".png").convert_alpha()
        spr_tiles = pygame.image.load("assets/" + tiles_name + ".png").convert_alpha() 
        background = pygame.image.load("assets/" + background_name + ".jpg").convert()
       
        trial_map = layout[tseq[j]]
        run_guess(display, screen, trial_map, spr_player, spr_tiles, background)
<<<<<<< HEAD
        time.sleep(1)
=======
        pygame.display.set_caption('Move the agent to find the goal object')
>>>>>>> 6f4aea6b93b61c4ced689e6ad77fff1c8e5c54fe
        run_trial(display, screen, trial_map, spr_player, spr_tiles, background)
        pygame.quit()
for i in range(len(output_df)):
    if isinstance(output_df[i][0], str):
        if output_df[i][0] == 'start':
            rt = 0
            output_df[i].append(rt)
        else:
            rt = str(output_df[i][1] - output_df[i-1][1])
            output_df[i].append(rt)
for i in range(len(output_df)):
    if isinstance(output_df[i][0], str):
        output_df[i][1] = str(output_df[i][1])
df = pd.DataFrame(output_df)
os.chdir(filedir)
df.to_csv("%d_maze_log.txt" %(subjectID), header = ['key_pressed', 'timestamp', 'coordinate', 'rt'], sep = '\t')  