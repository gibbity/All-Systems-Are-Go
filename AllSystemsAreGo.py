from pygame import * # for built in Pygame modules
from random import * # to generate random numbers
from math import * # to calculate projectiles
from ast import *#for files
from operator import * #for files

init() # initialise pygame

#create window
game_size = width,height = 800,600
whole_size = maxwidth,height = 1000,600
screen = display.set_mode(whole_size)
#sounds
music = mixer.music.load('sounds/Pamgaea.ogg')
crash_sound = mixer.Sound('sounds/general_crash.ogg')
cheer_sound = mixer.Sound('sounds/Eehh.ogg')
death_sound = mixer.Sound('sounds/death_crash.ogg')
moon_sound = mixer.Sound('sounds/moon_crash.ogg')
#images
def LoadAndScale(path,w,h):
    #loading images from the 'images' folder
    picture = image.load('images/' + path)
    if w != 0 and h != 0:
        #scaling images if I have stated the new width and height
        picture = transform.scale(picture,(w,h))
    return picture
#the images in the folder
background_img = LoadAndScale('background.png',maxwidth,height)
home_img = LoadAndScale('home_background.png',maxwidth,height)
name_img = LoadAndScale('name_input_background.png',maxwidth,height)
moon_img = LoadAndScale('moon.png',20,20)
rocket_img = LoadAndScale('bluerocket.png',20,20)
jupiter_img = LoadAndScale('jupiter.png',0,0)
mars_img = LoadAndScale('mars.png',0,0)
saturn_img = LoadAndScale('saturn.png',0,0)
uranus_img = LoadAndScale('uranus.png',0,0)
venus_img = LoadAndScale('venus.png',0,0)
earth_img = LoadAndScale('earth.png',0,0)
asteroid_img = LoadAndScale('asteroid.png',0,0)
dial_img = LoadAndScale('dial.png',194,194)
explosion_img = LoadAndScale('explosion.png',40,40)
spinning_asteroid = transform.scale(asteroid_img,(100,100))
#generating a random goal planet
random_planet = [jupiter_img, mars_img, saturn_img, uranus_img, venus_img]
the_planet = random_planet[randint(0,4)]
#fonts
density_font = font.SysFont("rockwell", 18)
button_font_14 = font.Font('fonts/Futura.ttf',14)
button_font_40 = font.Font('fonts/Futura.ttf',40)
button_font_55 = font.Font('fonts/Futura.ttf',55)
instructions_font = font.Font('fonts/Futura.ttf',20)
name_font = font.SysFont("rockwell", 40)
score_font = font.SysFont("rockwell", 60)
#colours
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
orange = (210,70,10)
green = (0,128,0)
navy = (4,8,40)
grey = (100,100,100)

