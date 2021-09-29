import os
import random
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pygame
from psychopy import gui, core
from pygame.locals import *
from Maze_map import *
from Maze_theme import *

### Set specific paths --- change based on computer --- follow same folder format
# filedir = '/Users/chaodanluo/Desktop/lab_github/MazeGame/solving_log_dir/'#provide output file directory
filedir_data = '/Users/kaminkim/Documents/projects/iEEG_MAZE/MazeGame/data/'#do not delete: comment out instead
filedir_config = '/Users/kaminkim/Documents/projects/iEEG_MAZE/MazeGame/config/'#do not delete: comment out instead

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
if os.path.isfile(filedir_data+"%d_maze_log.txt" %(subjectID)):
    os.rename(filedir_data+"%d_maze_log.txt" %(subjectID), filedir_data+"%d_maze_log_old_%s.txt" %(subjectID,time.time()))
output_df = []

# Set up a global clock for keeping time
globalClock = core.Clock()

# define experiment structure & parameters
nBlock = 1
nRepeat = 3
ITI = 1 # pause before launching the next maze in second
# hard-set features: do not change lines below
map_dimension = [7, 9]
nSet = 3 # 3 sets of 8 mazes, counterbalanced for goal location
screen_length = 288
screen_width = 224
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
    
    start_time = datetime.now(timezone.utc).astimezone()
    start_loc = (1.0, 1.0)
    line = ['start', start_time, start_loc]
    output_df.append(line)

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

        display.blit(pygame.transform.scale(screen, (screen_length * 2, screen_width * 2)), (0, 0))
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
        events = pygame.event.get()
        # psychopy instructions
        for event in events:
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

def get_coord(maze_map):
    for row in range(len(maze_map)):
        clm = str.find(maze_map[row], '2')
        if clm > -1:
            target_coord = [row, clm]
    return target_coord

def get_quad(row, clm, dim):
    row = row + 1
    clm = clm + 1
    if row < dim[0]/2 and clm > dim[1]/2:
        target_quadrant = 1
    elif row > dim[0]/2 and clm > dim[1]/2:
        target_quadrant = 2
    elif row > dim[0]/2 and clm < dim[1]/2:
        target_quadrant = 3
    elif row < dim[0]/2 and clm < dim[1]/2:
        target_quadrant = 4
    return target_quadrant

def counterbalance_maze_set (maze_idx, goal_quad):
    q1_mazelist = maze_idx[goal_quad == 1]
    q2_mazelist = maze_idx[goal_quad == 2]
    q3_mazelist = maze_idx[goal_quad == 3]
    q4_mazelist = maze_idx[goal_quad == 4]
    random.shuffle(q1_mazelist)
    random.shuffle(q2_mazelist)
    random.shuffle(q3_mazelist)
    random.shuffle(q4_mazelist)
    maze_set = []
    maze_set.append(np.concatenate((q1_mazelist[0:2], q2_mazelist[0:2], q3_mazelist[0:2], q4_mazelist[0:2])))
    maze_set.append(np.concatenate((q1_mazelist[2:4], q2_mazelist[2:4], q3_mazelist[2:4], q4_mazelist[2:4])))
    maze_set.append(np.concatenate((q1_mazelist[4:6], q2_mazelist[4:6], q3_mazelist[4:6], q4_mazelist[4:6])))
    return maze_set

############## prepare stimuli ###########################3
# associate each maze (layout) with a randomly-selected theme (shuffled)
random.shuffle(theme_strings)
new_layout = [layout[a] + (theme_strings[a],) for a in range(len(theme_strings))]

# maze assignment across blocks
# 8 mazes are learned in a set of 8 mazes: equal number of goal locations in each quadrantn a set
# a set of 8 mazes are repeated over 3 consecutive blocks

# Extract goal locations from maze_map, assign mazes to 3 sets while counterbalancing for goal location
goal_quad = []
for maze in range(len(layout)):
    goal = get_coord(layout[maze])
    goal_quad.append(get_quad(goal[0], goal[1], map_dimension))
goal_quad = np.array(goal_quad)
maze_idx = np.arange(len(goal_quad))
maze_set = counterbalance_maze_set(maze_idx, goal_quad)

maze_seqs = []
for set in range(len(maze_set)):
    maze_seq = maze_set[set] # DO NOT SHULFFLE THIS
    maze_seqlist = maze_seq.tolist()
    # will repeat this set - with maze order shuffled for each repetition
    for block in range(nRepeat):
        # randomize maze sequence, set up and run each trial
        rand_seq = random.sample(maze_seqlist, len(maze_seqlist))
        maze_seqs.append(['nav', rand_seq])
        for j in range(len(maze_seq)):
            # define map & agent for this trial
            display = pygame.display.set_mode((screen_length * 2, screen_width * 2)) # needs to be run before pygame.image.load

            # re-select in a map-specific manner
            player_name = maze_theme[new_layout[maze_seq[j]][7]][0]
            tiles_name = maze_theme[new_layout[maze_seq[j]][7]][1]
            background_name = maze_theme[new_layout[maze_seq[j]][7]][2]

            spr_player = pygame.image.load("assets/" + player_name + ".png").convert_alpha()
            spr_tiles = pygame.image.load("assets/" + tiles_name + ".png").convert_alpha()
            background = pygame.image.load("assets/" + background_name + ".jpg").convert()
            trial_map = layout[maze_seq[j]]

            pygame.display.set_caption('Move the agent to find the goal object')
            run_trial(display, screen, trial_map, spr_player, spr_tiles, background)
            time.sleep(ITI)
            pygame.quit()

        # randomize maze sequenc and run quiz for this set
        rand_seq = random.sample(maze_seqlist, len(maze_seqlist))
        maze_seqs.append(['quiz', rand_seq])
        for j in range(len(maze_seq)):
            # define map & agent for this trial
            display = pygame.display.set_mode((screen_length * 2, screen_width * 2))  # needs to be run before pygame.image.load

            # re-select in a map-specific manner
            player_name = maze_theme[new_layout[maze_seq[j]][7]][0]
            tiles_name = maze_theme[new_layout[maze_seq[j]][7]][1]
            background_name = maze_theme[new_layout[maze_seq[j]][7]][2]

            spr_player = pygame.image.load("assets/" + player_name + ".png").convert_alpha()
            spr_tiles = pygame.image.load("assets/" + tiles_name + ".png").convert_alpha()
            background = pygame.image.load("assets/" + background_name + ".jpg").convert()
            trial_map = layout[maze_seq[j]]

            pygame.display.set_caption('Click where you think the goal object was in this maze!')
            run_guess(display, screen, trial_map, spr_player, spr_tiles, background)
            time.sleep(1)

# write out a logfile
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
os.chdir(filedir_data)
df.to_csv("%d_maze_log.csv" %(subjectID), header = ['key_pressed', 'timestamp', 'coordinate', 'rt'], sep = ',')

# save sequences of mazes used
seq_df = pd.DataFrame(maze_seqs)
os.chdir(filedir_config)
seq_df.to_csv("%d_maze_seq.csv" %(subjectID), header = ['task', 'sequence'], sep = ',')

# save maze-theme association used
theme_df = pd.DataFrame(theme_strings)
os.chdir(filedir_config)
theme_df.to_csv("%d_maze_themes.csv" %(subjectID), header = ['theme'], sep = ',')

