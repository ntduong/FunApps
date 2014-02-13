'''
Created on 2013/10/23
@author: Duong Nguyen
'''

import pygame
from pygame.locals import *
from math import atan2, pi, cos, sin
import random, sys

# Initialize
pygame.init()
W, H = 640, 480
# set up display surface
display_surf = pygame.display.set_mode((W, H))
pygame.display.set_caption("Angry Pig")
# set up sound
pygame.mixer.init()

# Variables
bullet_vec = 10
max_health = 194
timer = 100
timer1 = 0
abirds = [[640,100]] # enemy list
n_shots, n_hits = 0, 0
bullets = [] # bullets list

# load images --> surfaces
player = pygame.image.load("resources/images/dude.png") 
grass = pygame.image.load("resources/images/grass.png")
castle = pygame.image.load("resources/images/new_home.png")
bullet_img = pygame.image.load("resources/images/bullet.png")
badguy1_img = pygame.image.load("resources/images/angry_bird.png")
badguy_img = badguy1_img 
healthbar = pygame.image.load("resources/images/healthbar.png")
health_img = pygame.image.load("resources/images/health.png")
gameover = pygame.image.load("resources/images/gameover.png")
win = pygame.image.load("resources/images/youwin.png")

# load audio
hit = pygame.mixer.Sound("resources/audio/explode.wav")
enemy = pygame.mixer.Sound("resources/audio/enemy.wav")
shoot = pygame.mixer.Sound("resources/audio/shoot.wav")
hit.set_volume(0.05)
enemy.set_volume(0.05)
shoot.set_volume(0.05)
pygame.mixer.music.load("resources/audio/moonlight.wav")
pygame.mixer.music.play(-1, 0.0) #bg music
pygame.mixer.music.set_volume(0.25)

grass_w, grass_h = grass.get_width(), grass.get_height()
player_x, player_y = 100, 100
keys = [False, False, False, False] # Up-Left-Down-Right order

running = True
exitcode = 0

