import pygame as pg
import random
import sys
import six
vec = pg.math.Vector2
#only for packing
#import packaging
from settings import *
from sprites import *
from tilemap import *

# Classes
class Game:
    #main class of the game, contains and initializes fundamental objects (clock, screen, etc) and controls load, main loop and quitting of the game
    def __init__(self):
        pg.init()
        #pg.mixer.pre_init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((width, height))
        self.clock = pg.time.Clock()
        self.paused = False
        self.cdown = level_time
        self.level = 1
        self.playing = False
        self.lives_spent = 0
        self.start_tick = 0
        self.player_score = 0
        self.started = False
        self.life_locations = []
        self.load_data()

    #initial data loading. Folder mapping can be done here but is done instead in the settings file
    #game_fld = os.path.dirname(__file__)
    #img_fld = os.path.join(game_fld, 'sprites')
    #player_fld = os.path.join(img_fld, 'char')

    def load_data(self):
        self.spritesheet = Spritesheet(os.path.join(img_fld,'spritesheet.png'),self)
        with open(os.path.join(game_fld,'highscore.txt'),'w') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

    #initializes new objects: sprite groups and sprites
    def new(self,level):
        self.map = Map(os.path.join(game_fld,'map32.txt'))
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.players = pg.sprite.Group()
        self.utilities = pg.sprite.Group()
        self.lethals = pg.sprite.Group()
        self.counters = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile in ['0','1','2','3','4','5','6','7','8','9']:
                    Platform(self, col, row, tile)
                if tile == 'B':
                    if level == 1:
                        if row < 16:
                            self.pb1 = PowBlock(self,col,row)
                        else:
                            self.pb2 = PowBlock(self,col,row)
                if tile == 'P':
                    self.player = Player(self, col, row)
                if tile == 'S':
                    if col < 16:
                        self.sp1 = SpawnPoint(self, col, row, True)
                    else:
                        self.sp2 = SpawnPoint(self, col, row, False)
                if tile == 'C':
                    self.counter = Counter(self, col, row)
                if tile == 'L':
                    self.life_locations.append(vec(col,row))
        self.camera = Camera(self.map.width, self.map.height)
        self.mob_spawnevent = pg.USEREVENT + 1
        self.life_spawnevent = pg.USEREVENT + 2
        pg.time.set_timer(self.mob_spawnevent, mob_spawn_time)
        pg.time.set_timer(self.life_spawnevent, life_spawn_time)
        if self.level > 1:
            if self.pb1.pows > 0:
                self.all_sprites.add(self.pb1)
            if self.pb2.pows > 0:
                self.all_sprites.add(self.pb2)
        if self.level == 1:
            self.bg = self.spritesheet.get_image('beach_bg')
        elif self.level == 2:
            self.bg = self.spritesheet.get_image('volcano_bg')
        elif self.level == 3:
            self.bg = self.spritesheet.get_image('city_bg')

    #standard finishing method - as seen on the internet
    def quit(self):
        pg.quit()
        sys.exit()

    #executes every single sprite update routine and controls where (to whom) camera is pointed
    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)
        if self.started:
            self.dt = self.clock.tick(fps) / 1000.0
            self.cdown -= self.dt
            if self.cdown <= 0:
                self.playing = False

    #guide grid can be drawn through this method
    '''def draw_grid(self):
        for x in range(0, width, tilesize):
            pg.draw.line(self.screen, lightgrey, (x,0),(x,height))
        for y in range(0, height, tilesize):
            pg.draw.line(self.screen, lightgrey, (0,y), (width,y))'''

    def draw_text(self, text, size, color, x, y):
        self.font = pg.font.Font(os.path.join(font_fld, 'Ubuntu-B.ttf'), size)
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        self.screen.blit(text_surface,text_rect)

    #sets graphical elements: display title (here - fps), sets screen background, and draws all sprites on the screen
    def draw(self):
        pg.display.set_caption('{:.2f}'.format(self.clock.get_fps()))
        self.screen.fill(bgcolor)
        self.screen.blit(pg.transform.scale(self.bg,(self.bg.get_width()*8,self.bg.get_height()*8)),(0,0))
        #self.cdown -= (pg.time.get_ticks()/1000)
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image,self.camera.apply(sprite))
        if self.playing:
            case = self.spritesheet.get_image('case').convert_alpha()
            life = self.spritesheet.get_image('patti_life').convert_alpha()
            pts = self.spritesheet.get_image('pts').convert_alpha()
            spoint = self.spritesheet.get_image('spawn_point_1').convert_alpha()
            self.screen.blit(pg.transform.scale(case,(int(case.get_width()*2),int(case.get_height()))),((width/2)-30,30))
            self.draw_text(str('{:.1f}'.format(self.cdown)), 22, white, width/2,32)
            self.screen.blit(pg.transform.scale(case,(int(case.get_width()*2.7),int(case.get_height()*2.5))),(width-int(case.get_width()*2.7),30))
            self.screen.blit(pg.transform.scale(pts,(int(case.get_width()),int(case.get_height()*0.5))),(width-72,43))
            self.screen.blit(pg.transform.scale(life,(int(case.get_width()*0.9),int(case.get_height()*0.8))),(width-72,73))
            self.draw_text(str(self.player_score), 20, white, width-23, 40)
            self.draw_text(str(self.player.lives), 20, white, width-23, 74)
        #self.draw_grid()
        pg.display.flip()

    #overall process input control - eg keys that interrupt the game directly
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if (event.key == pg.K_SPACE or event.key == pg.K_z) and not (self.player.isjump or self.player.midair):
                    jump(self.player)
            if event.type == self.mob_spawnevent:
                for sp in self.utilities:
                    if sp.active:
                        self.counter.send_mob(sp)
                        sp.active = False
                    else:
                        sp.active = True
            if event.type == self.life_spawnevent:
                self.counter.lifecheck()

    def wait_for_key(self):

        waiting = True
        while waiting:
            self.clock.tick(fps)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.quit()
                    else:
                        waiting = False
                        self.playing = True

    #title screen
    def show_start_screen(self):
        pg.mixer.music.stop()
        pg.mixer.music.load(os.path.join(sound_fld,'intro.ogg'))
        pg.mixer.music.play(-1)
        self.screen.fill(bgcolor)
        #self.draw_text(title, 48, white, width / 2, height / 4)
        banner = self.spritesheet.get_image('main_title')
        self.screen.blit(banner,((width / 3) - 10, height / 4))
        self.draw_text("Arrows/WASD to move, Space/Z to jump", 22, white, width / 2, height* 3 / 5)
        self.draw_text("Press a key to play", 22, white, width / 2, height * 3 / 4)
        self.draw_text('High Score: ' + str(self.highscore), 22, white, width/2, 15)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self, type):
        if type == 'over':
            self.screen.fill(bgcolor)
            if self.player.lives == 0 or self.cdown <= 0:
                #self.draw_text("GAME OVER", 48, white, width / 2, height / 4)
                cap = self.spritesheet.get_image('game_over')
                self.screen.blit(cap, (width / 3, height / 4))
            else:
                #self.draw_text("YOU WON!!", 48, white, width / 2, height / 4)
                cap = self.spritesheet.get_image('you_won')
                self.screen.blit(cap, (width / 3, height / 4))
            self.draw_text("Press a key to play again", 22, white, (width / 2)+30, height * 3 / 4)
            if self.player_score > self.highscore:
                self.highscore = self.player_score
                with open(os.path.join(game_fld,'highscore.txt'),'w') as f:
                    f.write(str(self.player_score))
                self.draw_text('New High Score! ' + str(self.highscore), 22, white, width/2, height/2)
            else:
                self.draw_text('Score: ' + str(self.player_score), 22, white, width/2, height/2 - 40)
                self.draw_text('High Score: ' + str(self.highscore),22,white,width/2,height/2)
            self.lives_spent = 0
            self.player_score = 0
            self.cdown = level_time
            self.level = 1
            pg.display.flip()
            self.wait_for_key()
        if type == 'level':
            pg.mixer.music.stop()
            if self.level == 1:
                pg.mixer.music.load(os.path.join(sound_fld,'level_1.ogg'))
                pg.mixer.music.set_volume(0.2)
            if self.level == 2:
                pg.mixer.music.load(os.path.join(sound_fld,'level_2.ogg'))
                pg.mixer.music.set_volume(0.4)
            if self.level == 3:
                pg.mixer.music.load(os.path.join(sound_fld,'level_3.ogg'))
                pg.mixer.music.set_volume(0.2)
            self.screen.fill(bgcolor)
            self.draw_text('Level ' + str(self.level), 38, white, width/2,height/2)
            pg.display.flip()
            pg.time.wait(3000)
            self.new(self.level)
            self.draw()
            self.counter.next_stage()
            pg.mixer.music.play(-1)

    #game main loop
    def run(self):
        self.show_start_screen()
        self.show_go_screen('level')
        while self.playing:
            self.update()
            self.events()
            self.draw()
        self.show_go_screen('over')

# Creating game object
g = Game()
while True:
    g.run()