class playfield:
#handles all the actual game components    
    def __init__(self):
    #create lists from map files    
        self.asteroids = []
        self.earth = []
        self.goal = []
        self.rocket = []
        
    def load_map(self,filename):
    #Change global variables to predefined paramaters in the file
        global max_power,min_power
        exec(open(filename,'r').read())

    def create(self,image,properties):
    #scale and blit images onto the playfield, with their densities    
        x = properties[0]
        y = properties[1]
        radius = properties[2]
        half_radius = properties[3]
        diameter = properties[2]*2
        scaled_image = transform.scale(image,(diameter,diameter))
        blit_image = screen.blit(scaled_image,(x-radius,y-radius))
        message = density_font.render(str(round(half_radius/radius,2)),1,red)
        w,h = density_font.size(str(round(half_radius/radius,2)))
        message = screen.blit(message,(x-w/2,y-h/2))

    def draw(self):
    #draw all objects (except moon) on the playfield
        global launch_start,power,max_power
        #use properties in file to draw
        game.create(earth_img,self.earth)
        game.create(the_planet,self.goal)
        for i in self.asteroids:
            game.create(asteroid_img,i)
        #only draw rocket if it is launched
        if self.rocket != []:
            x2 = self.rocket[0]-self.rocket[2]/6
            y2 = self.rocket[1]-self.rocket[3]/6
            dx = x2 - self.rocket[0]
            dy = y2 - self.rocket[1]
            rads = atan2(-dy,dx)
            rads %= 2*pi
            degs = degrees(rads) + 90
            rocket = transform.rotate(rocket_img, degs)
            rocket = screen.blit(rocket,(self.rocket[0]-10,self.rocket[1]-10))

    def moon(self, moon_visible):
        #draw the moon
        global speed, angle
        #make earth center of orbit
        center_x = self.earth[0] - 10
        center_y = self.earth[1] - 10
        radius = 60
        moon_x = radius * sin(angle) + center_x
        moon_y = radius * cos(angle) + center_y
        #moon will be invisible for the rest of the level if collided with
        if moon_visible: moon = screen.blit(moon_img,(moon_x,moon_y))
        angle += speed
        #to check for collision:
        return moon_x,moon_y
        
    def launch(self,x,y,click,angle):
    #use the selected power to give the rocket its initial properties
        global launch_start,power,power_direction,max_power,min_power
        #but only when the user has launched and within the playfield
        if self.rocket == []:
            if (mx < width):
                if not launch_start and click:
                    launch_start = 1
                    power = 10
                elif launch_start and click:
                    power += power_direction
                    if power >= max_power: power_direction = -sqrt(power_direction**2)
                    if power <= min_power: power_direction = sqrt(power_direction**2)
                elif launch_start and not click:
                    self.rocket = [x,y,cos(angle)*power,sin(angle)*power]
                    launch_start = 0

    def gravity(self,i):
    #calculate the rocket's projectile
        distance = sqrt((i[0]-self.rocket[0])**2+(i[1]-self.rocket[1])**2)-i[3]
        angle = atan((i[1]-self.rocket[1])/(i[0]-self.rocket[0]+0.0000001))
        if i[0] < self.rocket[0]: angle += radians(180)
        gravitational_effect = i[3]*(i[2]/(i[2]+distance))**2

        self.rocket[2] += cos(angle)*gravitational_effect/10
        self.rocket[3] += sin(angle)*gravitational_effect/10

    def update(self,moon_x,moon_y):
    #Update the rocket's position
        if self.rocket != []:
            for i in self.asteroids:
                game.gravity(i)
            for i in (self.earth,self.goal):
                game.gravity(i)
            self.rocket[0] += self.rocket[2]/10
            self.rocket[1] += self.rocket[3]/10
        #check collision with
            #asteroids
            for i in self.asteroids:
                if sqrt((i[0]-self.rocket[0])**2+(i[1]-self.rocket[1])**2) < i[2]:
                    return -1
            #earth
            if sqrt((self.earth[0]-self.rocket[0])**2+\
            (self.earth[1]-self.rocket[1])**2) < self.earth[2]:
                return -1
            #goal planet
            if sqrt((self.goal[0]-self.rocket[0])**2+\
            (self.goal[1]-self.rocket[1])**2) < self.goal[2]:
                return 1
            #screen border
            if self.rocket[0] < 0 or self.rocket[0] > width or\
            self.rocket[1] < 0 or self.rocket[1] > height:
                return -1
            #moon
            if sqrt((moon_x-self.rocket[0])**2+\
            (moon_y -self.rocket[1])**2) < 20:
                return 2
        return 0

    def crash(self):
    #play crash sound and change rocket image to exploded rocket image
        crash_sound.play() 
        screen.blit(explosion_img,(self.rocket[0]-20,self.rocket[1]-20))
        screen.blit(rocket,(self.rocket[0]-10,self.rocket[1]-10))
        display.flip()

    def check_gameover(self,lives,page,endgame,complete):
    #check if game has ended and display appropriate message if so
        if lives < 0 or complete:
            if lives < 0: #if out of lives
                death_sound.play()
                screen.blit(button_font_40.render("GAME OVER",1,red),(280,290))
            if complete: #if out of levels
                screen.blit(button_font_40.render("GAME COMPLETE",1,red),(240,290))
            screen.blit(button_font_14.render("Click to continue",1,red),(350,330))
            page = "nameinput"
            endgame = True #endgame is used to differenciate
            cont = True       #between saving a complete and incomplete game
            while cont:
                display.flip()
                for evnt in event.get():
                    if evnt.type == MOUSEBUTTONUP:
                        cont = False
        return page, endgame