while running:
    timer -= 1
    
    # clear display surface before drawing it again
    display_surf.fill((0,0,0))
    
    # fill the display surface with grass
    for i in xrange(int(W/grass_w) + 1):
        for j in xrange(int(H/grass_h) + 1):
            display_surf.blit(grass, (i*grass_w, j*grass_h))
            
    # put some castles onto grass too...
    display_surf.blit(castle, (0,30))
    display_surf.blit(castle, (0,135))
    display_surf.blit(castle, (0,240))
    display_surf.blit(castle, (0,345))
    
    # put player onto grass
    mouse_pos = pygame.mouse.get_pos()
    angle = atan2(mouse_pos[1]-player_y, mouse_pos[0]-player_x) # in radian
    # 360-angle*180/pi ccw = -angle*180/pi cw
    player_rot = pygame.transform.rotate(player, 360-angle*180/pi) 
    rot_rect = player_rot.get_rect()
    player_nx = player_x - int(rot_rect.width/2)
    player_ny = player_y - int(rot_rect.height/2)
    display_surf.blit(player_rot, (player_nx, player_ny))
    
    # Draw bullets
    for bullet in bullets:
        bid = 0
        # velocities in x, y directions
        vx = bullet_vec*cos(bullet[0])
        vy = bullet_vec*sin(bullet[0])
        bullet[1] += vx
        bullet[2] += vy
        if bullet[1] < -64 or bullet[1] > 640 or bullet[2] < -64 or bullet[2] > 480:
            bullets.pop(bid)
        bid += 1
        for bl in bullets:
            rot_bl = pygame.transform.rotate(bullet_img, 360-bl[0]*180/pi)
            display_surf.blit(rot_bl, (bl[1], bl[2]))
    
    # Draw abirds
    if timer == 0:
        abirds.append([640, random.randint(50,430)])
        timer = 100-(timer1*2)
        if timer1 >= 35:
            timer1 = 35
        else:
            timer1 += 5
    gid = 0
    for bird in abirds:
        if bird[0] < -32:
            abirds.pop(gid)
        bird[0] -= 2
        # Attack the castles
        brect = pygame.Rect(badguy_img.get_rect())
        brect.top = bird[1]
        brect.left = bird[0]
        if brect.left < 64:
            hit.play()
            max_health -= random.randint(5,20)
            abirds.pop(gid)
            
        # Check collisions
        cid = 0
        for bl in bullets:
            blrect = pygame.Rect(bullet_img.get_rect())
            blrect.left = bl[1]
            blrect.top = bl[2]
            if brect.colliderect(blrect):
                enemy.play()
                n_hits += 1
                abirds.pop(gid)
                bullets.pop(cid)
            cid += 1
        # next badguy
        gid += 1
            
    for badguy in abirds:
        display_surf.blit(badguy_img, badguy)
    
    # Draw clock
    font = pygame.font.Font(None, 24)
    survivedText = font.render(str((90000-pygame.time.get_ticks())/60000)+
                               ":"+str((90000-pygame.time.get_ticks())/1000 % 60).zfill(2), 
                               True, (0,0,0))
    textRect = survivedText.get_rect()
    textRect.topright = (635,5)
    display_surf.blit(survivedText, textRect)
    
    # Draw max_health bar
    display_surf.blit(healthbar, (5,5))
    for h in xrange(max_health):
        display_surf.blit(health_img, (h+8,8))
    
    # Update display surf
    pygame.display.flip()
    
    for evt in pygame.event.get():
        if evt.type == QUIT:
            pygame.quit()
            sys.exit()
        if evt.type == KEYDOWN:
            if evt.key == K_UP:
                keys[0] = True
            elif evt.key == K_LEFT:
                keys[1] = True
            elif evt.key == K_DOWN:
                keys[2] = True
            elif evt.key == K_RIGHT:
                keys[3] = True
        if evt.type == KEYUP:
            if evt.key == K_UP:
                keys[0] = False
            elif evt.key == K_LEFT:
                keys[1] = False
            elif evt.key == K_DOWN:
                keys[2] = False
            elif evt.key == K_RIGHT:
                keys[3] = False
        
        if evt.type == MOUSEBUTTONDOWN:
            shoot.play()
            pos = pygame.mouse.get_pos()
            n_shots += 1
            # adding rotate angle, dir of bullet
            bullets.append([atan2(pos[1]-(player_ny+32), pos[0]-(player_nx+26)), 
                           player_nx+32, player_ny+32])
        
    # Move player according to key press
    if keys[0]:
        player_y -= 5
    elif keys[2]:
        player_y += 5
    elif keys[1]:
        player_x -= 5
    elif keys[3]:
        player_x += 5
        
    if pygame.time.get_ticks() >= 90000:
        running = False
        exitcode = 1
    if max_health <= 0:
        running = False
        exitcode = 0
    
    if n_shots != 0:
        accuracy = n_hits*100.0/n_shots
    else:
        accuracy = 0

if exitcode == 0:
    pygame.font.init()
    font = pygame.font.Font(None, 24)
    text = font.render("Accuracy: %0.2f" %accuracy + "%", True, (255,0,0))
    textRect = text.get_rect()
    textRect.centerx = display_surf.get_rect().centerx
    textRect.centery = display_surf.get_rect().centery+24
    display_surf.blit(gameover, (0,0))
    display_surf.blit(text, textRect)
    
else:
    pygame.font.init()
    font = pygame.font.Font(None, 24)
    text = font.render("Accuracy: %0.2f" %accuracy + "%", True, (0,255,0))
    textRect = text.get_rect()
    textRect.centerx = display_surf.get_rect().centerx
    textRect.centery = display_surf.get_rect().centery+24
    display_surf.blit(win, (0,0))
    display_surf.blit(text, textRect)
    
while True:
    for evt in pygame.event.get():
        if evt.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.flip()
    
    
    