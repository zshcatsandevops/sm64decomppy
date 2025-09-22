#!/usr/bin/env python3
# Super Mario 3D World - Open World Playground (Solid Ground)
from ursina import *
import random, math, os

app = Ursina()
window.title = "Super Mario 3D World - Open World Playground"
window.size = (1280, 720)
window.borderless = False
window.fps_counter.enabled = True

# --------------------------
# Textures and Materials
# --------------------------
try:
    # Try to load some basic textures (you can replace these with actual Mario textures)
    grass_texture = load_texture('assets/grass.png') if os.path.exists('assets/grass.png') else None
    brick_texture = load_texture('assets/brick.png') if os.path.exists('assets/brick.png') else None
except:
    grass_texture = None
    brick_texture = None

# --------------------------
# Mario Player with Enhanced Movement
# --------------------------
class Mario(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube', 
            color=color.red,  # Mario's iconic red color
            scale=(0.8, 1.6, 0.8), 
            collider='box', 
            **kwargs
        )
        self.speed = 7
        self.jump_power = 10
        self.gravity = 30
        self.y_vel = 0
        self.grounded = False
        self.turn_speed = 180  # Degrees per second for smooth turning
        self.is_running = False
        self.coins_collected = 0
        
        # Simple animation states
        self.jump_animation = 0
        self.base_scale_y = 1.6
        
    def update(self):
        # Continuous turning (A: left/CCW, D: right/CW)
        turn_input = held_keys['a'] - held_keys['d']
        self.rotation_y += turn_input * self.turn_speed * time.dt
        
        # Relative forward/back movement
        self.is_running = held_keys['shift']
        current_speed = self.speed * (1.5 if self.is_running else 1.0)
        forward_input = held_keys['w'] - held_keys['s']
        move = self.forward * forward_input * current_speed * time.dt
        self.position += move
        
        # Jump with animation
        if self.grounded:
            if held_keys['space']:
                self.y_vel = self.jump_power
                self.grounded = False
                self.jump_animation = 1
        
        # Upward raycast for hitting question blocks from below
        if self.y_vel > 0:
            hit_up = raycast(
                self.position + (0, 0.8, 0), 
                direction=(0, 1, 0),
                distance=0.5, 
                ignore=[self]
            )
            if hit_up.hit and isinstance(hit_up.entity, QuestionBlock) and hit_up.entity.active:
                hit_up.entity.hit()
                self.y_vel *= -0.5  # Gentle bounce-back
        
        # Gravity
        self.y_vel -= self.gravity * time.dt
        self.y += self.y_vel * time.dt
        
        # Ground check with better collision
        hit = raycast(
            self.position + (0, 0.1, 0), 
            direction=(0, -1, 0),
            distance=1.2, 
            ignore=[self]
        )
        
        if hit.hit:
            self.grounded = True
            self.y = hit.world_point.y + 0.8
            self.y_vel = max(0, self.y_vel)  # Prevent sticking to ceiling
            self.jump_animation = 0
        else:
            self.grounded = False
            
        # Simple scale animation for jumping
        if self.jump_animation > 0:
            self.scale_y = self.base_scale_y + math.sin(self.jump_animation * 10) * 0.2
            self.jump_animation -= time.dt

# --------------------------
# Collectible Coins
# --------------------------
class Coin(Entity):
    def __init__(self, position, **kwargs):
        super().__init__(
            model='sphere',
            color=color.yellow,
            scale=0.5,
            position=position,
            collider='sphere',
            **kwargs
        )
        self.original_y = self.y
        self.rotation_speed = 100
        
    def update(self):
        self.rotation_y += time.dt * self.rotation_speed
        # Bobbing animation (no drift)
        self.y = self.original_y + math.sin(time.time() * 5) * 0.05

# --------------------------
# Question Blocks
# --------------------------
class QuestionBlock(Entity):
    def __init__(self, position, **kwargs):
        super().__init__(
            model='cube',
            color=color.orange,
            scale=(1, 1, 1),
            position=position,
            collider='box',
            **kwargs
        )
        self.active = True
        self.bounce_animation = 0
        self.original_y = self.y
        
    def hit(self):
        if self.active:
            self.active = False
            self.bounce_animation = 1
            self.color = color.gray  # Change color when hit
            # Spawn a coin
            coin = Coin(position=self.position + (0, 2, 0))
            invoke(destroy, coin, delay=2)  # Remove coin after 2 seconds
            
    def update(self):
        if self.bounce_animation > 0:
            self.y = self.original_y + math.sin(self.bounce_animation * 10) * 0.1
            self.bounce_animation -= time.dt
            if self.bounce_animation < 0:
                self.bounce_animation = 0
                self.y = self.original_y

