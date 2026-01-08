import pgzrun
import random
import math
import time
import pygame
WIDTH = 512
HEIGHT = 512


town_names = "a b d e f g h i j k l m o p".split()
locate = [Actor(name, (256, 256)) for name in town_names]
town_dict = {town.image: town for town in locate}


hero = Actor("men", (256, 490))
enemy = Actor("shadow", (300, 300))

hero.health = 100
enemy.strong = 50


npc_names = ["ofice", "sur", "fermer", "yong"]
npc_actor = None 


npc_dialogues = {
    "ofice": "Привет! Я из офиса. Спасибо за посылку !",
    "sur": "Я выживший. Спасибо за еду.",
    "fermer": "Здравствуй! У меня есть лучшие овощи в округе.",
    "yong": "Я юный выживший! Когда-нибудь я спасу мир! "
}


game_over = False
enemy_frozen = False
enemy_freeze_time = 0
freeze_duration = 5
score = 0   
npc_rewarded = False 
music_playing = False

lasers = []
last_shot = 0
shoot_delay = 1.5

def shoot_laser(direction):
    if direction in ("up", "down"):
        laser = Actor("laser", (enemy.x, enemy.y))
        sounds.sound_laser.play
    else:
        laser = Actor("laser_d", (enemy.x, enemy.y))
        sounds.sound_laser.play
    laser.dir = direction
    lasers.append(laser)
    

# --- НАСТРОЙКИ КАРТ ---
map_settings = {
    "a": {"borders": {"left":110,"right":110,"top":0,"bottom":0}, "spawn":"bottom"},
    "b": {"borders": {"left":0,"right":0,"top":110,"bottom":110}, "spawn":"left"},
    
    "d": {"borders": {"left":110,"right":0,"top":110,"bottom":0}, "spawn":"right"},
    "e": {"borders": {"left":0,"right":110,"top":110,"bottom":0}, "spawn":"bottom"},
    "f": {"borders": {"left":0,"right":110,"top":0,"bottom":110}, "spawn":"left"},
    "g": {"borders": {"left":0,"right":110,"top":0,"bottom":0}, "spawn":"top"},
    "h": {"borders": {"left":0,"right":0,"top":0,"bottom":110}, "spawn":"right"},
    "i": {"borders": {"left":110,"right":0,"top":0,"bottom":0}, "spawn":"bottom"},
    "j": {"borders": {"left":0,"right":0,"top":110,"bottom":0}, "spawn":"left"},
    "k": {"borders": {"left":0,"right":0,"top":0,"bottom":110}, "spawn":"right"},
    "l": {"borders": {"left":0,"right":110,"top":110,"bottom":110}, "spawn":"left"},
    "m": {"borders": {"left":110,"right":110,"top":110,"bottom":0}, "spawn":"bottom"},
    "o": {"borders": {"left":110,"right":0,"top":110,"bottom":110}, "spawn":"right"},
    "p": {"borders": {"left":110,"right":110,"top":0,"bottom":110}, "spawn":"top"},
}

draw_map = town_dict["a"]


def get_settings():
    return map_settings[draw_map.image]

