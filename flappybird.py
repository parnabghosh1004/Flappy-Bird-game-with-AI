import pygame
import neat
import time
import os,sys
import random

win_width = 550
win_height = 750
pygame.init()
pygame.mixer.init()
img = pygame.image.load('gallery/images/bluebird-downflap.png')
w,h = int(1.5*img.get_width()),int(1.5*img.get_height())
bird_imgs = [
             pygame.transform.scale(pygame.image.load('gallery/images/orangebird-downflap.png'),(w,h)),
             pygame.transform.scale(pygame.image.load('gallery/images/orangebird-midflap.png'),(w,h)),
             pygame.transform.scale(pygame.image.load('gallery/images/orangebird-upflap.png'),(w,h))
            ] 

pipe_img = pygame.transform.scale2x(pygame.image.load('gallery/images/pipe-red.png'))
base_img = pygame.transform.scale2x(pygame.image.load('gallery/images/base.png')) 
bg_img = pygame.transform.scale2x(pygame.image.load('gallery/images/background-night.png'))  
font = pygame.font.SysFont('comicsans',50)
font1 = pygame.font.SysFont('comicsans',100)
font2 = pygame.font.SysFont('comicsans',75)
font3 = pygame.font.SysFont('comicsans',30)

win = pygame.display.set_mode((win_width,win_height))
pygame.display.set_caption('Flappy bird')
clock = pygame.time.Clock()
s,x = 0,0
bird_height = bird_imgs[0].get_height()

wing = pygame.mixer.Sound('gallery/sounds/wing.wav')
point = pygame.mixer.Sound('gallery/sounds/point.wav')
hit = pygame.mixer.Sound('gallery/sounds/hit.wav')
die = pygame.mixer.Sound('gallery/sounds/die.wav')

class Bird:
    img = bird_imgs
    img_count = 1
    flap = 0
    vel= 0
    angle = 0
    tick = 0
    rotated_img = img[img_count]
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def jump(self):
        self.tick = 0
        self.vel = -6
    
    def move(self):
        
        self.tick += 1       
        d = self.vel*self.tick + 1.2*self.tick**2

        if d>=20:
            d = 20
        if d<0:
            d -= 2

        self.y += d

        if d>0:
            if self.angle > -80:
                self.rotated_img = pygame.transform.rotate(self.img[self.img_count],self.angle) 
                self.angle -= 2
            else:
                self.rotated_img = pygame.transform.rotate(self.img[self.img_count],self.angle)    
        if d<0:
            if self.angle<28:
                self.rotated_img = pygame.transform.rotate(self.img[self.img_count],self.angle) 
                self.angle += 4  
            else:
                self.rotated_img = pygame.transform.rotate(self.img[self.img_count],self.angle)       

    def draw(self,win):       
        if self.flap == 1:
            self.img_count+=1
            if self.img_count>2:
                self.img_count = 0
        else:
            self.img_count = 1        
        win.blit(self.rotated_img,(self.x,self.y))
        self.move()

class Pipe:
    pipe_height = pipe_img.get_height()
    pipe_width =  pipe_img.get_width()
    pipe_down = pipe_img
    pipe_up = pygame.transform.flip(pipe_img, False, True)
    vel = 5
    wh = win_height
    gap = int(2*bird_height/1.5) + 120

    def __init__(self,x1,x2):
        self.x1 = x1
        self.x2 = x2
        self.r1 = random.randint(200,580)
        self.r2 = random.randint(200,580)
        self.gap_btw_pipes = x2-x1

    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel   
        if self.x1+self.pipe_width<0:
            self.x1 = self.x2 + self.gap_btw_pipes
            self.r1 = random.randint(200,580)
        if self.x2+self.pipe_width<0:
            self.x2 = self.x1 + self.gap_btw_pipes
            self.r2 = random.randint(200,580)    

    def draw(self,win):
        win.blit(self.pipe_up,(self.x1,-self.r1))
        win.blit(self.pipe_down,(self.x1,self.pipe_height-self.r1+self.gap))
        win.blit(self.pipe_up,(self.x2,-self.r2))
        win.blit(self.pipe_down,(self.x2,self.pipe_height-self.r2+self.gap))
        self.move()

class Ground:
    width = base_img.get_width()
    vel = 5
    img = base_img

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width

    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel
        if self.x1+self.width<0:
            self.x1 = self.x2 + self.width    
        if self.x2+self.width<0:
            self.x2 = self.x1+self.width    
    
    def draw(self,win):
        self.move()
        win.blit(self.img,(self.x1,self.y))  
        win.blit(self.img,(self.x2,self.y))  

