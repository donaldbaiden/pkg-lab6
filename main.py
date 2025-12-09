from __future__ import annotations

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def create_box(origin, size):
    x, y, z = origin
    w, h, d = size
    vertices = [
        (x, y, z), (x + w, y, z), (x + w, y + h, z), (x, y + h, z),        
        (x, y, z + d), (x + w, y, z + d), (x + w, y + h, z + d), (x, y + h, z + d) 
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4), 
        (0, 4), (1, 5), (2, 6), (3, 7) 
    ]
    return vertices, edges

def get_k_geometry():
    width = 1.0
    depth = 1.0
    height = 6.0
    
    all_vertices = []
    all_edges = []
    
    v1, e1 = create_box((-2.0, -3.0, -0.5), (width, height, depth))
    offset = len(all_vertices)
    all_vertices.extend(v1)
    all_edges.extend([(a + offset, b + offset) for a, b in e1])
    
    
    v2_front = [
        (-1.0, 0.0, -0.5), (0.0, 0.0, -0.5),  
        (2.0, 3.0, -0.5), (1.0, 3.0, -0.5)    
    ]
    v2_back = [(x, y, z + 1.0) for x, y, z in v2_front]
    v2 = v2_front + v2_back
    e2 = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    
    offset = len(all_vertices)
    all_vertices.extend(v2)
    all_edges.extend([(a + offset, b + offset) for a, b in e2])
    
    v3_front = [
        (-1.0, 0.0, -0.5), (0.0, 0.0, -0.5),  
        (2.0, -3.0, -0.5), (1.0, -3.0, -0.5)   
    ]
    v3_back = [(x, y, z + 1.0) for x, y, z in v3_front]
    v3 = v3_front + v3_back
    e3 = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    
    offset = len(all_vertices)
    all_vertices.extend(v3)
    all_edges.extend([(a + offset, b + offset) for a, b in e3])
    
    return np.array(all_vertices, dtype=np.float32), all_edges