# --------------------------
# Enhanced Terrain
# --------------------------
def create_enhanced_terrain(size=40):
    # Main ground
    ground = Entity(
        model='plane',
        texture=grass_texture,
        scale=size,
        position=(0, 0, 0),
        collider='mesh'
    )
    
    # Add some platforms at different heights
    platform_heights = [3, 5, 8]
    for height in platform_heights:
        for i in range(3):
            platform = Entity(
                model='cube',
                color=color.green,
                scale=(5, 0.5, 3),
                position=(random.randint(-15, 15), height, random.randint(-15, 15)),
                collider='box'
            )
    
    # Add some hills
    for i in range(10):
        hill = Entity(
            model='sphere',
            color=color.lime,
            scale=(random.uniform(2, 5), random.uniform(1, 3), random.uniform(2, 5)),
            position=(random.randint(-18, 18), 0, random.randint(-18, 18)),
            collider='sphere'
        )
        hill.y = hill.scale_y / 2  # Position on ground

# --------------------------
# Environment Decorations
# --------------------------
def create_environment():
    # Trees with better appearance
    for i in range(30):
        trunk_height = random.uniform(2, 4)
        tree_trunk = Entity(
            model='cylinder',
            color=color.brown,
            scale=(0.5, trunk_height, 0.5),
            position=(random.randint(-35, 35), trunk_height/2, random.randint(-35, 35)),
            collider='mesh'
        )
        
        tree_top = Entity(
            model='sphere',
            color=color.rgb(0, random.randint(100, 150), 0),
            scale=random.uniform(2, 4),
            position=tree_trunk.position + (0, trunk_height, 0)
        )
    
    # Flowers and bushes
    for i in range(50):
        bush = Entity(
            model='sphere',
            color=color.rgb(random.randint(0, 255), random.randint(100, 200), 0),
            scale=random.uniform(0.5, 1.5),
            position=(random.randint(-38, 38), 0.5, random.randint(-38, 38))
        )
        bush.y = bush.scale_y / 2

# --------------------------
# UI Elements
# --------------------------
class GameUI:
    def __init__(self):
        self.coin_text = Text(
            text='Coins: 0',
            position=(-0.8, 0.45),
            scale=2,
            color=color.yellow
        )
        
        self.instructions = Text(
            text='WASD: Move/Turn | SPACE: Jump | SHIFT: Run',
            position=(-0.8, 0.4),
            scale=1.5,
            color=color.white
        )

# --------------------------
# Main Game Setup
# --------------------------
# Skybox
sky = Sky(color=color.rgb(135, 206, 235))

# Create world
create_enhanced_terrain(80)
create_environment()

# Create Mario
mario = Mario(position=(0, 5, 0))

# Create coins
coins = []
for i in range(20):
    coin = Coin(position=(
        random.randint(-35, 35),
        2,
        random.randint(-35, 35)
    ))
    coins.append(coin)

# Create question blocks
question_blocks = []
for i in range(10):
    block = QuestionBlock(position=(
        random.randint(-30, 30),
        3,
        random.randint(-30, 30)
    ))
    question_blocks.append(block)

# Setup UI
game_ui = GameUI()

# --------------------------
# Collision Detection
# --------------------------
def update():
    # Update coin collection
    for coin in coins[:]:
        if coin.intersects(mario).hit:
            coins.remove(coin)
            destroy(coin)
            mario.coins_collected += 1
            game_ui.coin_text.text = f'Coins: {mario.coins_collected}'
    
    # Smooth chase cam with better angles
    target_position = mario.position + Vec3(0, 8, -12)
    camera.position = lerp(camera.position, target_position, time.dt * 6)
    
    # Make camera look slightly ahead of Mario
    look_target = mario.position + mario.forward * 3 + Vec3(0, 2, 0)
    camera.look_at(look_target)
    
    # Water death plane
    if mario.y < -10:
        mario.position = (0, 10, 0)
        mario.y_vel = 0

# --------------------------
# Input Handling
# --------------------------
def input(key):
    if key == 'escape':
        application.quit()
    elif key == 'r':
        # Reset game
        mario.position = (0, 10, 0)
        mario.coins_collected = 0
        game_ui.coin_text.text = 'Coins: 0'

# --------------------------
# Start the Game
# --------------------------
if __name__ == '__main__':
    print("Super Mario 3D World - Open World Playground")
    print("Controls: W/S forward/back, A/D turn, SPACE to jump, SHIFT to run")
    print("Find and collect all the coins!")
    
    app.run()
