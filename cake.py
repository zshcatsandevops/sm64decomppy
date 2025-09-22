#!/usr/bin/env python3
# B3313-like Cake Level Demo (fixed geometry)
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math, random

app = Ursina()
window.title = "B3313 Cake Room - Fixed Cake Level"
window.size = (1280, 720)

# --- Materials ---
floor_color = color.rgb(255, 220, 200)   # cake base
frosting_color = color.rgb(255, 240, 240)
star_color = color.yellow

# --- Entities ---
# Cake floor as disk mesh (instead of missing cylinder)
cake_floor = Entity(
    model=Mesh(vertices=[Vec3(math.cos(a)*6,0,math.sin(a)*6) for a in [i*math.pi/24 for i in range(48)]] + [Vec3(0,0,0)],
               triangles=[[i, (i+1)%48, 48] for i in range(48)],
               mode='triangle'),
    color=floor_color,
    scale=2,
    y=0,
    collider='mesh'
)

# Frosting pillars
for i in range(12):
    angle = i * 30
    x, z = 8*math.cos(math.radians(angle)), 8*math.sin(math.radians(angle))
    Entity(model='cube', color=frosting_color, scale=(1,3,1), position=(x,1.5,z), collider='box')

# Star
star = Entity(model='sphere', color=star_color, scale=1.5, y=3, glow=1)

# Floating candles
for i in range(6):
    Entity(model='cube', color=color.orange, scale=(0.2,1,0.2),
           position=(random.uniform(-4,4), 2.5, random.uniform(-4,4)), glow=0.5)

# Player
player = FirstPersonController(y=2, speed=5)
player.cursor.visible = False

# Lighting
DirectionalLight(shadows=True).look_at(Vec3(1,-1,-1))
Sky(color=color.rgb(200,180,200))

# Win condition
def update():
    if distance(player.position, star.position) < 2:
        print(">>> STAR COLLECTED - LEVEL COMPLETE <<<")
        application.quit()

app.run()