def IsCollide(bird,pipe,ground):
    if bird.y + bird.img[bird.img_count].get_height()-20> ground.y:
        return True

    if pipe.x1<bird.x + bird.rotated_img.get_width()-25<pipe.x1+pipe.pipe_width and (bird.y + bird.rotated_img.get_height()//4   in range(0,pipe.pipe_height-pipe.r1) or bird.y + bird.rotated_img.get_height()//4 in range(pipe.pipe_height-pipe.r1 + pipe.gap,int(ground.y)) or bird.y + bird.rotated_img.get_height()-30>pipe.pipe_height-pipe.r1 + pipe.gap or bird.y+20<pipe.pipe_height-pipe.r1):
        return True 
    
    if pipe.x2<bird.x + bird.rotated_img.get_width()-25<pipe.x2+pipe.pipe_width  and (bird.y + bird.rotated_img.get_height()//4 in range(0,pipe.pipe_height-pipe.r2) or bird.y + bird.rotated_img.get_height()//4 in range(pipe.pipe_height-pipe.r2 + pipe.gap,int(ground.y)) or bird.y + bird.rotated_img.get_height()-30>pipe.pipe_height-pipe.r2 + pipe.gap or bird.y+20<pipe.pipe_height-pipe.r2):  
        return True

    return False

def score(bird,pipe,win,font):
    global s,x
    if x == 0:
        if bird.x > pipe.x1+pipe.pipe_width:
            s += 1
            x = 1
            point.play()

    if x == 1:     
        if bird.x > pipe.x2+pipe.pipe_width:
            s += 1
            x  = 0
            point.play()

    textobj = font3.render(f'Score : {s}',False,(0,0,0))
    win.blit(textobj,(50,50))

def gameStart(bird,ground,pipe):
    global gamestart,gameover
    win.blit(bg_img,(0,-100))
    pipe.draw(win)       
    ground.draw(win)
    bird.draw(win)

    key = pygame.key.get_pressed()
    if key[pygame.K_SPACE]:
        bird.flap = 1
        bird.jump()
        bird.vel -= 1
        wing.play()
    else:
        bird.flap = 0  

    score(bird,pipe,win,font)
    
    if IsCollide(bird,pipe,ground):
        hit.play(maxtime=1000)
        die.play(maxtime=1000)
        gamestart = False
        gameover = True
        return

def gameStartAI(genomes, config):
    global gen
    nets = []
    birds = []
    ge = []
    s,x = 0,0   # local to gameStartAI
    for genome_id, genome in genomes:
        genome.fitness = 0 
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(100,300))
        ge.append(genome)

    ground = Ground(win_height/1.12)
    pipe = Pipe(win_width*1.2,win_width*2)
    clock = pygame.time.Clock()
    pipe_index = 0
    run = True
    while run and len(birds) > 0:
        clock.tick(70)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                pygame.quit()
                sys.exit()
                
        if len(birds)>0:
            if birds[0].x > pipe.x2 + pipe.pipe_width:
                pipe_index = 0 
            elif birds[0].x > pipe.x1 + pipe.pipe_width:
                pipe_index = 1

        for i, bird in enumerate(birds):
            ge[i].fitness += 0.1
            output = [0]
            if pipe_index == 0:
                output = nets[i].activate((bird.y,abs(bird.y-pipe.pipe_height+pipe.r1),abs(bird.y-(pipe.pipe_height-pipe.r1+pipe.gap))))
            else:
                output = nets[i].activate((bird.y,abs(bird.y-pipe.pipe_height+pipe.r2),abs(bird.y-(pipe.pipe_height-pipe.r2+pipe.gap))))                             

            if output[0]>0.5:
                bird.flap = 1
                bird.jump()
                bird.vel -= 1
                wing.play()
            else:
                bird.flap = 0
        
        for bird in birds:
            if IsCollide(bird,pipe,ground):
                ge[birds.index(bird)].fitness -= 1
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))
        win.blit(bg_img,(0,-100))
        pipe.draw(win)       
        ground.draw(win)

        for bird in birds:
            bird.draw(win)
        
        for bird in birds:
            if x == 0:
                if bird.x > pipe.x1+pipe.pipe_width:
                    s += 1
                    x = 1
                    point.play()

            if x == 1:     
                if bird.x > pipe.x2+pipe.pipe_width:
                    s += 1
                    x  = 0
                    point.play()
                    
            textscore = font3.render(f'Score : {s}',False,(0,0,0))
            textgen = font3.render(f'Gen : {gen}',False,(0,0,0))
            textbird = font3.render(f'Birds alive : {len(birds)}',False,(0,0,0))
            win.blit(textscore,(50,50))
            win.blit(textgen,(50,100))
            win.blit(textbird,(50,150))
            break        

        pygame.display.update()

    gen += 1    

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(gameStartAI, 50)
    print('\nBest genome:\n{!s}'.format(winner))

local_dir = os.path.dirname(__file__)
config_file = os.path.join(local_dir, 'config-feedforward.txt')

gameclose = False
gamestart = False
gameAI = False
gameover = False
img_count = 0
anim_time = 0
gen = 0

while not gameclose:

    for event in pygame.event.get():
        if event.type==pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            gamestart  =True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            gameAI  = True        
    
    text3 = font2.render("Game Over !",False,(0,0,0))
    text4 = font.render(f"Your Score : {s}",False,(0,0,0))
    if not gamestart and not gameAI:
        win.blit(bg_img,(0,-100))
        win.blit(base_img,(0,win_height/1.12))
        text = font1.render("FLAPPY BIRD",True,(0,0,0))
        text1 = font.render("Press s to start",False,(0,0,0))
        text2 = font.render("Press q to quit",False,(0,0,0))
        text3 = font.render("Press a to play with AI",False,(0,0,0))
        win.blit(text,(40,100))
        win.blit(text1,(140,400))
        win.blit(text2,(140,450))
        win.blit(text3,(80,500))
        
        if anim_time%3 == 0:
            img_count += 1
            if img_count > 2:
                img_count = 0
        win.blit(bird_imgs[img_count],(250,250))          
        bird = Bird(100,300)
        ground = Ground(win_height/1.12)
        pipe = Pipe(win_width*1.2,win_width*2)
        anim_time +=1

    if gamestart:
        gen = 0
        gameStart(bird,ground,pipe)

    if gameAI:
        run(config_file)      
        gameAI = False
    
    if gameover:    
        s = 0
        x = 0
        anim_time = 0
        win.blit(text3,(130,350))
        win.blit(text4,(160,450))
        pygame.display.update()
        time.sleep(2)
        gameover = False


    clock.tick(40)
    pygame.display.update()
   
            


    
         
            
