import pygame, time
import pandas as pd
import numpy as np
from pygame.locals import *
from datetime import datetime, timezone
pygame.display.init()
pygame.mixer.init()

# create the screen
screen_length = 288
screen_width = 224
display = pygame.display.set_mode((screen_length*2, screen_width*2))
screen = pygame.Surface((screen_length, screen_width))
pygame.display.set_caption("Maze")
output_df = []


maze_theme = {
    'face' : ['happyface', 'original2', 'milkywhite'],
    'dolphin' : ['dolphin', 'ocean', 'blue'],
    'monkey' : ['monkey', 'jungle', 'green'],
    'bird' : ['bird', 'sky', 'white'],
    'cow' : ['cow', 'pasture3', 'grassgreen']
}
# num_theme = 0
# maze_theme_list = list(maze_theme)
# player_name = maze_theme[maze_theme_list[num_theme]][0]
# tiles_name = maze_theme[maze_theme_list[num_theme]][1]
# background_name = maze_theme[maze_theme_list[num_theme]][2]

# spr_player = pygame.image.load("assets/" + player_name + ".png").convert_alpha()
# spr_tiles = pygame.image.load("assets/" + tiles_name + ".png").convert_alpha() 
# background = pygame.image.load("assets/" + background_name + ".jpg").convert()



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
                        coordinate = self.x / 32, self.y / 32
                        line = [key_pressed, str(timestamp), coordinate]
                        output_df.append(line)
                if event.key == pygame.K_DOWN and self.y < screen_width-32:
                    if ((self.x/32, (self.y + 32)/32)) not in brick_index:
                        self.y += 32
                        key_pressed = 'down'
                        timestamp = datetime.now(timezone.utc).astimezone()
                        coordinate = self.x / 32, self.y / 32
                        line = [key_pressed, str(timestamp), coordinate]
                        output_df.append(line)
                if event.key == pygame.K_LEFT and self.x > 0:
                    if ((self.x - 32)/32, self.y/32) not in brick_index:
                        self.x -= 32
                        key_pressed = 'left'
                        timestamp = datetime.now(timezone.utc).astimezone()
                        coordinate = self.x / 32, self.y / 32
                        line = [key_pressed, str(timestamp), coordinate]
                        output_df.append(line)
                if event.key == pygame.K_RIGHT and self.x < screen_length-32:
                    if ((self.x + 32)/32, self.y/32) not in brick_index:
                        self.x += 32
                        key_pressed = 'right'
                        timestamp = datetime.now(timezone.utc).astimezone()
                        coordinate = self.x / 32, self.y / 32
                        line = [key_pressed, str(timestamp), coordinate]
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



from Maze_map import *





room_num = 0
run = True
while run:
    ### level generation

    load = []
    remove = []
    player = Player(0,0)
    start_time = datetime.now(timezone.utc).astimezone()
    start_loc = (0.0, 0.0)
    line = ['start', str(start_time), start_loc]
    output_df.append(line)
    hidden_block_index = []
    brick_index = []
    target = ()

    player_name = maze_theme[layout[room_num][7]][0]
    tiles_name = maze_theme[layout[room_num][7]][1]
    background_name = maze_theme[layout[room_num][7]][2]

    spr_player = pygame.image.load("assets/" + player_name + ".png").convert_alpha()
    spr_tiles = pygame.image.load("assets/" + tiles_name + ".png").convert_alpha() 
    background = pygame.image.load("assets/" + background_name + ".jpg").convert()


    for i in range(len(layout[room_num])):
        for j in range(len(layout[room_num][i])):
            if layout[room_num][i][j] == "P":
                player = Player(j*32, i*32)
                load.append(player)
            if layout[room_num][i][j] == "0":
                load.append(Terrain(j*32, i*32, 0))
                brick_index.append((j,i))
            if layout[room_num][i][j] == "1":
                load.append(Terrain(j*32, i*32, 1))
                hidden_block_index.append((j,i))
            if layout[room_num][i][j] == "2":
                load.append(Terrain(j*32, i*32, 1))
                target = (j,i)
     


    alive = True
    while run and alive:

        screen.blit(background, (0, 0))

        # event is your mouse movement, if press "x", quit the game
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
           

        for obj in load:
            obj.update()
            obj.draw()
        for obj in remove:
            load.remove(obj)
        remove = []
        
        if (round(player.x / 32), round(player.y / 32)) == target:
            alive = False
            


        display.blit(pygame.transform.scale(screen, (screen_length*2, screen_width*2)),(0, 0))
        pygame.display.flip()


    if (round(player.x / 32), round(player.y / 32)) == target:
        room_num += 1
     
    df = pd.DataFrame(output_df)
    df.to_csv('output.txt', header = ['key_pressed', 'timestamp', 'coordinate'], sep = '\t')
pygame.quit()



