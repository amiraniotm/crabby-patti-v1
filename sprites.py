import pygame as pg
from settings import *
from tilemap import collide_hit_rect
vec = pg.math.Vector2
import random
import xml.etree.ElementTree as ET

#method for colliding any sprite with the game platforms
#it sets sprite pos to the edge of the collided sprite in group (here platform) and
#sets velocity to 0, movement direction must be passed
def collide_with_platforms(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            #here its established if a sprite center is above a platform center, so it can keep moving linearly while colliding on edges
            if (hits[0].rect.centery - sprite.rect.centery) > 5:
                sprite.above = True
            else: sprite.above = False
            if not sprite.above:
                if sprite.vel.x > 0:
                    sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
                if sprite.vel.x < 0:
                    sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
                sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if sprite in sprite.game.mobs:
                if sprite.exploding:
                    sprite.explode()
            if sprite.vel.y > 0:
                sprite.pos.y = hits[0].rect.top - ((sprite.hit_rect.height / 2) - 1)
                sprite.isjump = False
            if sprite.vel.y < 0:
                sprite.pos.y = hits[0].rect.bottom + ((sprite.hit_rect.height / 2) + 1)
                #when player hits platform from below, 'flopped' state changes and allows platform to flip enemies
                for hit in hits:
                    hit.floptime = pg.time.get_ticks()
                    hit.flopped = True
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y
            return True
        else: return False

def jump(sprite):
    if sprite in sprite.game.players:
        #pg.mixer.Sound.play(sprite.jumpsound)
        sprite.isjump = True
        sprite.midair = True
        if not sprite.slowed:
            sprite.vel.y = player_jump
        else:
            sprite.vel.y = player_jump * 0.8
        sprite.image = sprite.game.spritesheet.get_image('patti_jump')
    else:
        now = pg.time.get_ticks()
        if now - sprite.jumpies > mob_jump_delay:
            sprite.jumpies = now
            sprite.vel.y = mob_jump
            if not sprite.left:
                sprite.vel.x = mob_speed
                sprite.image = sprite.game.spritesheet.get_image('baby_up')
            else:
                sprite.vel.x = -mob_speed
                sprite.image = pg.transform.flip(sprite.game.spritesheet.get_image('baby_up'),True,False)
            sprite.isjump = True
            sprite.jumpstart = pg.time.get_ticks()
        else:
            sprite.standing = True
            sprite.vel = vec(0,0)
    sprite.standing = False
    sprite.jumptime = 0

#cycling through walking sprites
def walk(sprite):
    now = pg.time.get_ticks()
    if sprite.walkcount + 1 >= (20 if sprite.type in ['patti','flamey','rept','gooey'] else 40):
        sprite.walkcount = 0
    if not sprite.standing and not sprite.midair:
        if now - sprite.walkies > walk_delay:
            sprite.walkies = now
            sprite.image = sprite.walk_sprites[sprite.walkcount//10]
            sprite.walkcount += 2
            if sprite not in sprite.game.players:
                if sprite.mad:
                    try:
                        sprite.image = sprite.mad_sprites[sprite.walkcount//10]
                        sprite.walkcount += 2
                    except:
                        sprite.walkcount = 0
                sprite.rect = sprite.image.get_rect()
                sprite.rect.center = sprite.pos
                sprite.hit_rect.center = sprite.rect.center
            if sprite.left:
                sprite.image = pg.transform.flip(sprite.image,True,False)
    elif sprite.kicking:
        if pg.time.get_ticks() - sprite.kicktime < 300:
            sprite.image = sprite.game.spritesheet.get_image('patti_attack')
            sprite.kicking = False

def item_probs(caller,itemprob):
    prob_life = random.randrange(0,100)
    prob_loc = random.randrange(1,100*len(caller.game.life_locations))
    life_loc = None
    if prob_life < itemprob:
        for i in range(len(caller.game.life_locations)):
            if (i*100 + 1) < prob_loc < ((i+1)*100 + 1):
                life_loc = caller.game.life_locations[i]
    return life_loc

class Spritesheet():

    def __init__(self,filename,game):
        self.game = game
        self.spritesheet = pg.image.load(filename).convert_alpha()
        self.tree = ET.parse(os.path.join(img_fld,'spritesheet.xml'))
        self.root = self.tree.getroot()

    def get_image(self,name):
        for child in self.root.findall('SubTexture'):
            if child.get('name') == name:
                x = int(child.get('x'))
                y = int(child.get('y'))
                iwidth = int(child.get('width'))
                iheight = int(child.get('height'))
        image = pg.Surface((iwidth,iheight),flags = pg.SRCALPHA)
        image.convert_alpha()
        image.blit(self.spritesheet, (0,0),(x,y,iwidth,iheight))
        chara = ['patti','baby','pgrunt','psuper','rept']
        for char in chara:
            if char in name:
                image = pg.transform.scale(image,(int(image.get_width()*1.3),int(image.get_height()*1.2)))
        return image

    def get_image_list(self,sprite,action,spriteType,status = None):
        if (sprite in sprite.game.players) or (sprite in sprite.game.mobs):
            s_list = []
            if action == 'walk':
                if spriteType in ['patti','rept', 'flamey', 'gooey']:
                    for i in range(1,3):
                        if status == None:
                            s_list.append(sprite.game.spritesheet.get_image(spriteType + '_walk_' + str(i)))
                        elif status == 'mad':
                            s_list.append(sprite.game.spritesheet.get_image(spriteType + '_mad_' + str(i)))
                elif spriteType in ['pgrunt', 'psuper']:
                    for i in range(1,5):
                        s_list.append(sprite.game.spritesheet.get_image(spriteType + '_walk_' + str(i)))
        return s_list

#the player sprite is the effector of the real life player inputs
class Player(pg.sprite.Sprite):

    def __init__(self, game, x, y):
        self._layer = 2
        self.groups = game.all_sprites, game.players
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = 'patti'
        self.image = self.game.spritesheet.get_image('patti_stand')
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * tilesize
        self.rect.y = y * tilesize
        self.hit_rect = pg.Rect(0,0,int(self.image.get_width()*0.7),int(self.image.get_height()*0.7))
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.acc = vec(0,0)
        self.pos = vec(x, y) * tilesize
        self.inipos = (x*tilesize, y*tilesize)
        self.isjump = False
        self.jumptime = 0
        self.midair = False
        self.above = False
        self.lives = player_lives - self.game.lives_spent
        self.rsp = True
        self.rsptime = 0
        self.standing = True
        self.walkcount = 0
        self.walk_sprites = self.game.spritesheet.get_image_list(self,'walk',self.type)
        self.stand = self.game.spritesheet.get_image('patti_stand')
        #self.jumpsound = self.game.sfx['jump.wav']
        #self.fallsound = self.game.sfx['player_fall.wav']
        self.left = False
        self.ded = False
        self.walkies = 0
        self.kicking = False
        self.kicktime = 0
        self.mask = pg.mask.from_surface(self.image)
        self.slowed = False
        self.mad = False
        self.rplat = Platform(self.game,(self.rect.left/tilesize) - 1,(self.rect.bottom/tilesize)-0.3,'9')

    #keyboard input mapping
    def get_keys(self):
        self.standing = True
        #jumping
        #moving left
        if self.rsp == True and (pg.time.get_ticks() - self.rsptime) < player_respawn_time and not self.isjump:
            pass
        else:
            keys = pg.key.get_pressed()
            if keys[pg.K_a] or keys[pg.K_LEFT]:
                self.acc.x = -player_acc
                self.standing = False
                '''self.right = False
                self.left = True'''
            #moving right
            if keys[pg.K_d] or keys[pg.K_RIGHT]:
                pg.key.set_repeat(200,100)
                self.acc.x = player_acc
                self.standing = False
                '''self.left = False
                self.right = True'''

    def die(self):
        self.ded = True
        self.lives -= 1
        self.game.lives_spent += 1
        self.isjump = False

    #method for respawning after unflipped enemy hit
    def revive(self):
        self.image = self.stand
        self.ded = False
        if self.lives > 0:
            self.rsptime = pg.time.get_ticks()
            self.rsp = True
            self.pos.y = self.inipos[1]
            self.pos.x = self.inipos[0]
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = vec(0,0)
            self.vel = vec(0,0)
            self.rplat = Platform(self.game,self.rect.left/tilesize,self.rect.bottom/tilesize,'9')
        #quits game when life counter hits 0
        else:
            self.game.playing = False

    #continually updates position, velocity and acceleration in response to events
    def update(self):
        #applying gravity to player and making its x velocity 0 if no inputs
        self.acc = vec(0,player_grav)
        #collecting key presses
        self.get_keys()
        #update of position,acceleration,velocity and rect position
        if not self.slowed:
            self.acc.x += self.vel.x * player_fric
        else:
            self.acc.x += self.vel.x * player_fric * 1.8
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        walk(self)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        #edge of screen roundabout
        if self.pos.x > width:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = width
        #continually collide with platforms so sprites dont pass through
        if not self.ded:
            self.hit_rect.centerx = self.pos.x
            collide_with_platforms(self, self.game.platforms, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_platforms(self, self.game.platforms, 'y')
            self.rect.center = self.hit_rect.center
            if collide_with_platforms(self, self.game.platforms, 'y') and pg.sprite.spritecollide(self,self.game.platforms,False)[0].charred:
                self.slowed = True
            else:
                self.slowed = False
        else:
            self.pos.y += 5
            self.image = self.game.spritesheet.get_image('patti_ded')
            if self.pos.y >= self.game.map.height:
                self.revive()
        #checks if sprite is falling so it cant jump midair
        if self.vel.y > 0:
            self.midair = True
        else: self.midair = False
        #midair stasis on respawn (sprite dont move unless time passes or key pressed)
        if self.rsp == True and (pg.time.get_ticks() - self.rsptime) < player_respawn_time and not self.isjump:
            self.pos.y = self.inipos[1]
            self.pos.x = self.inipos[0]
            self.acc = vec(0,0)
            self.vel = vec(0,0)
            self.midair = False
        else:
            self.rsp = False
            self.rplat.kill()
        if self.vel.x > 0:
            self.left = False
        else:
            self.left = True

#enemies that have to be beaten to win the game
class Mob(pg.sprite.Sprite):

    def __init__(self, game, spoint, x, y, type):
        self._layer = 2
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.spoint = spoint
        self.type = type
        self.image = self.game.spritesheet.get_image(type+'_walk_1')
        if self.spoint.x*tilesize > width/2:
            self.image = pg.transform.flip(self.image,True,False)
        self.rect = self.image.get_rect()
        self.hit_rect = pg.Rect(0,0,int(self.image.get_width()*0.7),int(self.image.get_height()*0.7))
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y) * tilesize
        self.vel = vec(0, 0)
        self.rect.center = self.pos
        self.standing = True
        self.midair = True
        self.isjump = True
        self.jumptime = 0
        self.above = False
        self.spawning = True
        self.flipped = False
        self.fliptime = 0
        self.flippable = True
        self.iniy = 0
        self.inix = 0
        self.kicked = False
        self.mad = False
        self.left = False
        #self.hitsound = self.game.sfx['hit_enemy.wav']
        self.walk_sprites = self.game.spritesheet.get_image_list(self,'walk',self.type)
        if type in ['rept', 'flamey', 'gooey']:
            self.mad_sprites = self.game.spritesheet.get_image_list(self,'walk',self.type,'mad')
        self.walkcount = 0
        self.jumpies = 0
        self.jumpstart = 0
        self.kicking = False
        self.walkies = 0
        self.crashing = False
        self.exploding = False
        self.mask = pg.mask.from_surface(self.image)
        self.tremble_time = 0

    #controls every move action and interaction of the sprite
    def move(self):
        #collision with player
        hit = pg.sprite.spritecollide(self, self.game.players, False)
        if hit:
            if self.flipped and not self.type in ['flamey','gooey']:
                hit[0].kicking = True
                hit[0].kicktime = pg.time.get_ticks()
                pg.display.flip()
                self.kicked = True
                if self.type == 'pgrunt':
                    points = 10
                elif self.type == 'psuper':
                    points = 20
                elif self.type == 'rept':
                    points = 40
                elif self.type == 'baby':
                    points = 50
                self.game.player_score += points
            else:
                if not hit[0].ded:
                    hit[0].die()
                #hit[0].fallsound.play()
        #slows down and mantains midair if spawning
        if abs(self.rect.centerx - self.spoint.rect.centerx) > 100:
            self.spawning = False
        if self.vel.y < 0:
            if self.jumpstart != 0 and (pg.time.get_ticks() - self.jumpstart) > mob_jump_time:
                self.midair = True
        if self.spawning:
            self.vel = vec(mob_spawn_vel,0)
            if self.spoint.pos.x > width/2:
                self.vel.x = self.vel.x * -1
        #stops sprite while flipped
        elif self.flipped:
            self.vel = vec(0,0)
            #restarts movement if time has passed
            if (pg.time.get_ticks() - self.fliptime) > mob_flip_time/2:
                self.tremble()
            if (pg.time.get_ticks() - self.fliptime) > mob_flip_time:
                self.flipped = False
                self.fliptime = 0
                self.inix = 0
                self.image = self.game.spritesheet.get_image(self.type+'_walk_1')
        #controls fall
        else:
            if self.midair:
                self.vel = vec(mob_speed,player_grav)
                if self.type == 'baby':
                    self.image = self.game.spritesheet.get_image('baby_down')
                if self.left:
                    self.vel = vec(-mob_speed,player_grav)
                    if self.type == 'baby':
                        self.image = pg.transform.flip(self.game.spritesheet.get_image('baby_down'),True,False)
            if not self.midair and not self.flipped:
                if self.type == 'pgrunt':
                    self.vel.x = mob_speed
                elif self.type == 'psuper':
                    self.vel.x = mob_speed*1.5
                elif self.type == 'rept':
                    if not self.mad:
                        self.vel.x = mob_speed*2
                    else:
                        self.vel.x = mob_speed*2.2
                        if (pg.time.get_ticks() - self.fliptime) > mob_mad_time:
                            self.mad = False
                            self.fliptime = 0
                elif self.type in ['flamey','gooey']:
                    if not self.mad:
                        self.vel.x = mob_speed
                    else:
                        self.vel.x = mob_speed*1.5
                        if (pg.time.get_ticks() - self.fliptime) > mob_mad_time:
                            self.exploding = True
                self.crash()
                if self.left:
                    self.vel.x *= -1
                if self.type != 'baby':
                    walk(self)
                if self.type == 'baby' and not self.isjump:
                    jump(self)
                #inverts speed from enemies spawning from the right (left-wards)
                #edge of screen rondabout and respawing upon reaching bottom and edges
        if self.pos.x > width:
            if (self.game.map.height - self.rect.centery) < 96 :
                self.respawn()
            else:
                self.pos.x = 0
        if self.pos.x < 0:
            if (self.game.map.height - self.rect.centery) < 96 :
                self.respawn()
            else:
                self.pos.x = width

    def tremble(self):
        now = pg.time.get_ticks()
        if now - self.tremble_time > mob_tremble_delay:
            if self.pos.x == self.inix:
                self.pos.x += 3
            elif self.pos.x > self.inix:
                self.pos.x -= 3
            self.tremble_time = now

    def explode(self):
        hit = pg.sprite.spritecollide(self,self.game.platforms,False)
        if hit:
            hit[0].dmg = self.type
            hit[0].origin = True
            hit[0].charred = True
            self.kill()

    def crash(self):
        mobhit = pg.sprite.spritecollide(self, self.game.mobs, False)
        if mobhit and mobhit[0]!=self:
            if not (mobhit[0].midair or self.midair):
                if not self.crashing:
                    self.crashing = True
                    if mobhit[0].left and not self.left:
                        mobhit[0].left = False
                        self.left = True
                    elif self.left and not mobhit[0].left:
                        mobhit[0].left = True
                        self.left = False
        else:
            self.crashing = False

    #after reaching the bottom platform and one of the edges, sprite will reappear on spawn point
    def respawn(self):
        if self.mad:
            self.mad = False
        if self.spoint.x*tilesize > width/2:
            self.left = True
            self.image = pg.transform.flip(self.game.spritesheet.get_image(self.type+'_walk_1'),True,False)
        else:
            self.left = False
            self.image = self.game.spritesheet.get_image(self.type+'_walk_1')
        self.pos.y = self.spoint.rect.centery
        self.pos.x = self.spoint.rect.centerx
        self.spawning = True
        self.standing = True

    #if sprite is on top of platform thats been hit by player from below, it will stop moving and become vulnerable
    def flip(self):
        if self.flippable:
            #self.hitsound.play()
            self.fliptime = pg.time.get_ticks()
            self.flippable = False
            if not self.flipped:
                if self.type != 'rept' and self.type not in ['flamey','gooey']:
                    self.image = self.game.spritesheet.get_image(self.type+'_ded')
                    self.flipped = True
                    if self.left:
                        self.image = pg.transform.flip(self.image, True, False)
                elif self.type == 'rept' and self.mad:
                    self.image = self.game.spritesheet.get_image(self.type+'_ded')
                    if self.left:
                        self.image = pg.transform.flip(self.image, True, False)
                    self.flipped = True
                elif self.type == 'rept' and not self.mad:
                    self.mad = True
            else:
                self.flipped = False
                self.image = self.game.spritesheet.get_image(self.type+'_walk_1')

    #constant update of major status changes
    def update(self):
        #prevents the sprite from being flipped/unflipped by contiguous platforms
        if self.flippable == False and self.fliptime != 0 and (pg.time.get_ticks() - self.fliptime) > 200:
            self.flippable = True
        #completes jump animation when flipped (initiated by Platform)
        if (self.iniy != 0 and self.midair) and (self.flipped or self.mad):
            if self.type in ['flamey','gooey']:
                if (pg.time.get_ticks() - self.fliptime) < mob_flame_time:
                    self.vel = vec(0,0)
                    if not self.mad:
                        self.image = self.game.spritesheet.get_image(self.type + '_stat')
                    else:
                        self.image = self.game.spritesheet.get_image(self.type + '_ded')
                    self.rect = self.image.get_rect()
                    self.rect.center = self.pos
                else:
                    if self.mad:
                        self.ded = True
                        self.kill()
                        self.game.player_score += 35
                        self.game.counter.living_enemies -= 1
                    else:
                        self.pos.y += 10
                        self.flipped = False
                        self.mad = True
                        self.iniy = 0
                        self.vel = vec(mob_speed*1.2,0)
                        self.rect = self.image.get_rect()
                        self.rect.center = self.pos
            else:
                self.pos.y += 10
        #kickout mechanics: kicked = flipped + player collision
        if not self.kicked:
            self.move()
        else:
            self.pos.y += 5
            if self.pos.y >= self.game.map.height:
                self.kill()
                self.game.counter.living_enemies -= 1
        #update of pos and rect pos
        self.pos += self.vel
        self.rect.center = self.pos
        self.hit_rect.center = self.rect.center
        self.hit_rect.centerx = self.pos.x
        #continually collide with platforms so sprites dont pass through
        collide_with_platforms(self, self.game.platforms, 'x')
        self.hit_rect.centery = self.pos.y
        #checking if sprite is falling
        collide_with_platforms(self, self.game.platforms, 'y')
        if collide_with_platforms(self, self.game.platforms, 'y'):
            self.midair = False
            self.standing = False
        else:
            if self.type != 'baby':
                self.midair = True

#platforms where sprites can stand
class Platform(pg.sprite.Sprite):

    def __init__(self, game, x, y, subgroup):
        self._layer = 1
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        if subgroup != '9':
            if self.game.level == 1:
                self.image = self.game.spritesheet.get_image('beach_plat')
            elif self.game.level == 2:
                self.image = self.game.spritesheet.get_image('volcano_plat')
            elif self.game.level == 3:
                self.image = self.game.spritesheet.get_image('city_plat')
        else:
            self.image = self.game.spritesheet.get_image('revive_plat')
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.pos = vec(x,y) * tilesize
        self.rect.x = x * tilesize
        self.rect.y = y * tilesize
        self.floptime = 0
        self.flopped = False
        self.subgroup = subgroup
        self.charred = False
        self.chartime = 0
        self.charcount = 1
        self.origin = False
        self.subg = []
        self.c_right = []
        self.c_left = []
        self.mask = pg.mask.from_surface(self.image)
        self.dmg = ''

    #when platform is hit from below, it flips any enemy above it
    def flop(self):
        if self.flopped:
            self.pos.y -= 5
            self.flopped = False
            #flip animation is started on any mobs above
            hits = pg.sprite.spritecollide(self, self.game.mobs, False)
            if hits:
                for hit in hits:
                    hit.pos.y -= 10
                    hit.iniy = hit.pos.y
                    hit.inix = hit.pos.x
                    hit.flip()
                    if hit.type in ['flamey','gooey']:
                        hit.flipped = True

    def burn_plats(self):
        if self.subg == []:
            for plat in self.game.platforms:
                if plat.subgroup == self.subgroup and not plat == self:
                    plat.dmg = self.dmg
                    self.subg.append(plat)
            for pt in self.subg:
                for i in range(len(self.subg) + 1):
                    if pt.rect.centerx == self.rect.centerx + i*tilesize:
                        self.c_right.append(pt)
                    if pt.rect.centerx == self.rect.centerx - i*tilesize:
                        self.c_left.append(pt)
        now = pg.time.get_ticks()
        if now - self.chartime > plat_burn_delay:
            for ptl in self.c_left:
                if ptl.rect.centerx == self.rect.centerx - self.charcount*tilesize:
                    if self.game.lethals:
                        for f in self.game.lethals:
                            if f.dir == 'left':
                                f.kill()
                    debris = Debris(self.game,ptl.rect.centerx,ptl.rect.centery - tilesize,ptl.dmg,'left')
                    debris.image = pg.transform.flip(debris.image,True,False)
                    ptl.charred = True
                    if pg.sprite.spritecollide(self.game.player,self.game.lethals,False) and not self.game.player.ded:
                        self.game.player.die()
                    self.subg.pop(self.subg.index(ptl))
            for ptr in self.c_right:
                if ptr.rect.centerx == self.rect.centerx + self.charcount*tilesize:
                    if self.game.lethals:
                        for f in self.game.lethals:
                            if f.dir == 'right':
                                f.kill()
                    debris = Debris(self.game,ptr.rect.centerx,ptr.rect.centery - tilesize,ptr.dmg,'right')
                    ptr.charred = True
                    if pg.sprite.spritecollide(self.game.player,self.game.lethals,False) and not self.game.player.ded:
                        self.game.player.die()
                    self.subg.pop(self.subg.index(ptr))
            self.charcount += 1
            self.chartime = now
            if self.subg == []:
                self.game.counter.living_enemies -= 1
                self.origin = False
                for f in self.game.lethals:
                    f.kill()

    #checks for flops and updates position and rect position if any
    def update(self):
        self.flop()
        self.rect.centery = self.pos.y
        if self.floptime != 0 and (pg.time.get_ticks() - self.floptime) > 100:
            self.pos.y += 5
            self.floptime = 0
        if self.charred:
            self.image = self.game.spritesheet.get_image(self.dmg+'_plat')
        if self.origin:
            self.burn_plats()

#points where enemies are generated and where they come back to
class SpawnPoint(pg.sprite.Sprite):

    def __init__(self, game, x, y, active):
        self._layer = 2
        self.groups = game.all_sprites, game.utilities
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = x
        self.y = y
        self.image = self.game.spritesheet.get_image('spawn_point_1')
        self.image = pg.transform.scale(self.image,(self.image.get_width()*2,self.image.get_height()*2))
        if self.x*tilesize > width/2:
            self.image = pg.transform.flip(self.image,True, False)
        self.rect = self.image.get_rect()
        self.pos = vec(x, y) * tilesize
        self.rect.x = x * tilesize
        self.rect.y = y * tilesize
        self.start = False
        self.stime = 0
        self.active = active
        self.spawning = 0

    #creates a mob (enemy)
    def spawn(self,type):
        if self.game.counter.enemy_count != 0 and self.active:
            nmob = Mob(self.game,self,self.x,self.y,type)
            if self.x*tilesize < width/2:
                nmob.left = False
            else:
                nmob.left = True
            self.stime = pg.time.get_ticks()
            self.game.counter.enemy_count += -1

#general counter for the game (only counts enemies for now)
class Counter(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.counters
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((32,32))
        self.game = game
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.pos = vec(x,y) * tilesize
        self.rect.center = self.pos
        self.stage = 0
        self.level_enemies = enemies[self.game.level - 1]
        self.living_enemies = 0
        self.enemy_count = 0
        self.extra = False
        self.total_enemies = 0

    def send_mob(self,sp):
        for key in self.stage_enemies.keys():
            if self.stage_enemies[key] != 0:
                sp.spawn(key)
                self.stage_enemies[key] -= 1
                break

    def lifecheck(self):
        if self.game.player.lives < player_lives:
            if self.game.cdown < life_q:
                if self.living_enemies < self.total_enemies:
                    if not self.extra:
                        self.send_life()

    def send_life(self):
        prob = item_probs(self,life_prob)
        if prob == None:
            pass
        else:
            Life(self.game,prob.x,prob.y)
            self.extra = True

    def next_stage(self):
        self.stage += 1
        self.game.cdown = 90
        if self.stage > len(self.level_enemies):
            self.game.level += 1
            if self.game.level > total_levels:
                self.game.playing = False
            else:
                self.game.show_go_screen('level')
            return
        tr_time = pg.time.get_ticks()
        self.game.player.pos = self.game.player.inipos
        self.game.player.rect.center = self.game.player.pos
        self.stage_enemies = self.level_enemies[self.stage - 1].copy()
        self.game.draw()
        self.game.draw_text('Stage ' + str(self.game.level) + ' - ' + str(self.stage), 26, white, width / 2, height / 2)
        pg.display.flip()
        pg.time.wait(transition_time)
        self.game.start_tick = pg.time.get_ticks()/1000
        self.game.clock.tick(fps)
        self.game.started = True
        for x in self.stage_enemies.values():
            self.living_enemies += x
            self.enemy_count += x
            self.total_enemies += x

    def update(self):
        if self.living_enemies == 0:
            self.next_stage()

#special tile: when hit from below by player, flips any mob on a platform
class PowBlock(pg.sprite.Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        self.game = game
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = self.game.spritesheet.get_image('powblock_1')
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.pos = vec(x, y) * tilesize
        self.rect.x = x * tilesize
        self.rect.y = y * tilesize
        self.pows = pb_pows

    #flips/unflips any mob on a platform and lowers internal counter
    def pow(self):
        if self.pows != 0:
            for mob in self.game.mobs:
                if not mob.midair:
                    if mob.type != 'baby':
                        mob.pos.y += -10
                        mob.iniy = mob.pos.y
                        mob.inix = mob.pos.x
                        mob.flip()
                    else:
                        if not mob.isjump:
                            mob.pos.y += -10
                            mob.iniy = mob.pos.y
                            mob.inix = mob.pos.x
                            mob.flip()
                    if mob.type in ['flamey','gooey']:
                        mob.flipped = True
        self.pows -= 1

    #checks for collisions with player and keeps it away if collided
    def update(self):
        hit = pg.sprite.collide_mask(self,self.game.player)
        if hit and self.game.player.vel.y < 0:
            self.game.player.pos.y = self.rect.bottom + self.game.player.hit_rect.height
            self.game.player.isjump = False
            self.game.player.midair = True
            self.game.player.vel.y = 0
            self.game.player.hit_rect.centery = self.game.player.pos.y
            self.pow()
        if self.pows == 2:
            self.image = self.game.spritesheet.get_image('powblock_2')
        if self.pows == 1:
            self.image = self.game.spritesheet.get_image('powblock_3')
        #disappears if internal counter hits 0
        if self.pows == 0:
            self.kill()

class Debris(pg.sprite.Sprite):

    def __init__(self, game, x, y, type, dir):
        self.groups = game.all_sprites,game.lethals
        self.game = game
        self.dir = dir
        pg.sprite.Sprite.__init__(self, self.groups)
        if type == 'flamey':
            self.image = self.game.spritesheet.get_image('fire_2')
        else:
            self.image = self.game.spritesheet.get_image('goo')
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
        self.rect.center = self.pos

class Life(pg.sprite.Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        self.game = game
        pg.sprite.Sprite.__init__(self,self.groups)
        self.image = self.game.spritesheet.get_image('patti_life')
        self.rect = self.image.get_rect()
        self.pos = vec(x*tilesize,y*tilesize)
        self.rect.center = self.pos
        self.duration = life_duration
        self.spawntime = pg.time.get_ticks()
        self.blink_time = 0
        self.transparent = False

    def blink(self):
        now = pg.time.get_ticks()
        if now - self.blink_time > life_blink_delay:
            if not self.transparent:
                self.image = pg.Surface((32,32))
                self.image.fill(black)
                self.image.set_colorkey(black)
                self.transparent = True
            else:
                self.image = self.game.spritesheet.get_image('patti_life')
                self.transparent = False
            self.blink_time = now

    def update(self):
        if abs(self.spawntime - pg.time.get_ticks()) > self.duration / 2:
            self.blink()
        if abs(self.spawntime - pg.time.get_ticks()) > self.duration:
            self.kill()
        if pg.sprite.spritecollide(self,self.game.players,False):
            self.kill()
            self.game.player.lives += 1
            self.game.lives_spent -= 1
