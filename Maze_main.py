import os
import random
import time
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import pygame
import pygame.freetype
from psychopy import gui, core
from pygame.locals import *
from Maze_map import *
from Maze_theme import *

# Set directories
MazeGame_dir = os.getcwd()
filedir_data = MazeGame_dir+'/data/'
filedir_config = MazeGame_dir+'/config/'

### Session information GUI
correctSubj = False
while not correctSubj:
    dialog = gui.Dlg(title="Maze Experiment")
    dialog.addField("Participant Number:")
    dialog.show()
    if gui.OK:
        subjectID = dialog.data[0]
        correctSubj = True

# Create a logfile
if os.path.isfile(filedir_data+"%s_maze_log.txt" %(subjectID)):
    os.rename(filedir_data+"%s_maze_log.txt" %(subjectID), filedir_data+"%s_maze_log_old_%s.txt" %(subjectID,time.time()))
output_df = []

# Set up a global clock for keeping time
globalClock = core.Clock()

# define experiment structure & parameters
nRepeat = 3
ITI = 0.5 # pause before launching the next maze in second
photodiode_square_size = 3 # choosing from SS_levels
SS_levels = [16, 24, 32, 48, 64, 128]

# hard-set features: do not change lines below
pygame.display.init()
map_dimension = [7, 9]
nSet = 3 # 3 sets of 8 mazes, counterbalanced for goal location
screen_width = 288
screen_height = 224
info = pygame.display.Info()
width, height = info.current_w, info.current_h
start_x, start_y = int((width/2) - screen_width), int((height / 2) - screen_height)
screen = pygame.Surface((screen_width, screen_height))
square_size = SS_levels[photodiode_square_size]