class App:
    def __init__(self):
        pygame.init()
        self.display = (1000, 700)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Lab 6")
        
        self.vertices, self.edges = get_k_geometry()
        
        self.scale = [1.0, 1.0, 1.0]
        self.translation = [0.0, 0.0, -10.0]
        self.rotation = [0.0, 0.0, 0.0]
        
        self.view_mode = 0
        self.transform_mode = 0
        
        self.bg_color = (0.1, 0.1, 0.1, 1.0)
        self.line_color = (0.0, 1.0, 0.0)
        
        self.font = pygame.font.SysFont('Arial', 16)
        
        glEnable(GL_DEPTH_TEST)

    def draw_text(self, x, y, text):
        pass

    def get_matrix_string(self):
        m = glGetFloatv(GL_MODELVIEW_MATRIX)
        lines = []
        for i in range(4):
            row = [f"{m[j][i]:.2f}" for j in range(4)]
            lines.append(" | ".join(row))
        return "\n".join(lines)

    def draw_axes(self, length=2.0):
        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0); glVertex3f(length, 0.0, 0.0)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, length, 0.0)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, 0.0, length)
        glEnd()

    def set_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        aspect = self.display[0] / self.display[1]
        
        if self.view_mode == 0:
            gluPerspective(45, aspect, 0.1, 50.0)
        else:
            zoom = 10.0
            if aspect >= 1.0:
                glOrtho(-zoom * aspect, zoom * aspect, -zoom, zoom, 0.1, 50.0)
            else:
                glOrtho(-zoom, zoom, -zoom / aspect, zoom / aspect, 0.1, 50.0)
                
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_camera_view(self):
        if self.view_mode == 0:
            glTranslatef(self.translation[0], self.translation[1], self.translation[2])
            glRotatef(self.rotation[0], 1, 0, 0)
            glRotatef(self.rotation[1], 0, 1, 0)
            glRotatef(self.rotation[2], 0, 0, 1)
            glScalef(self.scale[0], self.scale[1], self.scale[2])
            
        elif self.view_mode == 1:
            gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)
            
        elif self.view_mode == 2:
            gluLookAt(0, 10, 0, 0, 0, 0, 0, 0, -1)
            
        elif self.view_mode == 3:
            gluLookAt(10, 0, 0, 0, 0, 0, 0, 1, 0)
            
        if self.view_mode != 0:
             glTranslatef(self.translation[0], self.translation[1], 0)
             glRotatef(self.rotation[0], 1, 0, 0)
             glRotatef(self.rotation[1], 0, 1, 0)
             glRotatef(self.rotation[2], 0, 0, 1)
             glScalef(self.scale[0], self.scale[1], self.scale[2])

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        print("Controls:")
        print("1: Perspective View")
        print("2: Oxy Projection (Front)")
        print("3: Oxz Projection (Top)")
        print("4: Oyz Projection (Side)")
        print("TAB: Switch Transform Mode (Current: Translate)")
        print("Arrows/PgUp/PgDn: Apply Transformation")
        print("R: Reset")
        print("-" * 20)

        modes = ["Translate", "Rotate", "Scale"]

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_1: self.view_mode = 0
                    if event.key == K_2: self.view_mode = 1
                    if event.key == K_3: self.view_mode = 2
                    if event.key == K_4: self.view_mode = 3
                    
                    if event.key == K_TAB:
                        self.transform_mode = (self.transform_mode + 1) % 3
                        print(f"Mode: {modes[self.transform_mode]}")
                        
                    if event.key == K_r:
                        self.scale = [1.0, 1.0, 1.0]
                        self.translation = [0.0, 0.0, -10.0]
                        self.rotation = [0.0, 0.0, 0.0]

            keys = pygame.key.get_pressed()
            speed = 0.1
            rot_speed = 2.0
            scale_speed = 0.05
            
            if self.transform_mode == 0:
                if keys[K_LEFT]: self.translation[0] -= speed
                if keys[K_RIGHT]: self.translation[0] += speed
                if keys[K_UP]: self.translation[1] += speed
                if keys[K_DOWN]: self.translation[1] -= speed
                if keys[K_PAGEUP]: self.translation[2] += speed
                if keys[K_PAGEDOWN]: self.translation[2] -= speed
                
            elif self.transform_mode == 1:
                if keys[K_LEFT]: self.rotation[1] -= rot_speed
                if keys[K_RIGHT]: self.rotation[1] += rot_speed
                if keys[K_UP]: self.rotation[0] -= rot_speed
                if keys[K_DOWN]: self.rotation[0] += rot_speed
                if keys[K_PAGEUP]: self.rotation[2] -= rot_speed
                if keys[K_PAGEDOWN]: self.rotation[2] += rot_speed
                
            elif self.transform_mode == 2:
                if keys[K_LEFT]: self.scale[0] -= scale_speed
                if keys[K_RIGHT]: self.scale[0] += scale_speed
                if keys[K_UP]: self.scale[1] += scale_speed
                if keys[K_DOWN]: self.scale[1] -= scale_speed
                if keys[K_PAGEUP]: self.scale[2] += scale_speed
                if keys[K_PAGEDOWN]: self.scale[2] -= scale_speed

            glClearColor(*self.bg_color)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            self.set_projection()
            self.set_camera_view()
            
            glLoadIdentity()
            if self.view_mode == 0:
                pass
            elif self.view_mode == 1: gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)
            elif self.view_mode == 2: gluLookAt(0, 10, 0, 0, 0, 0, 0, 0, -1)
            elif self.view_mode == 3: gluLookAt(10, 0, 0, 0, 0, 0, 0, 1, 0)

            glPushMatrix()
            if self.view_mode == 0: glTranslatef(0, 0, -10)
            self.draw_axes(length=5.0)
            glPopMatrix()
            
            if self.view_mode == 0: glTranslatef(0, 0, -10)
            
            glTranslatef(self.translation[0], self.translation[1], self.translation[2])
            glRotatef(self.rotation[0], 1, 0, 0)
            glRotatef(self.rotation[1], 0, 1, 0)
            glRotatef(self.rotation[2], 0, 0, 1)
            glScalef(self.scale[0], self.scale[1], self.scale[2])
            
            glBegin(GL_LINES)
            glColor3fv(self.line_color)
            for edge in self.edges:
                for vertex in edge:
                    glVertex3fv(self.vertices[vertex])
            glEnd()
            
            if pygame.time.get_ticks() % 1000 < 20: 
                pass

            status = f"Mode: {modes[self.transform_mode]} | View: {self.view_mode} | T: {self.translation[0]:.1f},{self.translation[1]:.1f},{self.translation[2]:.1f} R: {self.rotation[0]:.0f},{self.rotation[1]:.0f},{self.rotation[2]:.0f} S: {self.scale[0]:.1f}"
            pygame.display.set_caption(f"Lab 6 - {status}")

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    app = App()
    app.run()

