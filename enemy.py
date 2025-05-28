# 文档3: enemy.py
import random
import pygame

class Enemy:
    def __init__(self, path, enemy_type):
        self.path = path
        self.path_index = 0
        self.x, self.y = path.points[0]
        self.speed = random.uniform(1.0, 3.0)
        self.health = 100
        self.max_health = 100
        self.type = enemy_type  # 'enemy1'或'enemy2'
        
    def update(self, game):
        # 移动逻辑
        if self.path_index < len(self.path.points):
            target = self.path.points[self.path_index]
            dx, dy = target[0]-self.x, target[1]-self.y
            dist = (dx**2 + dy**2)**0.5
            
            if dist < 5:
                self.path_index += 1
            else:
                self.x += dx/dist * self.speed
                self.y += dy/dist * self.speed
        
        # 死亡检测
        if self.health <= 0:
            return False
        
        # 终点检测
        if self.path_index >= len(self.path.points):
            game.lives -= 1
            return False
            
        return True
    
    def take_damage(self, amount):
        self.health -= amount
        return self if self.health <= 0 else None
    
    def draw(self, surface, res_manager):
        if self.type in res_manager.images:
            img = res_manager.images[self.type]
            rect = img.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(img, rect)
        
        # 血条
        health_width = 30 * (self.health / self.max_health)
        pygame.draw.rect(surface, (255,0,0), (self.x-15, self.y-25, 30, 5))
        pygame.draw.rect(surface, (0,255,0), (self.x-15, self.y-25, health_width, 5))