import cv2
import numpy as np
from random import randint
from time import time

cicle_time = 0.03

class GameObject:

    def __init__(self, x, y, texture_path):

        self.x = x
        self.y = y
        self.texture_path = texture_path
        if texture_path == "":
            self.texture = np.zeros(shape=(50, 50, 4), dtype=np.uint8)
        else:
            self.texture = cv2.imread(texture_path, -1)
        self.w = self.texture.shape[1]
        self.h = self.texture.shape[0]

    def set_texture_path(self, texture_path):

        self.texture_path = texture_path
        if texture_path == "":
            self.texture = np.zeros(shape=(50, 50, 4), dtype=np.uint8)
        else:
            self.texture = cv2.imread(texture_path, -1)
        self.w = self.texture.shape[1]
        self.h = self.texture.shape[0]

    def update(self, vx, vy):
        self.x = round(self.x + vx*cicle_time, 0)
        self.y = round(self.y + vy*cicle_time, 0)

    def render(self, image):

        int_x = int(self.x)
        int_y = int(self.y)
        int_w = int(self.w)
        int_h = int(self.h)

        min_tex_x = 0

        min_tex_y = 0

        min_img_x = int_x
        max_img_x = int_x + int_w

        min_img_y = int_y
        max_img_y = int_y + int_h

        if int_x < 0:
            min_tex_x = -int_x
            min_img_x = 0

        if int_x + int_w >= image.shape[1]:
            max_img_x = image.shape[1]
        
        if int_y < 0:
            min_tex_y = -int_y
            min_img_y = 0
        
        if int_y + int_h > image.shape[0]:
            max_img_y = image.shape[0]
        
        max_tex_x = min_tex_x + (max_img_x - min_img_x)
        max_tex_y = min_tex_y + (max_img_y - min_img_y)

        if int_x + int_w < 0 or int_x > image.shape[1] or int_y + int_h < 0 or int_y > image.shape[0]:
            return False

        cropped_image = self.texture[min_tex_y: max_tex_y, min_tex_x: max_tex_x]    

        image[min_img_y : max_img_y, min_img_x : max_img_x] = cropped_image

class Block(GameObject):
    
    def check_collision(self, x, y, w, h):

        if (x <= self.x and x+w >= self.x) or (x <= self.x+self.w and x+w >= self.x+self.w):
            if (y >= self.y and y <= self.y + self.h) or (y+h >= self.y and y+h <= self.y + self.h):
                return True
        if (y <= self.y and y+h >= self.y) or (y <= self.y+self.h and y+h >= self.y+self.h):
            if (x >= self.x and x <= self.x + self.w) or (x+w >= self.x and x+w <= self.x + self.w):
                return True
        return False

class Player(GameObject):

    pass


player = Player(100, 400, "textures/player.png")

skys = [GameObject(0, 0, "textures/sky.png"), GameObject(600, 0, "textures/sky.png")]

blocks = []

for x in range(0, 650, 50):
    blocks.append(Block(x, 700, "textures/grass.png"))
    blocks.append(Block(x, 750, "textures/dirt.png"))
    blocks.append(Block(x, -50, ""))

pipes = []

last_height = 400
possible_range = 700

def generate_initial_pipes():
    global last_height
    counter_x = 0
    for x in range(300, 1000, 200):
        pipes.append([])
        height = randint(max(last_height-possible_range, 50), min(last_height+possible_range, 450))
        counter_y = 0
        for y in range(0, height, 50):
            if counter_y == 0:
                pipes[counter_x].append(Block(x, y, "textures/pipe2.png"))
            else:
                pipes[counter_x][counter_y-1].set_texture_path("textures/pipe3.png")
                pipes[counter_x].append(Block(x, y, "textures/pipe2.png"))
            counter_y += 1
        last_count = counter_y
        counter_y = 0
        for y in range(650, height+200, -50):
            if counter_y == 0:
                pipes[counter_x].append(Block(x, y, "textures/pipe1.png"))
            else:
                pipes[counter_x][last_count+counter_y-1].set_texture_path("textures/pipe3.png")
                pipes[counter_x].append(Block(x, y, "textures/pipe1.png"))
            counter_y += 1
        last_height = height
        counter_x += 1



generate_initial_pipes()

player_velocity_y = 0
velocity = 200
pontuation = 0
initialization_time = time()
max_elapsed_time = 0

while True:

    initial_time = time()

    key = cv2.waitKey(1)

    image = np.zeros(shape=(800, 600, 4), dtype=np.uint8)

    for sky in skys:
        sky.update(-velocity*1.2, 0)
        if sky.x < -sky.w:
            sky.x = image.shape[1] + (sky.x + sky.w)
        sky.render(image)

    player_velocity_y += 100

    velocity += .1

    elapsed_time = time() - initialization_time
    if elapsed_time > max_elapsed_time:
        max_elapsed_time = elapsed_time

    if key == 0:
        player_velocity_y = -700
    player.update(0, player_velocity_y)
    player.render(image)

    for block in blocks:
        block.update(-velocity, 0)
        if block.x < -block.w:
            block.x = image.shape[1] + (block.x + block.w)
        block.render(image)
        if block.check_collision(player.x, player.y, player.w, player.h):
            player.x = 100
            player.y = 400
            player_velocity_y = 0
            velocity = 200
            del pipes[:]
            initialization_time = time()
            generate_initial_pipes()
    
    for pipe in pipes:
        if pipe[0].x + pipe[0].w >= 0:
            for block in pipe:
                block.update(-velocity, 0)
                block.render(image)
                if block.check_collision(player.x, player.y, player.w, player.h):
                    player.x = 100
                    player.y = 400
                    player_velocity_y = 0
                    velocity = 200
                    del pipes[:]
                    initialization_time = time()
                    generate_initial_pipes()
        else:
            del pipe[:]
            height = randint(max(last_height-possible_range, 50), min(last_height+possible_range, 450))
            counter_y = 0
            for y in range(0, height, 50):
                if counter_y == 0:
                    pipe.append(Block(image.shape[1] + 150, y, "textures/pipe2.png"))
                else:
                    pipe[counter_y-1].set_texture_path("textures/pipe3.png")
                    pipe.append(Block(image.shape[1] + 150, y, "textures/pipe2.png"))
                counter_y += 1
            last_count = counter_y
            counter_y = 0
            for y in range(650, height+200, -50):
                if counter_y == 0:
                    pipe.append(Block(image.shape[1] + 150, y, "textures/pipe1.png"))
                else:
                    pipe[last_count+counter_y-1].set_texture_path("textures/pipe3.png")
                    pipe.append(Block(image.shape[1] + 150, y, "textures/pipe1.png"))
                counter_y += 1
            last_height = height

    cv2.putText(image, "Record: " + str(int(max_elapsed_time)) + " segundos", (100, 50), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 0, 0))
    cv2.putText(image, "Voce sobreviveu " + str(int(elapsed_time)) + " segundos", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 0, 0))

    cv2.imshow("Flappy Bird", image)

    while time() - initial_time < cicle_time:
        pass

    if key == 27:
        exit(0)