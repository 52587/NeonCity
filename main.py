import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import perlin as noise
import math

# --- Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
COLOR_BUILDING = (0.08, 0.08, 0.1, 1.0)
COLOR_WINDOW_OFF = (0.04, 0.04, 0.06, 1.0)

# Cyberpunk Themes
THEMES = [
    {
        'name': 'Neon Cool',
        'bg': (0.04, 0.04, 0.12, 1.0),
        'lights': [(0.39, 0.78, 1.0), (0.20, 0.39, 1.0), (0.78, 0.39, 1.0)]
    },
    {
        'name': 'Neon Warm',
        'bg': (0.12, 0.04, 0.04, 1.0),
        'lights': [(1.0, 0.78, 0.39), (1.0, 0.59, 0.20), (1.0, 0.39, 0.20)]
    },
    {
        'name': 'The Matrix',
        'bg': (0.0, 0.1, 0.0, 1.0),
        'lights': [(0.0, 1.0, 0.4), (0.2, 0.9, 0.2), (0.8, 1.0, 0.8)]
    },
    {
        'name': 'Vaporwave',
        'bg': (0.1, 0.05, 0.15, 1.0),
        'lights': [(1.0, 0.0, 0.8), (0.0, 0.9, 1.0), (1.0, 0.9, 0.2)]
    },
    {
        'name': 'Toxic',
        'bg': (0.05, 0.05, 0.0, 1.0),
        'lights': [(0.8, 1.0, 0.0), (0.6, 0.0, 0.8), (0.0, 0.8, 0.2)]
    }
]

# --- Classes ---

class Particle:
    display_list = None

    def __init__(self, x, y, z, color):
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.1, 0.3)
        self.vx = math.cos(angle) * speed
        self.vy = random.uniform(0.1, 0.5) # Upward burst
        self.vz = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(0.03, 0.06)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        self.vy -= 0.01 # Gravity
        self.life -= self.decay
        return self.life > 0

    @classmethod
    def get_display_list(cls):
        if cls.display_list is None:
            cls.display_list = glGenLists(1)
            glNewList(cls.display_list, GL_COMPILE)
            size = 0.1
            glBegin(GL_QUADS)
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    for dz in [-1, 1]:
                        glVertex3f(dx*size, dy*size, dz*size)
            glEnd()
            glEndList()
        return cls.display_list

    def draw(self):
        if self.life > 0:
            glColor4f(*self.color, self.life)
            glPushMatrix()
            glTranslatef(self.x, self.y, self.z)
            glCallList(self.get_display_list())
            glPopMatrix()