def change_map(new_map_name):
    global draw_map, enemy, npc_actor, npc_rewarded
    draw_map = town_dict[new_map_name]
    spawn_side = map_settings[draw_map.image]["spawn"]

    if spawn_side == "top":
        hero.pos = (WIDTH//2, 50)
    elif spawn_side == "bottom":
        hero.pos = (WIDTH//2, HEIGHT-50)
    elif spawn_side == "left":
        hero.pos = (50, HEIGHT//2)
    elif spawn_side == "right":
        hero.pos = (WIDTH-50, HEIGHT//2)

    if new_map_name in ["p", "o", "m", "l"]:
        npc_actor = Actor(random.choice(npc_names), (WIDTH//2, HEIGHT//2))
        enemy.pos = (-100, -100)
        npc_rewarded = False  
    else:
        npc_actor = None
        enemy.pos = (WIDTH//2, HEIGHT//2)

def check_map_transition():
    borders = get_settings()["borders"]

    if borders["bottom"] == 0 and hero.y >= HEIGHT:
        change_map(random.choice(list(map_settings.keys())))
    elif borders["top"] == 0 and hero.y <= 0:
        change_map(random.choice(list(map_settings.keys())))
    elif borders["right"] == 0 and hero.x >= WIDTH:
        change_map(random.choice(list(map_settings.keys())))
    elif borders["left"] == 0 and hero.x <= 0:
        change_map(random.choice(list(map_settings.keys())))
def music():
    pygame.mixer.music.load("sounds/music.wav")
    pygame.mixer.music.play(-1)
def stop_music():
    pygame.mixer.music.stop()


def reset_game():
    global hero, enemy, lasers, game_over, draw_map, last_shot, npc_actor, enemy_frozen, score
    hero.pos = (256, 490)
    hero.health = 100
    enemy.pos = (300, 300)
    enemy.image = "shadow"
    lasers = []
    draw_map = town_dict["a"]
    npc_actor = None
    game_over = False
    last_shot = 0
    enemy_frozen = False
    score = 0

def update(dt):
    global last_shot, game_over, enemy_frozen, enemy_freeze_time, score, npc_rewarded

    if game_over:
        if keyboard.r:
            reset_game()
        return

    speed = 1
    borders = get_settings()["borders"]

    if keyboard.right and hero.x < WIDTH - borders["right"]:
        hero.x += speed
        hero.image = "men_a"
        

    if keyboard.left and hero.x > borders["left"]:
        hero.x -= speed
        hero.image = "men_s"
        

    if keyboard.up and hero.y > borders["top"]:
        hero.y -= speed
        hero.image = "men_back"
        

    if keyboard.down and hero.y < HEIGHT - borders["bottom"]:
        hero.y += speed
        hero.image = "men"
        

    if npc_actor and hero.colliderect(npc_actor) and not npc_rewarded:
        score += 10
        npc_rewarded = True

  
    if npc_actor is None:
        if enemy_frozen:
            if time.time() - enemy_freeze_time >= freeze_duration:
                enemy_frozen = False
                enemy.image = "shadow"
            return

        if hero.colliderect(enemy):
            enemy_frozen = True
            enemy_freeze_time = time.time()
            enemy.image = "shadow_stan"
            sounds.knife.play()
            return

        enemy_speed = 0.5
        dx = hero.x - enemy.x
        dy = hero.y - enemy.y
        dist = math.hypot(dx, dy)

        direction = None
        if abs(dx) > abs(dy):
            if dx > 0:
                enemy.image = "shadow_d"
                direction = "right"
            else:
                enemy.image = "shadow_a"
                direction = "left"
        else:
            if dy < 0:
                enemy.image = "shadow_back"
                direction = "up"
            else:
                enemy.image = "shadow"
                direction = "down"

        if dist > 1:
            enemy.x += dx / dist * enemy_speed
            enemy.y += dy / dist * enemy_speed

        now = time.time()
        if direction and now - last_shot > shoot_delay:
             now = time.time()
        if direction and now - last_shot > shoot_delay:
            shoot_laser(direction)
             
            last_shot = now
             
            

        for laser in lasers[:]:
            if laser.dir == "up":
                laser.y -= 3
            elif laser.dir == "down":
                laser.y += 3
            elif laser.dir == "left":
                laser.x -= 3
            elif laser.dir == "right":
                laser.x += 3

            if laser.colliderect(hero):
                hero.health -= 100
                lasers.remove(laser)
                if hero.health <= 0:
                    hero.health = 0
                    game_over = True
            elif (laser.x < 0 or laser.x > WIDTH or
                  laser.y < 0 or laser.y > HEIGHT):
                lasers.remove(laser)

    check_map_transition()

def draw():
    global music_playing
    if  not music_playing:
         music()
         music_playing = True


    
    if game_over:
        screen.fill("gray")
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2 - 20), fontsize=60, color="red")
        screen.draw.text("Press R to Restart", center=(WIDTH//2, HEIGHT//2 + 40), fontsize=40, color="white")
        screen.draw.text(f"очки: {score}",center=(WIDTH//2, HEIGHT//2 + 60), fontsize=30, color="green")

        stop_music()
        music_playing = False
        return

    screen.clear()
    draw_map.draw()
    hero.draw()

    if npc_actor:
        npc_actor.draw()
        if hero.colliderect(npc_actor):
            dialog = npc_dialogues[npc_actor.image]
            screen.draw.filled_rect(Rect((20, HEIGHT-80), (WIDTH-40, 60)), (0,0,0))
            screen.draw.text(dialog, (30, HEIGHT-70), fontsize=24, color="white")
    else:
        enemy.draw()
        for laser in lasers:
            laser.draw()
        if enemy_frozen:
            left = freeze_duration - int(time.time() - enemy_freeze_time)
            if left > 0:
                screen.draw.text(f"СТОИТ {left}", center=(enemy.x, enemy.y-40), fontsize=24, color="yellow")

    
    screen.draw.text(f"HP: {hero.health}", (10, 10), fontsize=30, color="red")
    screen.draw.text(f"SCORE: {score}", (10, 50), fontsize=30, color="green")

pgzrun.go()