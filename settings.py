import os
import math
import pygame as pg

# defining colors
white = (255,255,255)
black = (0,0,0)
darkgrey = (40,40,40)
lightgrey = (100,100,100)
green = (0,255,0)
red = (255,0,0)
blue = (0,0,255)
yellow = (255,255,0)

# Map settings
tilesize = 32
plat_burn_delay = 50
#gridwidth = width/tilesize
#gridheight = height/tilesize
#plat settings

# Game settings
width = 1024
height = 704
fps = 60
title = "Crabby Patti vs The World"
bgcolor = black
#test enemies
enemies = [[{'gooey':1,'pgrunt':1}],[{'pgrunt':1, 'psuper':1,'rept':1}],[{'psuper':1,'rept': 1, 'baby':1}]]
#final enemies
'''enemies = [[{'pgrunt':5},{'pgrunt':4, 'psuper':2},{'pgrunt':2, 'psuper':4}],
            [{'pgrunt':4, 'psuper':4,}, {'pgrunt':4, 'psuper':4, 'flamey':1}, {'pgrunt':2, 'psuper':3,'rept':2,'flamey':2}],
            [{'psuper':2,'rept': 4, 'baby':1,'flamey':1}, {'psuper':2,'rept':4,'baby':2,'flamey':1}, {'rept':4, 'baby':4,'flamey':2}]]'''
enemy_types = ['pgrunt','psuper','flamey','rept','baby']
transition_time = 3000
level_time = 90
pb_pows = 3
walk_delay = 25
total_levels = 3
life_duration = 5000
life_spawn_time = 5000
life_q = 85
life_prob = 99
life_blink_delay = 200

# Player settings
player_acc = 6
player_fric = -1
player_grav = 1.8
player_jump = -35
player_image = ''
player_lives = 3
player_respawn_time = 3000
player_jump_delay = 50
player_input_delay = 4000

# Mob settings
mob_image = ''
mob_hit_rect = pg.Rect(0, 0, 32, 32)
mob_speed = 1.8
mob_spawn_vel = 1
mob_spawn_time = 4000
mob_flip_time = 4500
mob_mad_time = 3000
mob_jump = -2
mob_jump_delay = 1500
mob_jump_time = 400
mob_flame_time = 1500
mob_tremble_delay = 400

# Folders
game_fld = os.path.dirname(__file__)
media_fld = os.path.join(game_fld, 'media')
img_fld = os.path.join(media_fld, 'sprites')
blocks_fld = os.path.join(media_fld, 'blocks')
font_fld = os.path.join(media_fld, 'fonts')
sound_fld = os.path.join(media_fld, 'sfx')