class Building:
    def __init__(self, x, z, width, height, depth, theme_colors):
        self.x = x
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth
        self.theme_colors = theme_colors
        self.windows = []
        self.display_list = None
        
        # Generate windows on 4 faces
        # Simplified: just front and back for now, or all 4
        # Let's do all 4 faces
        win_size = 0.15
        gap = 0.05
        
        # Calculate rows/cols based on physical size
        cols_x = max(1, int((width - gap) / (win_size + gap)))
        cols_z = max(1, int((depth - gap) / (win_size + gap)))
        rows = max(1, int((height - gap) / (win_size + gap)))
        
        # Helper to add windows for a face
        def add_face_windows(start_x, start_z, is_x_face):
            cols = cols_x if is_x_face else cols_z
            face_width = width if is_x_face else depth
            
            start_offset = (face_width - (cols * (win_size + gap))) / 2
            
            for r in range(rows):
                for c in range(cols):
                    offset = start_offset + c * (win_size + gap)
                    y = gap + r * (win_size + gap)
                    
                    is_lit = random.random() > 0.7
                    color = random.choice(self.theme_colors)
                    
                    if is_x_face:
                        # Front/Back faces
                        wx = start_x + offset
                        wz = start_z
                        self.windows.append({'pos': (wx, y, wz), 'lit': is_lit, 'color': color, 'axis': 'x'})
                    else:
                        # Left/Right faces
                        wx = start_x
                        wz = start_z + offset
                        self.windows.append({'pos': (wx, y, wz), 'lit': is_lit, 'color': color, 'axis': 'z'})

        # Front Face (z + depth)
        add_face_windows(0, depth, True)
        # Back Face (z)
        add_face_windows(0, 0, True)
        # Left Face (x)
        add_face_windows(0, 0, False)
        # Right Face (x + width)
        add_face_windows(width, 0, False)

    def flicker_window(self):
        if not self.windows: return
        # Pick one random window to toggle
        win = random.choice(self.windows)
        win['lit'] = not win['lit']
        
        if self.display_list is not None:
            glDeleteLists(self.display_list, 1)
            self.display_list = None

    def draw_geometry(self):
        glPushMatrix()
        glTranslatef(self.x, 0, self.z)
        
        # Draw Building Body
        glColor4f(*COLOR_BUILDING)
        w, h, d = self.width, self.height, self.depth
        
        glBegin(GL_QUADS)
        # Front
        glVertex3f(0, 0, d); glVertex3f(w, 0, d); glVertex3f(w, h, d); glVertex3f(0, h, d)
        # Back
        glVertex3f(0, 0, 0); glVertex3f(0, h, 0); glVertex3f(w, h, 0); glVertex3f(w, 0, 0)
        # Left
        glVertex3f(0, 0, 0); glVertex3f(0, 0, d); glVertex3f(0, h, d); glVertex3f(0, h, 0)
        # Right
        glVertex3f(w, 0, 0); glVertex3f(w, h, 0); glVertex3f(w, h, d); glVertex3f(w, 0, d)
        # Top
        glVertex3f(0, h, 0); glVertex3f(0, h, d); glVertex3f(w, h, d); glVertex3f(w, h, 0)
        glEnd()
        
        # Draw Windows
        # Use Polygon Offset to handle Z-fighting cleanly
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(-1.0, -1.0)
        
        win_s = 0.15
        
        glBegin(GL_QUADS)
        for win in self.windows:
            if win['lit']:
                glColor3f(*win['color'])
            else:
                glColor4f(*COLOR_WINDOW_OFF)
            
            wx, wy, wz = win['pos']
            
            if win['axis'] == 'x':
                # On front or back face
                glVertex3f(wx, wy, wz)
                glVertex3f(wx + win_s, wy, wz)
                glVertex3f(wx + win_s, wy + win_s, wz)
                glVertex3f(wx, wy + win_s, wz)
            else:
                # On left or right face
                glVertex3f(wx, wy, wz)
                glVertex3f(wx, wy, wz + win_s)
                glVertex3f(wx, wy + win_s, wz + win_s)
                glVertex3f(wx, wy + win_s, wz)
        glEnd()
        glDisable(GL_POLYGON_OFFSET_FILL)
        
        glPopMatrix()

    def draw(self):
        if self.display_list is None:
            self.display_list = glGenLists(1)
            glNewList(self.display_list, GL_COMPILE)
            self.draw_geometry()
            glEndList()

        glCallList(self.display_list)

    def cleanup(self):
        if self.display_list is not None:
            glDeleteLists(self.display_list, 1)
            self.display_list = None

