import pygame

class Path:
    def __init__(self):
        # S形路径点
        self.points = [
            (0, 300), (200, 300), (200, 150),
            (400, 150), (400, 450), (600, 450),
            (600, 300), (800, 300)
        ]
        self.width = 40
        
    def draw(self, surface):
        for i in range(len(self.points)-1):
            pygame.draw.line(surface, (150, 150, 150), 
                           self.points[i], self.points[i+1], 
                           self.width)