class shapes(sprite.Sprite):
#class for buttons
    def __init__(self,x,y,width,height,border,option):
        #define a button
        sprite.Sprite.__init__(self)
        self.box = Surface([x+width,y+height],border)
        if option == 1: #1 for rectange, 2 for circle
            #draw button and outline
            draw.rect(screen,black,[x,y,width,height],0)
            draw.rect(screen,white,[x,y,width,height],border)
        if option == 2:
            radius = int(width/2)
            draw.ellipse(screen,black,[x,y,width,height],0)
            for i in range(300): #loop for creating circle outline
                ang = i * 3.14159 * 2 / 300
                dx = int(cos(ang) * radius)
                dy = int(sin(ang) * radius)
                bx = x + dx
                by = y + dy
                draw.circle(screen,white,[bx+radius,by+radius],(border//3))
        self.rect = self.box.get_rect() 
        self.rect.x = x #get the coordinates of the button
        self.rect.y = y #to check for collisions (mouse clicks)

def game_panel():
    draw.rect(screen,grey,[width,0,200,height])#grey panel
    reset_button = shapes(815,425,80,80,3,2)#buttons
    save_button = shapes(905,425,80,80,3,2)
    home_button = shapes(815,515,80,80,3,2)
    sound_button = shapes(905,515,80,80,3,2)
    title(816,60,page)
    shapes(810,10,180,50,3,1)#these two won't be buttons
    shapes(810,355,180,60,3,1)
    #text 
    screen.blit(density_font.render("Level " + str(level+1),1,green),(815,360))
    screen.blit(density_font.render("Lives remaining: " + str(lives),1,green),(815,385))
    screen.blit(button_font_14.render("Reset",1,red),(836,450))
    screen.blit(button_font_14.render("rocket",1,red),(833,462))
    screen.blit(button_font_14.render("Save and",1,green),(912,450))
    screen.blit(button_font_14.render("exit",1,green),(930,462))
    homebutton(815,515)
    soundbutton(905,515,red,change_to)
    #drawing the power bar
    draw.rect(screen,green,(812,12,power*(180/max_power)-3,46))
    for i in range(840,990,15):
        #red lines are fiducial markers
        draw.line(screen,red,(i,12),(i,20),2)
        draw.line(screen,red,(i,50),(i,57),2)
        
def instructions():
    shapes(15,95,750,483,3,1)
    i = 150
    screen.blit(instructions_font.render("Guide the rocket to land on the planet. But beware the asteroids in",1,red),(30,i))
    screen.blit(instructions_font.render("between!",1,red),(30,i+30))
    screen.blit(instructions_font.render("Left-click in the direction you want the rocket to face and hold down ",1,green),(30,i+90))
    screen.blit(instructions_font.render("to build up power. Release when your desired power is reached.",1,green),(30,i+120))
    screen.blit(instructions_font.render("Use the numbers on the bodies  - their relative densities – to guide you.",1,red),(30,i+180))
    screen.blit(instructions_font.render("When you crash into an asteroid, you lose a life. But you can gain lives",1,green),(30,i+240))
    screen.blit(instructions_font.render("by hitting the orbiting moon!",1,green),(30,i+270))

def about():
    shapes(15,95,750,483,3,1)
    x = 50
    i = 150
    screen.blit(instructions_font.render("Giny Huynh 2015",1,white),(300,i))
    screen.blit(instructions_font.render("Images:",1,green),(x,i+60))
    screen.blit(instructions_font.render("clipartlord.com",1,red),(x,i+90))
    screen.blit(instructions_font.render("clker.com",1,red),(x,i+120))
    screen.blit(instructions_font.render("mycutegraphics.com",1,red),(x,i+150))
    screen.blit(instructions_font.render("Music:",1,green),(x,i+210))
    screen.blit(instructions_font.render('"Pamgaea" Kevin MacLeod (incompetech.com) ',1,red),(x,i+240))
    screen.blit(instructions_font.render("Licensed under Creative Commons: By Attribution 3.0 ",1,red),(x,i+270))
    screen.blit(instructions_font.render("http://creativecommons.org/licenses/by/3.0/",1,red),(x,i+300))

def save(name,level,lives):
    f = open("files/SavedGamesFile.txt", "a+")
    f.write("('" + name + "'," + str(level) + "," + str(lives) +")\n")
    f.close()

def currentgames(games_lst):
    shapes(15,110,753,60,3,1)
    screen.blit(name_font.render("Name",1,white),(30,113))
    screen.blit(name_font.render("Current level",1,white),(520,113))
    for i in range(3):
        shapes(520,110+(i+1)*100,250,60,3,1)
    for j in range(len(games_lst)):
        if j%2==1:
            colour = red
        else:
            colour = green
        screen.blit(name_font.render(games_lst[j][0],1,colour),(30,115+(j+1)*100))
        screen.blit(name_font.render(str(games_lst[j][1]+1),1,colour),(635,115+(j+1)*100))
     
def highscores(name, score):
    f = open("files/HighscoresFile.txt", "a+")
    f.write("('" + name + "'," + str(score) + ")\n")
    f.close()
    with open('files/HighscoresFile.txt', 'r', encoding='utf-8') as f:
        f.seek(0)
        lst = [literal_eval(line.strip()) for line in f]
    f.close()
    scoreslst = sorted(lst, key=itemgetter(1), reverse=True)
    while len(scoreslst) > 5:
        del scoreslst[-1]
    f = open("files/HighscoresFile.txt", "w")
    for i in scoreslst:
        f.write("('" + i[0] + "'," + str(i[1]) + ")\n")
    f.close

def scoretable(scores):
    shapes(15,110,753,60,3,1)
    screen.blit(name_font.render("#",1,white),(30,113))
    screen.blit(name_font.render("Name",1,white),(160,113))
    screen.blit(name_font.render("Score",1,white),(650,113))
    for i in range(1,6):
        shapes(15,110+i*80,120,60,3,1)
        shapes(155,110+i*80,475,60,3,1)
        shapes(650,110+i*80,120,60,3,1)
        colour = red
    for j in range(len(scores)):
        if j%2==1:
            colour = red
        else:
            colour = green
        screen.blit(name_font.render(str(j+1),1,colour),(30,115+(j+1)*80))
        screen.blit(name_font.render(scores[j][0],1,colour),(170,115+(j+1)*80))
        screen.blit(name_font.render(str(scores[j][1]),1,colour),(665,115+(j+1)*80))

def title(x,y,page):
#draw the title, 'All Systems Are Go'
    crimson = (180,0,0)
    if page != "home" and page !="nameinput" and page !="loadgame":
        #only these three pages have a box surrounding the title
        shapes(x-6,y+20,180,260,3,1)
    #the text
    screen.blit(font.SysFont("rockwell", 130).render("All",1,crimson),(x,y))
    screen.blit(font.SysFont("rockwell", 46).render("Systems",1,crimson),(x,y+120))
    screen.blit(font.SysFont("rockwell", 46).render("Are",1,crimson),(x+95,y+158))
    screen.blit(font.SysFont("rockwell", 130).render("Go",1,crimson),(x-8,y+145))

def homebutton(x,y):
    #create text for home button with given coordinates
    screen.blit(button_font_14.render("Home",1,green),(x+20,y+30))
    
def soundbutton(x,y,colour,option):
    #create text for sound button with given coordinates,
    #colour and whether the text is 'on' or 'off
    screen.blit(button_font_14.render("Sound",1,colour),(x+15,y+25))
    screen.blit(button_font_14.render(option,1,colour),(x+27,y+37))

def rotate(image, rect, angle,x,y):
#rotate an image around a given point
    rot_image = transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    screen.blit(rot_image,(rot_rect.x+x, rot_rect.y + y))

def sounds(option):
#change text on button when
#user turns sound on/off
    if option == "on":
        mixer.music.unpause()
        option = "off"
    else:
        mixer.music.pause()
        option = "on"
    return option     

###########################################################################

game = playfield() #initialise the game

rotation = 0
timer = 0
speed = 0.08
angle = pi

launch_start = 0
max_power = 60
min_power = 10
power = 10
power_direction = 2

maps = ['maps/map'+str(i+1)+'.txt' for i in range(10)]

page = "home"
mixer.music.play(-1)
change_to = "off"

cont = 1
while cont:
    screen.fill(grey)
    # Handle events
    for evnt in event.get():
        if evnt.type == QUIT:   # Closes the game
            cont = 0

        if evnt.type == KEYDOWN:
            if evnt.key == K_ESCAPE: # Closes the game
                cont = 0
            if page == "nameinput":
                if (evnt.key == K_BACKSPACE):
                    if (len(name)>0):
                        name= name[:-1]
                elif (evnt.key == K_RETURN):
                    if endgame == True:
                        page = "highscores"
                        highscores(name, level+1)
                    else:
                        page = "home"
                        save(name,level,lives)
                else:
                    if (evnt.key >= 48 and evnt.key <= 57) or (evnt.key >= 97 and evnt.key <= 122) or (evnt.key == 32):
                        if (len(name)<10):
                            if (key.get_pressed()[K_LSHIFT]) or (key.get_pressed()[K_RSHIFT]): 
                              evnt.key -= 32
                            name += chr(evnt.key)
        if evnt.type == MOUSEBUTTONUP:#if the user clicks something
            pos = mouse.get_pos()
            if (page == "home" or page == "playfield") and sound_button.rect.collidepoint(pos):
                change_to = sounds(change_to)
            elif home_button.rect.collidepoint(pos):
                page = "home"
            else:
                if page == "home": #buttons on the homepage
                    if start_button.rect.collidepoint(pos):
                        page = "loadgame"
                    if instructions_button.rect.collidepoint(pos):
                        page = "instructions"
                    if highscores_button.rect.collidepoint(pos):
                        page = "highscores"
                    if exit_button.rect.collidepoint(pos):
                        cont = 0
                    if about_button.rect.collidepoint(pos):
                        page = "about"
                elif page == "loadgame": #buttons on the load page
                    if new_button.rect.collidepoint(pos):
                        page = "playfield"
                    if load_button.rect.collidepoint(pos):
                        page = "selectgame"
                elif page == "selectgame": #saved games on the select game page
                    for i in range(len(games_lst)):
                        if savedgames[i].rect.collidepoint(pos):
                            name = games_lst[i][0]
                            level = games_lst[i][1]
                            lives = games_lst[i][2]
                            game.load_map(maps[level])
                            page = "playfield"
                elif page == "playfield": #buttons on the playfield page
                    if reset_button.rect.collidepoint(pos):
                        game.rocket = []
                        power = min_power
                        lives -=1
                    if save_button.rect.collidepoint(pos):
                        page = "nameinput"
                elif page == "highscores": #clear button on high scores page
                    if clear_button.rect.collidepoint(pos):
                        with open("files/HighscoresFile.txt", "w") as f:
                            f.close()
                    
                    
    if page == "home":

        level = 0
        game.load_map(maps[level])
        lives = 10
        name = ""
        moon_visible = True
        complete = False
        endgame = False
        
        screen.blit(background_img,(0,0))#sky image
        
        #making the rocket orbit
        rocket = transform.rotate(rocket_img,-90)
        center_x, center_y = 500,800 #center of orbit
        radius = 700 #radius of orbit
        speed = 0.02 
        x = radius * sin(angle) + center_x
        y = radius * cos(angle) + center_y
        screen.blit(rocket,(x,y))
        angle -= speed

        screen.blit(home_img,(0,0))#ship image
        title(50,325,page)
        #buttons
        start_button = shapes(250,370,200,200,10,2)
        instructions_button = shapes(475,355,300,60,3,1)
        highscores_button = shapes(475,435,300,60,3,1)
        exit_button = shapes(475,515,300,60,3,1)
        about_button = shapes(830,390,80,80,3,2)
        sound_button = shapes(830,490,80,80,3,2)
        home_button = shapes(0,0,0,0,0,1)
        #drawing the rotating red dial
        rotation -= 2 #degrees
        rotate(dial_img,dial_img.get_rect(),rotation,252,372)
        rotate(dial_img,dial_img.get_rect(),rotation-22.5,252,372)
        #text
        screen.blit(button_font_55.render("Play",1,green),(290,435))
        screen.blit(button_font_40.render("Instructions",1,green),(510,360))
        screen.blit(button_font_40.render("Highscores",1,green),(515,440))
        screen.blit(button_font_40.render("Exit",1,green),(590,520))
        screen.blit(button_font_14.render("About",1,green),(845,420))
        soundbutton(830,490,green,change_to)

    elif page == "loadgame":
        
        screen.blit(background_img,(0,0))
        rocket = transform.rotate(rocket_img,-90)
        screen.blit(home_img,(0,0))
        title(50,325,page)

        new_button = shapes(280,370,200,200,10,2)
        load_button = shapes(520,370,200,200,10,2)
        home_button = shapes(900,500,80,80,3,2)
        homebutton(900,500)
        
        rotation +=2
        rotate(dial_img,dial_img.get_rect(),rotation,282,372)
        rotate(dial_img,dial_img.get_rect(),-rotation,522,372)

        screen.blit(button_font_40.render("New",1,green),(335,425))
        screen.blit(button_font_40.render("game",1,green),(322,455))
        screen.blit(button_font_40.render("Load",1,green),(568,425))
        screen.blit(button_font_40.render("game",1,green),(562,455))

    elif page == "selectgame":
        title(806,0,page)
        shapes(15,15,300,60,3,1)
        screen.blit(button_font_40.render("Load Game",1,green),(50,20))
        home_button = shapes(900,500,80,80,3,2)
        homebutton(900,500)
        
        savedgames = [shapes(15,210,475,60,3,1), shapes(15,310,475,60,3,1), shapes(15,410,475,60,3,1)]

        with open('files/SavedGamesFile.txt', 'r', encoding='utf-8') as f:
            games_lst = [literal_eval(line.strip()) for line in f]
        f.close()
        while len(games_lst) >  3:
            del games_lst[0]
        currentgames(games_lst)
        
    elif page == "playfield":

        # Update screen
        screen.blit(background_img,(0,0))
        
        draw.rect(screen,grey,[width,0,200,height])
        reset_button = shapes(815,425,80,80,3,2)
        save_button = shapes(905,425,80,80,3,2)
        home_button = shapes(815,515,80,80,3,2)
        sound_button = shapes(905,515,80,80,3,2)
        game_panel()
        
        game.draw()
        moon_x,moon_y = game.moon(moon_visible)
        if game.rocket == []: draw.circle(screen,red,(round(x),round(y)),5)

        mx,my = mouse.get_pos()
        lc = mouse.get_pressed()[0]

        f_angle = atan((my-game.earth[1])/(mx-game.earth[0]+0.00000001))
        if mx < game.earth[0]: f_angle += radians(180)
        x = cos(f_angle)*game.earth[2]+game.earth[0]
        y = sin(f_angle)*game.earth[2]+game.earth[1]

        game.launch(x,y,lc,f_angle)
        action = game.update(moon_x,moon_y)  # Will return -1 if the player crashed and 1 if succeed
        if action < 0:
            game.crash()
            lives -= 1
            game.rocket = []
            power = min_power
        elif action == 2:
            if moon_visible:
                moon_sound.play()
                moon_visible = False
                lives += 1
        elif action == 1:
            cheer_sound.play()
            level += 1
            try: game.load_map(maps[level]) # Tries to load the next map
            except:
                complete = True
                endgame = True
                page,endgame = game.check_gameover(lives,page,endgame,complete)
            game.rocket = []
            power = min_power
            moon_visible = True
            complete = False

        page,endgame = game.check_gameover(lives,page,endgame,complete)

    elif page == "instructions":
        title(806,0,page)
        shapes(15,15,300,60,3,1)
        screen.blit(button_font_40.render("Instructions",1,green),(50,20))
        home_button = shapes(900,500,80,80,3,2)
        homebutton(900,500)
        instructions()

    elif page == "about":
        title(806,0,page)
        shapes(15,15,300,60,3,1)
        screen.blit(button_font_40.render("About",1,green),(100,20))
        home_button = shapes(900,500,80,80,3,2)
        homebutton(900,500)
        about()

    elif page == "highscores":
        title(806,0,page)
        shapes(15,15,300,60,3,1)
        screen.blit(button_font_40.render("Highscores",1,green),(50,20))
        home_button = shapes(900,500,80,80,3,2)
        homebutton(900,500)
        clear_button = shapes(800,500,80,80,3,2)
        screen.blit(button_font_14.render("Clear",1,red),(820,520))
        screen.blit(button_font_14.render("highscores",1,red),(804,535))
        
        with open('files/HighscoresFile.txt', 'r', encoding='utf-8') as f:
            scores = [literal_eval(line.strip()) for line in f]
        f.close()
        scoretable(scores)

    elif page == "nameinput":
        screen.blit(background_img,(0,0))
        
        rotation -= 2
        center_x = 400
        center_y = 1000
        radius = 1000
        speed = 0.005
        x = radius * sin(angle) + center_x
        y = radius * cos(angle) + center_y
        angle -= speed
        rotate(spinning_asteroid,spinning_asteroid.get_rect(),rotation,x,y)
        
        screen.blit(name_img,(0,0))
        title(50,285,page)
        
        shapes(400,220,200,200,10,2)
        rotate(dial_img,dial_img.get_rect(),rotation,402,222)
        screen.blit(density_font.render("Score:",1,green),(478,270))
        score = score_font.render(str(level+1),1,green)
        screen.blit(score,[(screen.get_rect().centerx)-(score.get_rect().centerx), 285])

        home_button = shapes(900,500,80,80,3,2)
        screen.blit(button_font_14.render("Continue",1,green),(908,520))
        screen.blit(button_font_14.render("without",1,green),(913,532))
        screen.blit(button_font_14.render("saving",1,green),(918,544))

        shapes(280,450,125,60,3,1)
        screen.blit(name_font.render("Name:",1,green),(283,455))
        shapes(420,450,300,60,3,1)
        screen.blit(button_font_14.render("Press Enter to submit",1,green),(500,510))

        display_name = name_font.render(name,1,red)
        screen.blit(display_name,[(screen.get_rect().centerx)-(display_name.get_rect().centerx)+ 70, 455])


        

    display.flip()
    time.delay(20)
quit()
