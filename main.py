from __future__ import annotations

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Определение вершин и ребер для буквы "К"
# Буква будет состоять из трех блоков:
# 1. Вертикальная палка
# 2. Верхняя наклонная
# 3. Нижняя наклонная

def create_box(origin, size):
    x, y, z = origin
    w, h, d = size
    # Вершины
    vertices = [
        (x, y, z), (x + w, y, z), (x + w, y + h, z), (x, y + h, z),           # Front
        (x, y, z + d), (x + w, y, z + d), (x + w, y + h, z + d), (x, y + h, z + d) # Back
    ]
    # Ребра (индексы вершин)
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0), # Front face
        (4, 5), (5, 6), (6, 7), (7, 4), # Back face
        (0, 4), (1, 5), (2, 6), (3, 7)  # Connecting lines
    ]
    return vertices, edges

def get_k_geometry():
    # Толщина и ширина элементов
    width = 1.0
    depth = 1.0
    height = 6.0
    
    all_vertices = []
    all_edges = []
    
    # 1. Вертикальная палка (слева)
    # Позиция: x=-2, y=-3 (центруем по вертикали)
    v1, e1 = create_box((-2.0, -3.0, -0.5), (width, height, depth))
    offset = len(all_vertices)
    all_vertices.extend(v1)
    all_edges.extend([(a + offset, b + offset) for a, b in e1])
    
    # 2. Верхняя наклонная
    # Начинается от середины палки (y=0) и идет вправо-вверх
    # Для упрощения сделаем просто прямоугольник, смещенный
    # Но чтобы было похоже на K, нужно повернуть или просто расположить ступеньками
    # Сделаем просто диагональный блок, задав вершины вручную для красоты,
    # или используем повернутый box?
    # Проще просто нарисовать box и повернуть его glRotate, но нам нужен единый массив вершин для Lab 6a.
    # Поэтому зададим координаты явно.
    
    # Верхняя нога (от (-1, 0, ...) до (2, 3, ...))
    # Просто 4 точки спереди, 4 сзади
    # Front face
    v2_front = [
        (-1.0, 0.0, -0.5), (0.0, 0.0, -0.5),  # Low end attached to stick
        (2.0, 3.0, -0.5), (1.0, 3.0, -0.5)    # High end
    ]
    # Back face
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
    
    # 3. Нижняя наклонная
    # От (-1, 0) до (2, -3)
    v3_front = [
        (-1.0, 0.0, -0.5), (0.0, 0.0, -0.5),   # Top end attached to stick
        (2.0, -3.0, -0.5), (1.0, -3.0, -0.5)   # Low end
    ]
    v3_back = [(x, y, z + 1.0) for x, y, z in v3_front]
    v3 = v3_front + v3_back
    # Edges same structure as box
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
        pygame.display.set_caption("Lab 6: 3D Visualization & Transformations (OpenGL)")
        
        self.vertices, self.edges = get_k_geometry()
        
        # Transformation state
        self.scale = [1.0, 1.0, 1.0]
        self.translation = [0.0, 0.0, -10.0] # Initial zoom out
        self.rotation = [0.0, 0.0, 0.0] # x, y, z axes
        
        # Modes
        self.view_mode = 0 # 0: Perspective, 1: Oxy, 2: Oxz, 3: Oyz
        self.transform_mode = 0 # 0: Translate, 1: Rotate, 2: Scale
        
        # Colors
        self.bg_color = (0.1, 0.1, 0.1, 1.0)
        self.line_color = (0.0, 1.0, 0.0)
        
        # Font
        self.font = pygame.font.SysFont('Arial', 16)
        
        glEnable(GL_DEPTH_TEST)

    def draw_text(self, x, y, text):
        # Pygame text render requires switching from OpenGL to 2D
        # This is complex in pure pygame+opengl loop.
        # Simple hack: Render text to surface, then texture quad. 
        # Or just print to console?
        # Requirement: "display transformation matrix". 
        # Let's print to console for simplicity OR try to render titlebar?
        # Actually, using pygame.display.set_caption is easy for status.
        # But for matrix, we need more space.
        # We will assume "Console Output" for matrix is acceptable or draw simple lines.
        # Let's try to stick to console output for the matrix to keep code clean, 
        # or just print it periodically.
        pass

    def get_matrix_string(self):
        # Retrieve current modelview matrix
        m = glGetFloatv(GL_MODELVIEW_MATRIX)
        # m is 4x4 column-major
        lines = []
        for i in range(4):
            row = [f"{m[j][i]:.2f}" for j in range(4)]
            lines.append(" | ".join(row))
        return "\n".join(lines)

    def draw_axes(self, length=2.0):
        glBegin(GL_LINES)
        # X - Red
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0); glVertex3f(length, 0.0, 0.0)
        # Y - Green
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, length, 0.0)
        # Z - Blue
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
            # Orthographic
            zoom = 10.0
            if aspect >= 1.0:
                glOrtho(-zoom * aspect, zoom * aspect, -zoom, zoom, 0.1, 50.0)
            else:
                glOrtho(-zoom, zoom, -zoom / aspect, zoom / aspect, 0.1, 50.0)
                
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_camera_view(self):
        # For projection views, we need to set lookAt
        # 1: Oxy (Front) -> Look from +Z
        # 2: Oxz (Top) -> Look from +Y
        # 3: Oyz (Side) -> Look from +X
        
        if self.view_mode == 0:
            # Free view - transformations applied to object, camera fixed (or object moves)
            # In this logic: Object transformations are applied. Camera is at origin (moved back by translation)
            glTranslatef(self.translation[0], self.translation[1], self.translation[2])
            glRotatef(self.rotation[0], 1, 0, 0)
            glRotatef(self.rotation[1], 0, 1, 0)
            glRotatef(self.rotation[2], 0, 0, 1)
            glScalef(self.scale[0], self.scale[1], self.scale[2])
            
        elif self.view_mode == 1: # Oxy (Front view, looking along Z)
            gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)
            
        elif self.view_mode == 2: # Oxz (Top view, looking along Y)
            gluLookAt(0, 10, 0, 0, 0, 0, 0, 0, -1) # Up vector is -Z to match standard topdown
            
        elif self.view_mode == 3: # Oyz (Side view, looking along X)
            gluLookAt(10, 0, 0, 0, 0, 0, 0, 1, 0)
            
        # For ortho views, we usually want to see the object transformed OR just the projection?
        # Lab 6c says "construct 3 orthographic projections".
        # Usually this implies seeing the OBJECT (transformed) from different sides.
        # So we should apply object transforms even in ortho modes?
        # Let's apply them.
        if self.view_mode != 0:
             # Apply object transforms "in place"
             glTranslatef(self.translation[0], self.translation[1], 0) # Z translation irrelevant for ortho? No, clipping.
             # Actually, keep translation fully to keep it in frustum
             # But for pure projection planes, we might ignore Z translation visually?
             # Let's just apply full transform.
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

            # Continuous input
            keys = pygame.key.get_pressed()
            speed = 0.1
            rot_speed = 2.0
            scale_speed = 0.05
            
            if self.transform_mode == 0: # Translate
                if keys[K_LEFT]: self.translation[0] -= speed
                if keys[K_RIGHT]: self.translation[0] += speed
                if keys[K_UP]: self.translation[1] += speed
                if keys[K_DOWN]: self.translation[1] -= speed
                if keys[K_PAGEUP]: self.translation[2] += speed
                if keys[K_PAGEDOWN]: self.translation[2] -= speed
                
            elif self.transform_mode == 1: # Rotate
                if keys[K_LEFT]: self.rotation[1] -= rot_speed
                if keys[K_RIGHT]: self.rotation[1] += rot_speed
                if keys[K_UP]: self.rotation[0] -= rot_speed
                if keys[K_DOWN]: self.rotation[0] += rot_speed
                if keys[K_PAGEUP]: self.rotation[2] -= rot_speed
                if keys[K_PAGEDOWN]: self.rotation[2] += rot_speed
                
            elif self.transform_mode == 2: # Scale
                if keys[K_LEFT]: self.scale[0] -= scale_speed
                if keys[K_RIGHT]: self.scale[0] += scale_speed
                if keys[K_UP]: self.scale[1] += scale_speed
                if keys[K_DOWN]: self.scale[1] -= scale_speed
                if keys[K_PAGEUP]: self.scale[2] += scale_speed
                if keys[K_PAGEDOWN]: self.scale[2] -= scale_speed

            # Drawing
            glClearColor(*self.bg_color)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            self.set_projection()
            self.set_camera_view()
            
            # Draw Axes (Fixed at local origin of object if we want to see object rotation axes, 
            # OR global axes? 
            # If we draw axes AFTER transform, they move with object.
            # If BEFORE, they are global world axes.
            # Let's draw Global Axes first (undoing transform for them? No, just draw before model transform if we used push/pop)
            # But we applied transform in set_camera_view.
            
            # Let's restructure:
            # 1. Identity
            # 2. Camera View (LookAt)
            # 3. Draw Global Axes
            # 4. Apply Object Model Transform
            # 5. Draw Object
            
            # Refactoring render logic inline:
            glLoadIdentity()
            # Handle Camera depending on View Mode
            if self.view_mode == 0:
                # Perspective: Camera is static, Object moves. 
                # OR Camera moves to simulate object movement?
                # Let's say Camera is at 0,0,0 (looking -Z). 
                # Objects are placed at self.translation.
                pass 
                # Actually set_camera_view logic was mixing Model and View.
            
            # Correct Separation:
            # VIEW MATRIX
            if self.view_mode == 0:
                # Normal 3D view
                # We can imagine camera is at origin, but we push object back.
                # Or use gluLookAt to sit at (0,0,10)
                pass # Identity is fine if object is at z=-10
            elif self.view_mode == 1: gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)
            elif self.view_mode == 2: gluLookAt(0, 10, 0, 0, 0, 0, 0, 0, -1)
            elif self.view_mode == 3: gluLookAt(10, 0, 0, 0, 0, 0, 0, 1, 0)

            # Draw Static Grid/Axes (World)
            glPushMatrix()
            # If Perspective, we might need to move grid slightly back to be visible if camera is at 0?
            # If view_mode 0, our object translation handles position.
            # Let's draw axes at 0,0,0.
            if self.view_mode == 0: glTranslatef(0, 0, -10) # Move world origin to visible range
            self.draw_axes(length=5.0)
            glPopMatrix()
            
            # MODEL MATRIX (Object Transform)
            if self.view_mode == 0: glTranslatef(0, 0, -10) # Base position
            
            glTranslatef(self.translation[0], self.translation[1], self.translation[2])
            glRotatef(self.rotation[0], 1, 0, 0)
            glRotatef(self.rotation[1], 0, 1, 0)
            glRotatef(self.rotation[2], 0, 0, 1)
            glScalef(self.scale[0], self.scale[1], self.scale[2])
            
            # Draw Object (Letter K)
            glBegin(GL_LINES)
            glColor3fv(self.line_color)
            for edge in self.edges:
                for vertex in edge:
                    glVertex3fv(self.vertices[vertex])
            glEnd()
            
            # Requirement: Output Matrix
            # Only periodically to not spam
            if pygame.time.get_ticks() % 1000 < 20: 
                # print("\nCurrent ModelView Matrix:")
                # print(self.get_matrix_string())
                pass

            # Display Status in Title
            status = f"Mode: {modes[self.transform_mode]} | View: {self.view_mode} | T: {self.translation[0]:.1f},{self.translation[1]:.1f},{self.translation[2]:.1f} R: {self.rotation[0]:.0f},{self.rotation[1]:.0f},{self.rotation[2]:.0f} S: {self.scale[0]:.1f}"
            pygame.display.set_caption(f"Lab 6 - {status}")

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    app = App()
    app.run()