# 2D UI Overlay Helper
def draw_text(x, y, text, font):
    text_surface = font.render(text, True, (255, 255, 255, 255), (0,0,0,0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    w, h = text_surface.get_width(), text_surface.get_height()
    
    glWindowPos2d(x, SCREEN_HEIGHT - y - h)
    glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

# --- Main Application ---

def main():
    pygame.init()
    
    # Enable Multisampling (MSAA) for smoother edges
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Neon City 3D")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)

    # OpenGL Setup
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glEnable(GL_MULTISAMPLE) # Ensure MSAA is on
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Fog Setup to hide distant aliasing
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, 15.0)
    glFogf(GL_FOG_END, 45.0)

    def set_projection():
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (SCREEN_WIDTH / SCREEN_HEIGHT), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    set_projection()

    # State
    state = {
        'density': 50, 
        'theme_index': 0,
        'buildings': [],
        'particles': [],
        'cam_x': 0,
        'cam_z': 20,
        'cam_angle': 0,
        'rot_speed': 0.005,
        'is_paused': False
    }

    def generate_city():
        for b in state['buildings']:
            b.cleanup()
        state['buildings'] = []
        
        target_count = state['density']
        
        # Calculate map size based on density
        # Use sqrt to scale area proportionally to count
        map_size = math.sqrt(target_count) * 4.0
        half_map = map_size / 2.0
        
        attempts = 0
        max_attempts = target_count * 100 # Avoid infinite loops
        
        noise_scale = 0.1
        
        current_theme = THEMES[state['theme_index']]
        theme_colors = current_theme['lights']

        while len(state['buildings']) < target_count and attempts < max_attempts:
            attempts += 1
            
            # Randomize dimensions for organic variety
            b_width = random.uniform(0.8, 2.0)
            b_depth = random.uniform(0.8, 2.0)
            
            # Random position within map bounds
            bx = random.uniform(-half_map, half_map - b_width)
            bz = random.uniform(-half_map, half_map - b_depth)
            
            # Collision Check (AABB)
            collision = False
            min_gap = 0.4 # Minimum alley width
            
            for other in state['buildings']:
                if (bx < other.x + other.width + min_gap and
                    bx + b_width + min_gap > other.x and
                    bz < other.z + other.depth + min_gap and
                    bz + b_depth + min_gap > other.z):
                    collision = True
                    break
            
            if not collision:
                # Perlin noise for height consistency in neighborhoods
                n_val = noise.pnoise2(bx * noise_scale, bz * noise_scale, octaves=2)
                height = max(2.0, ((n_val + 1) * 5) + random.uniform(-1.0, 4.0))
                
                b = Building(bx, bz, b_width, height, b_depth, theme_colors)
                state['buildings'].append(b)

    def toggle_color():
        state['theme_index'] = (state['theme_index'] + 1) % len(THEMES)
        current_theme = THEMES[state['theme_index']]
        new_colors = current_theme['lights']
        
        for b in state['buildings']:
            b.theme_colors = new_colors
            for w in b.windows:
                w['color'] = random.choice(new_colors)
            b.cleanup()

    # Initial Generation
    generate_city()
    last_density = state['density']

    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    toggle_color()
                if event.key == pygame.K_p:
                    state['is_paused'] = not state['is_paused']
                if event.key == pygame.K_UP:
                    state['density'] = min(100, state['density'] + 10)
                if event.key == pygame.K_DOWN:
                    state['density'] = max(10, state['density'] - 10)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Ray casting is hard, let's just spawn particles in front of camera
                # or at a random building top
                if state['buildings']:
                    target = random.choice(state['buildings'])
                    tx = target.x + target.width/2
                    ty = target.height
                    tz = target.z + target.depth/2
                    
                    current_theme = THEMES[state['theme_index']]
                    for _ in range(20):
                        p_color = random.choice(current_theme['lights'])
                        state['particles'].append(Particle(tx, ty, tz, p_color))

        # 2. Update
        if abs(state['density'] - last_density) > 0.1:
            last_density = state['density']
            generate_city()

        # Optimized Flicker: Only update one building per frame
        if state['buildings']:
            # Pick a few random buildings to flicker
            for _ in range(2):
                b = random.choice(state['buildings'])
                b.flicker_window()

        state['particles'] = [p for p in state['particles'] if p.update()]
        
        # Camera Rotation
        if not state['is_paused']:
            state['cam_angle'] += state['rot_speed']
        
        # Dynamic Camera Distance based on map size
        # Updated for organic map size calculation
        map_radius = (math.sqrt(state['density']) * 4.0) / 2.0
        cam_dist = map_radius * 1.5 + 5 # Closer to the city
        
        state['cam_x'] = math.sin(state['cam_angle']) * cam_dist
        state['cam_z'] = math.cos(state['cam_angle']) * cam_dist
        
        # Elevate camera to look down (45-60 degree angle approx)
        cam_y = cam_dist * 0.5

        # 3. Draw
        current_theme = THEMES[state['theme_index']]
        glClearColor(*current_theme['bg'])
        glFogfv(GL_FOG_COLOR, current_theme['bg']) # Sync fog color with theme
        
        # Adjust fog distance based on camera
        glFogf(GL_FOG_START, cam_dist * 0.5)
        glFogf(GL_FOG_END, cam_dist * 2.5)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glLoadIdentity()
        gluLookAt(state['cam_x'], cam_y, state['cam_z'], 0, 0, 0, 0, 1, 0)

        for b in state['buildings']:
            b.draw()

        for p in state['particles']:
            p.draw()
            
        # Draw UI (2D Overlay)
        # Switch to Ortho
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        
        # Draw Text
        draw_text(20, 20, f"Density: {state['density']} (Up/Down Arrows)", font)
        draw_text(20, 50, f"Theme: {current_theme['name']} (Space)", font)
        draw_text(20, 80, "Click: Fireworks", font)
        draw_text(20, 110, "Pause Rotation: P", font)
        
        # Restore Perspective
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
