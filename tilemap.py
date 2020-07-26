import pygame as pg
from settings import *
vec = pg.math.Vector2

#collides hit rectangles of sprites instead of sprite images
#why is it in tilemap?
def collide_hit_rect(one,two):
    return one.hit_rect.colliderect(two.rect)

#game map created by parsing through map file (txt)
class Map:
    def __init__(self,filename):
        #filling a list with -letters?- that is passed on to the game to draw the map
        self.data = []
        with open(filename,'rt') as f:
            for line in f:
                self.data.append(line.strip())
        #setting map and tile size
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * tilesize
        self.height = self.tileheight* tilesize

#camera keeps player always centered on screen
class Camera:
    def __init__(self, mywidth, myheight):
        self.camera = pg.Rect(0, 0, mywidth, myheight)
        self.width = mywidth
        self.height = myheight

    #shifts every sprite around player movement
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        #follows player position around
        x = -target.rect.centerx + int(width / 2)
        y = -target.rect.centery + int(height / 2)

        # limits scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - width), x)  # right
        y = max(-(self.height - height), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)