# Player and Terrain classes are initialized/defined for each maze trial
def run_trial(display, screen, trial_map, spr_player, spr_tiles, background, block_num, trial_num, maze_ID):
    block_num = block_num
    trial_num = trial_num + 1
    class Player():
        def __init__(self, x, y):
            self.x = x
            self.y = y 

        def cal_4_sides(self):
            sides = [1,1,1,1]
            right_index = ((self.x+32) / 32, self.y / 32)
            left_index = ((self.x-32) / 32, self.y / 32)
            up_index = (self.x / 32, (self.y-32) / 32)
            down_index = (self.x / 32, (self.y+32) / 32)

            if right_index in brick_index or self.x >= screen_width-32:
                sides[1] = 0
            if right_index == target:
                sides[1] = 2
            if left_index in brick_index or self.x <= 0:
                sides[3] = 0
            if left_index == target:
                sides[3] = 2
            if up_index in brick_index or self.y <= 0:
                sides[0] = 0
            if up_index == target:
                sides[0] = 2
            if down_index in brick_index or self.y >= screen_height-32:
                sides[2] = 0
            if down_index == target:
                sides[2] = 2
            return(sides)

        def classify_blocks(self,sides):
            block = ''
            if sides.count(1) == 2:
                block = 'N' # neutral path
            if sides.count(1) >= 3:
                sides_2nd = [1,1,1,1,1,1,1,1]
                sides_2nd_general = [0,0,0,0]
                pos_0 = (self.x / 32, (self.y-64) / 32)
                pos_1 = ((self.x+32) / 32, (self.y-32) / 32)
                pos_2 = ((self.x+64) / 32, self.y / 32)
                pos_3 = ((self.x+32) / 32, (self.y+32) / 32)
                pos_4 = (self.x / 32, (self.y+64) / 32)
                pos_5 = ((self.x-32) / 32, (self.y+32) / 32)
                pos_6 = ((self.x-64) / 32, self.y / 32)
                pos_7 = ((self.x-32) / 32, (self.y-32) / 32)

                if pos_0 in brick_index or self.y - 32 <= 0:
                    sides_2nd[0] = 0
                if pos_1 in brick_index or self.y <= 0 or self.x >= screen_width-32:
                    sides_2nd[1] = 0
                if pos_2 in brick_index or self.x + 32 >= screen_width-32:
                    sides_2nd[2] = 0
                if pos_3 in brick_index or self.y >= screen_height-32 or self.x >= screen_width-32:
                    sides_2nd[3] = 0
                if pos_4 in brick_index or self.y + 32 >= screen_height-32:
                    sides_2nd[4] = 0
                if pos_5 in brick_index or self.x <= 0 or self.y >= screen_height-32:
                    sides_2nd[5] = 0
                if pos_6 in brick_index or self.x - 32 <= 0:
                    sides_2nd[6] = 0
                if pos_7 in brick_index or self.y <= 0 or self.x <= 0:
                    sides_2nd[7] = 0

                if sides[0] == 1:
                    if sides_2nd[0] == 1 or sides_2nd[1] == 1 or sides_2nd[7] == 1:
                        sides_2nd_general[0] = 1
                if sides[1] == 1:
                    if sides_2nd[1] == 1 or sides_2nd[2] == 1 or sides_2nd[3] == 1:
                        sides_2nd_general[1] = 1
                if sides[2] == 1:
                    if sides_2nd[3] == 1 or sides_2nd[4] == 1 or sides_2nd[5] == 1:
                        sides_2nd_general[2] = 1
                if sides[3] == 1:
                    if sides_2nd[5] == 1 or sides_2nd[6] == 1 or sides_2nd[7] == 1:
                        sides_2nd_general[3] = 1

                if sides_2nd_general.count(1) >= 3:
                    block = 'D' # decision point
                else:
                    block = 'F' # fake/void decision point
            if sides.count(0) == 3:
                block = 'Z' # deadend
            if 2 in sides:
                block = 'G' #  target revealed
            if (self.x // 32, self.y // 32) == target:
                block = 'E'  # entering/ goal location

            return block

        def update(self):
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.y > 0:
                        if ((self.x/32, (self.y - 32)/32)) not in brick_index:
                            self.y -= 32
                            key_pressed = 'up'
                            timestamp = datetime.now(timezone.utc).astimezone()
                            coordinate = (self.x / 32) + 1, (self.y / 32) + 1
                            sides = self.cal_4_sides()
                            type = self.classify_blocks(sides)
                            #print(type)
                            line = ['nav', block_num, trial_num, key_pressed, timestamp, coordinate, type, maze_ID]
                            output_df.append(line)
                    if event.key == pygame.K_DOWN and self.y < screen_height-32:
                        if ((self.x/32, (self.y + 32)/32)) not in brick_index:
                            self.y += 32
                            key_pressed = 'down'
                            timestamp = datetime.now(timezone.utc).astimezone()
                            coordinate = (self.x / 32) + 1, (self.y / 32) + 1
                            sides = self.cal_4_sides()
                            type = self.classify_blocks(sides)
                            #print(type)
                            line = ['nav', block_num, trial_num, key_pressed, timestamp, coordinate, type, maze_ID]
                            output_df.append(line)
                    if event.key == pygame.K_LEFT and self.x > 0:
                        if ((self.x - 32)/32, self.y/32) not in brick_index:
                            self.x -= 32
                            key_pressed = 'left'
                            timestamp = datetime.now(timezone.utc).astimezone()
                            coordinate = (self.x / 32) + 1, (self.y / 32) + 1
                            sides = self.cal_4_sides()
                            type = self.classify_blocks(sides)
                            #print(type)
                            line = ['nav', block_num, trial_num, key_pressed, timestamp, coordinate, type, maze_ID]
                            output_df.append(line)
                    if event.key == pygame.K_RIGHT and self.x < screen_width-32:
                        if ((self.x + 32)/32, self.y/32) not in brick_index:
                            self.x += 32
                            key_pressed = 'right'
                            timestamp = datetime.now(timezone.utc).astimezone()
                            coordinate = (self.x / 32) + 1, (self.y / 32) + 1
                            sides = self.cal_4_sides()
                            type = self.classify_blocks(sides)
                            #print(type)
                            line = ['nav', block_num, trial_num, key_pressed, timestamp, coordinate, type, maze_ID]
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

    pygame.event.clear() # clear events when initializing a maze
    load = []
    remove = []
    player = Player(0, 0) # initial x y coordinate for a player is always [0 0]
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

    # logging initial position
    start_time = datetime.now(timezone.utc).astimezone()
    start_loc = (1.0, 1.0)
    line = ['nav', block_num, trial_num, 'start', start_time, start_loc, 'X', maze_ID]
    output_df.append(line)

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

        display.blit(pygame.transform.scale(screen, (screen_width * 2, screen_height * 2)), ((width / 2) - screen_width, (height / 2) - screen_height))  # (0,0)
        pygame.display.flip()
    time.sleep(1) # display stays for 1sec after entering the goal location

def run_guess(display, screen, trial_map, spr_tiles, background, block_num, trial_num, maze_ID):
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
                self.type = 3

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

    screen.blit(background, (0, 0))
    for obj in load:
        obj.draw()
        display.blit(pygame.transform.scale(screen, (screen_width * 2, screen_height * 2)), ((width / 2) - screen_width, (height / 2) - screen_height))  # (0,0)
    pygame.display.flip()

    # For a valid click, give a visual feedback & log the response
    pygame.event.clear()  # clear events first
    correctClick = False
    while not correctClick:
        events = pygame.event.get()
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for index in range(len(hidden_coor)):
                    if mouse_x in hidden_coor[index][0] and mouse_y in hidden_coor[index][1]:
                        guess_coor = ((hidden_coor[index][0][-1]+1-start_x) / 64, (hidden_coor[index][1][-1]+1-start_y) / 64) # or do not subtract
                        line = ['quiz', block_num, trial_num + 1, '', '', guess_coor, '', maze_ID]
                        output_df.append(line)
                        for obj in load:
                            if (obj.x / 32) + 1 == guess_coor[0] and (obj.y / 32) + 1 == guess_coor[1]:
                                obj.type = 3
                                obj.draw()
                                correctClick = True 
        display.blit(pygame.transform.scale(screen, (screen_width * 2, screen_height * 2)), ((width / 2) - screen_width, (height / 2) - screen_height))  # (0,0)
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

def render_text(surface, text, text_size, color):
    surface.fill((0, 0, 0))# 255, 255,255 (white), 0, 0, 0 (black) 196, 196, 196 (gray)
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

############## prepare stimuli ###########################
# associate each maze (layout) with a randomly-selected theme (shuffled)
random.shuffle(theme_strings)
new_layout = [layout[a] + (theme_strings[a],) for a in range(len(theme_strings))]

# maze assignment across blocks
# 8 mazes are learned over a chunk of 3 block [total 9 blocks, 24 mazes]
# a set of 8 mazes
# - equal number of goal locations in each quadrant (2 each)
# - repeated over 3 consecutive blocks

# Extract goal locations from maze_map, assign mazes to 3 sets while counterbalancing for which quadrant the goal is
goal_quad = []
for maze in range(len(layout)):
    goal = get_coord(layout[maze]) # gets target location
    goal_quad.append(get_quad(goal[0], goal[1], map_dimension))
goal_quad = np.array(goal_quad)
maze_idx = np.arange(len(goal_quad))
maze_set = counterbalance_maze_set(maze_idx, goal_quad)

############## prepare messages ###########################
instructText = {'inst_nav': "Navigate to find the goal object. Press a key to go proceed.",
                'inst_quiz': "Click at the goal object location. Press a key to go proceed.",
                'new_set': "You'll now visit NEW mazes! Press a key to go proceed.",
                'start': "Press a key to when you are ready to start.",
                'greatjob': 'You finished this block. Great Job!',
                'thankyou' : 'The experiment is finished, thank you for your participation.'
                }
text_color = (255, 255, 255) # 255, 255,255 (white), 0, 0, 0 (black)

pygame.init()
font = pygame.freetype.SysFont("freesansbold", 0)
display = pygame.display.set_mode((0,0,), pygame.FULLSCREEN)

block_num = 1
maze_seqs = []
for set in range(len(maze_set)):
    maze_seq = maze_set[set] # DO NOT SHUFFLE THIS
    maze_seqlist = maze_seq.tolist()
    if set > 0:
        display_message_key(display, instructText['new_set'], text_color)

    # repeat this set over nRepeat blocks - with maze order shuffled for each repetition
    for block in range(nRepeat):
        #-------------- NAVIGATION --------------#
        # message: starting navigation
        display_message_key(display, instructText['inst_nav'], text_color)
        display_message_key(display, instructText['start'], text_color)
        display.fill((0, 0, 0))
        pygame.mouse.set_visible(False)

        # randomize maze sequence, set up and run each trial
        rand_seq = random.sample(maze_seqlist, len(maze_seqlist))
        maze_seqs.append(['nav', rand_seq])
        for j in range(len(rand_seq)):
            # call map & agent for this trial
            player_name = maze_theme[new_layout[rand_seq[j]][7]][0]
            tiles_name = maze_theme[new_layout[rand_seq[j]][7]][1]
            background_name = maze_theme[new_layout[rand_seq[j]][7]][2]
            spr_player = pygame.image.load("assets/" + player_name + ".png").convert_alpha()
            spr_tiles = pygame.image.load("assets/" + tiles_name + ".png").convert_alpha()
            background = pygame.image.load("assets/" + background_name + ".jpg").convert()
            trial_map = layout[rand_seq[j]]
            maze_ID = rand_seq[j]
            # run a navigation trial
            run_trial(display, screen, trial_map, spr_player, spr_tiles, background, block_num, j, maze_ID)            # display = pygame.display.set_mode((0,0,), pygame.FULLSCREEN)
            photodiode_square(display)

        # -------------- QUIZ --------------#
        # messages
        display_message_key(display, instructText['inst_quiz'], text_color)
        display_message_key(display, instructText['start'], text_color)
        display.fill((0, 0, 0))
        pygame.mouse.set_visible(True)

        # randomize maze sequence and run quiz for this set
        rand_seq = random.sample(maze_seqlist, len(maze_seqlist))
        maze_seqs.append(['quiz', rand_seq])
        for j in range(len(rand_seq)):
            # call map for this trial
            tiles_name = maze_theme[new_layout[rand_seq[j]][7]][1]
            background_name = maze_theme[new_layout[rand_seq[j]][7]][2]
            spr_tiles = pygame.image.load("assets/" + tiles_name + ".png").convert_alpha()
            background = pygame.image.load("assets/" + background_name + ".jpg").convert()
            trial_map = layout[rand_seq[j]]
            maze_ID = rand_seq[j]
            # run a quiz trial
            run_guess(display, screen, trial_map, spr_tiles, background, block_num, j, maze_ID)
            photodiode_square(display)
        display_message_timed(display, instructText['greatjob'], text_color, 3)
        block_num += 1

# write out a logfile
for i in range(len(output_df)):
    if output_df[i][0] == 'nav':
        if output_df[i][3] == 'start':
            rt = 0
            output_df[i].append(rt)
        else:
            rt = str((output_df[i][4] - output_df[i-1][4]).total_seconds()*1000)
            output_df[i].append(rt)
for i in range(len(output_df)):
    if output_df[i][0] == 'nav':
        output_df[i][1] = str(output_df[i][1])

# save data logfile
df = pd.DataFrame(output_df)
os.chdir(filedir_data)
df.to_csv("%s_maze_log.csv" %(subjectID), header = ['task', 'block', 'trial','key_pressed', 'timestamp', 'coordinate', 'block_type', 'maze_ID', 'rt'], sep = ',')

# save sequences of mazes used
seq_df = pd.DataFrame(maze_seqs)
os.chdir(filedir_config)
seq_df.to_csv("%s_maze_seq.csv" %(subjectID), header = ['task', 'sequence'], sep = ',')

# save maze-theme association used
theme_df = pd.DataFrame(theme_strings)
os.chdir(filedir_config)
theme_df.to_csv("%s_maze_themes.csv" %(subjectID), header = ['theme'], sep = ',')

display_message_timed(display, instructText['thankyou'], text_color, 3)

