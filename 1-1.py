#!/usr/bin/env python3
# Super Mario 3D World - Open World Playground (Solid Ground)
from ursina import *
import random, math

app = Ursina()
window.title = "Super Mario 3D World - Open World Playground"
window.size = (1280, 720)
window.color = color.rgb(135, 206, 235)   # sky blue

# --------------------------
# Mario Player
# --------------------------
class Mario(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='cube', color=color.azure,
                         scale=(0.8,1.6,0.8), collider='box', **kwargs)
        self.speed = 7
        self.jump_power = 9
        self.gravity = 25
        self.y_vel = 0
        self.grounded = False

    def update(self):
        # 8-dir movement
        move = Vec3(held_keys['d']-held_keys['a'], 0,
                    held_keys['w']-held_keys['s']).normalized()
        self.position += move * time.dt * self.speed

        # Jump
        if self.grounded and held_keys['space']:
            self.y_vel = self.jump_power
            self.grounded = False

        # Gravity
        self.y_vel -= self.gravity * time.dt
        self.y += self.y_vel * time.dt

        # Ground check
        hit = raycast(self.position+(0,0.1,0), direction=(0,-1,0),
                      distance=1.2, ignore=[self])
        if hit.hit:
            self.grounded = True
            self.y = hit.world_point.y + 0.8
            self.y_vel = 0

# --------------------------
# Terrain
# --------------------------
def create_grass_world(size=40):
    for x in range(-size//2, size//2):
        for z in range(-size//2, size//2):
            Entity(model='cube',
                   color=color.lime,
                   texture='white_cube',
                   texture_scale=(2,2),
                   position=(x,0,z),
                   scale=(1,1,1),
                   collider='box')

create_grass_world(100)  # 100x100 block world

# Decorative "trees"
for i in range(60):
    Entity(model='cube',
           color=color.rgb(0, random.randint(150,200), 0),
           scale=(random.uniform(1,3), random.uniform(2,6), random.uniform(1,3)),
           position=(random.randint(-40,40),1,random.randint(-40,40)),
           collider='box')

# --------------------------
# Entities
# --------------------------
mario = Mario(position=(0,2,0))

# --------------------------
# Camera follow
# --------------------------
camera.fov = 75
camera.rotation_x = 20

def update():
    # Smooth chase cam
    camera.position = lerp(camera.position,
                           mario.position + Vec3(0,12,-20),
                           time.dt*5)
    camera.look_at(mario.position + Vec3(0,2,0))

app.run()
