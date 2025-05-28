import pygame
import math

class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y, speed, damage, color, radius):
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.damage = damage
        self.color = color
        self.radius = radius
        self.active = True
        
        # 计算方向向量
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.sqrt(dx**2 + dy**2)
        self.vx = dx / dist * speed
        self.vy = dy / dist * speed
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        # 检查是否到达目标位置
        dist = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
        if dist < 5:
            self.active = False
            
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Tower:
    def __init__(self, x, y, image_key):
        self.x = x
        self.y = y
        self.image_key = image_key
        self.range = 150
        self.damage = 10
        self.cooldown = 0
        self.cooldown_max = 30
        self.width = 40  # 网格宽度
        self.height = 40 # 网格高度（塔身较高）
        self.rect = pygame.Rect(x - self.width//2, y - self.height//2, 
                               self.width, self.height)
        self.color = (0, 100, 200)  # 默认蓝色
        self.projectiles = []
        self.show_range = False  # 默认不显示攻击范围
        
    def attack(self, enemies):
        if self.cooldown <= 0:
            for enemy in enemies[:]:
                dist = math.sqrt((self.x-enemy.x)**2 + (self.y-enemy.y)**2)
                if dist <= self.range:
                    # 创建子弹
                    self.projectiles.append(
                        Projectile(self.x, self.y, enemy.x, enemy.y, 
                                 self.get_projectile_speed(), self.damage,
                                 self.get_projectile_color(), self.get_projectile_radius())
                    )
                    
                    self.cooldown = self.cooldown_max
                    return enemy  # 返回目标敌人，但不立即造成伤害
        else:
            self.cooldown -= 1
        return None
    
    def update_projectiles(self, enemies):
        killed_enemy = None
        for proj in self.projectiles[:]:
            if proj.active:
                proj.update()
                
                # 检查是否击中敌人
                for enemy in enemies:
                    dist = math.sqrt((proj.x-enemy.x)**2 + (proj.y-enemy.y)**2)
                    if dist < 20:  # 击中判定距离
                        killed = enemy.take_damage(proj.damage)
                        if killed:
                            killed_enemy = killed
                        proj.active = False
                        break
            else:
                self.projectiles.remove(proj)
        return killed_enemy
    
    def get_projectile_speed(self):
        return 5
    
    def get_projectile_color(self):
        return self.color
    
    def get_projectile_radius(self):
        return 5
        
    def draw(self, surface, res_manager):
        """新增图片缩放和定位逻辑"""
        if self.image_key in res_manager.images:
            img = res_manager.images[self.image_key]
            # 等比例缩放至网格尺寸
            scaled_img = pygame.transform.scale(
                img, 
                (int(self.width * 0.9), int(self.height * 0.9))  # 保留10%边距
            )
            rect = scaled_img.get_rect(center=(self.x, self.y))
            surface.blit(scaled_img, rect)
        
        # 绘制攻击范围（仅在show_range为True时显示）
        if self.show_range:
            range_surface = pygame.Surface((self.range*2, self.range*2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (*self.color, 50), (self.range, self.range), self.range)
            surface.blit(range_surface, (self.x-self.range, self.y-self.range))
        
        # 绘制子弹
        for proj in self.projectiles:
            proj.draw(surface)

class BasicTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, "basic_tower")
        self.color = (0, 100, 200)  # 蓝色
        self.damage = 10
        self.range = 150
        
    def get_projectile_color(self):
        return (0, 150, 255)  # 亮蓝色
        
    def get_projectile_radius(self):
        return 4

class CannonTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, "cannon_tower")
        self.color = (200, 100, 50)  # 橙色
        self.damage = 20
        self.range = 200
        
    def get_projectile_speed(self):
        return 4
        
    def get_projectile_color(self):
        return (255, 100, 0)  # 亮橙色
        
    def get_projectile_radius(self):
        return 6

class ArcherTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, "archer_tower")
        self.color = (50, 200, 50)  # 绿色
        self.damage = 15
        self.range = 180
        self.cooldown_max = 20
        
    def get_projectile_speed(self):
        return 7
        
    def get_projectile_color(self):
        return (100, 255, 100)  # 亮绿色
        
    def get_projectile_radius(self):
        return 3