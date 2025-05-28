import pygame
import random
import math
from path import Path
from tower import BasicTower, CannonTower, ArcherTower
from enemy import Enemy
from resources import ResourceManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("石塔防御战")
        
        self.res = ResourceManager()
        self._load_resources()
        
        self.path = Path()
        self.towers = []
        self.enemies = []
        self.wave = 1
        self.money = 1000
        self.lives = 10
        self.selected_tower_type = None
        self.tower_costs = {
            "basic": 100,
            "cannon": 200,
            "archer": 150
        }
        self.tower_names = {
            "basic": "基础塔",
            "cannon": "炮塔",
            "archer": "箭塔"
        }
        self.grid_size = 40
        self.buildable_grid = self._init_buildable_grid()
        self.clock = pygame.time.Clock()
        self.paused = False  # 新增暂停状态
        
    def _load_resources(self):
        # 背景图
        self.res.load_image('assets/background.png', 'background')
        
        # 防御塔图片
        self.res.load_image('assets/towers/basic.png', 'basic_tower', (50,70))
        self.res.load_image('assets/towers/cannon.png', 'cannon_tower', (60,80))
        self.res.load_image('assets/towers/archer.png', 'archer_tower', (55,75))
        
        # 敌人图片
        self.res.load_image('assets/enemies/bird.png', 'enemy1', (35,35))
        self.res.load_image('assets/enemies/monster.png', 'enemy2', (45,45))
        
        # 音频
        self.res.load_music('assets/audio/background.mp3')
        self.res.load_sound('assets/audio/build.wav', 'build')
        self.res.load_sound('assets/audio/explosion.wav', 'explode')

    def _init_buildable_grid(self):
        grid = []
        path_margin = self.path.width // 2 + 15
        
        for x in range(0, 800, self.grid_size):
            for y in range(0, 600, self.grid_size):
                center = (x + self.grid_size//2, y + self.grid_size//2)
                
                is_valid = True
                for i in range(len(self.path.points)-1):
                    p1, p2 = self.path.points[i], self.path.points[i+1]
                    line_vec = (p2[0]-p1[0], p2[1]-p1[1])
                    point_vec = (center[0]-p1[0], center[1]-p1[1])
                    cross = abs(line_vec[0]*point_vec[1] - line_vec[1]*point_vec[0])
                    line_len = math.sqrt(line_vec[0]**2 + line_vec[1]**2)
                    if cross/line_len < path_margin:
                        is_valid = False
                        break
                
                if is_valid:
                    grid.append(pygame.Rect(x, y, self.grid_size, self.grid_size))
        return grid

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # 塔选择按钮
                    if 700 <= mouse_x <= 790 and 100 <= mouse_y <= 130:
                        self.selected_tower_type = "basic"
                    elif 700 <= mouse_x <= 790 and 140 <= mouse_y <= 170:
                        self.selected_tower_type = "cannon"
                    elif 700 <= mouse_x <= 790 and 180 <= mouse_y <= 210:
                        self.selected_tower_type = "archer"
                    
                    # 建造逻辑
                    elif self.selected_tower_type:
                        grid_x = (mouse_x // self.grid_size) * self.grid_size
                        grid_y = (mouse_y // self.grid_size) * self.grid_size
                        grid_rect = pygame.Rect(grid_x, grid_y, self.grid_size, self.grid_size)
                        
                        if any(grid_rect.colliderect(area) for area in self.buildable_grid):
                            cost = self.tower_costs[self.selected_tower_type]
                            if self.money >= cost:
                                if 'build' in self.res.sounds:
                                    self.res.sounds['build'].play()
                                
                                center_x = grid_x + self.grid_size // 2
                                center_y = grid_y + self.grid_size // 2
                                if self.selected_tower_type == "basic":
                                    tower = BasicTower(center_x, center_y)
                                elif self.selected_tower_type == "cannon":
                                    tower = CannonTower(center_x, center_y)
                                elif self.selected_tower_type == "archer":
                                    tower = ArcherTower(center_x, center_y)
                                
                                # 鼠标悬停时显示攻击范围
                                tower.show_range = False
                                self.towers.append(tower)
                                self.money -= cost
                                self.selected_tower_type = None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.selected_tower_type = "basic"
                elif event.key == pygame.K_2:
                    self.selected_tower_type = "cannon"
                elif event.key == pygame.K_3:
                    self.selected_tower_type = "archer"
                elif event.key == pygame.K_SPACE:  # 空格键暂停/继续
                    self.paused = not self.paused
                    
            # 鼠标悬停时显示防御塔攻击范围
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for tower in self.towers:
                    if math.sqrt((tower.x - mouse_x)**2 + (tower.y - mouse_y)**2) < 30:
                        tower.show_range = True
                    else:
                        tower.show_range = False
                        
        return True

    def update(self):
        if self.paused:
            return
            
        # 波次生成
        if len(self.enemies) == 0:
            self.spawn_wave()
        
        # 敌人更新
        for enemy in self.enemies[:]:
            if not enemy.update(self):
                self.enemies.remove(enemy)
        
        # 防御塔攻击和子弹更新
        for tower in self.towers:
            target = tower.attack(self.enemies)
            if target:
                if 'explode' in self.res.sounds:
                    self.res.sounds['explode'].play()
            
            # 更新子弹并检查是否击中敌人
            if killed_enemy := tower.update_projectiles(self.enemies):
                self.money += 20

    def spawn_wave(self):
        enemy_count = min(5 + self.wave * 2, 20)
        for _ in range(enemy_count):
            enemy_type = 'enemy1' if random.random() < 0.7 else 'enemy2'
            self.enemies.append(Enemy(self.path, enemy_type))
        self.wave += 1

    def draw(self):
        # 绘制背景
        if 'background' in self.res.images:
            self.screen.blit(self.res.images['background'], (0, 0))
        else:
            self.screen.fill((100, 200, 100))
        
        # 绘制路径
        self.path.draw(self.screen)
        
        # 绘制可建造网格
        for area in self.buildable_grid:
            pygame.draw.rect(self.screen, (100, 255, 100, 30), area, 1)
        
        # 绘制防御塔
        for tower in self.towers:
            tower.draw(self.screen, self.res)
        
        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(self.screen, self.res)
        
        # 绘制UI
        texts = [
            (f"波次: {self.wave}", (10, 10)),
            (f"金钱: ${self.money}", (10, 50)),
            (f"生命: {self.lives}", (10, 90))
        ]
        for text, pos in texts:
            text_surface = self.res.font.render(text, True, (0, 0, 0))
            self.screen.blit(text_surface, pos)
        
        # 塔选择按钮
        buttons = [
            ((0, 100, 200), "基础塔(1)", (700, 100)),
            ((200, 100, 50), "炮塔(2)", (700, 140)),
            ((50, 200, 50), "箭塔(3)", (700, 180))
        ]
        for color, text, pos in buttons:
            pygame.draw.rect(self.screen, color, (*pos, 90, 30))
            text_surface = self.res.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (pos[0]+5, pos[1]+5))
        
        # 显示当前选择的防御塔名称
        if self.selected_tower_type:
            try:
                text = f"已选择: {self.tower_names[self.selected_tower_type]}"
                text_surface = self.res.font.render(text, True, (255,0,0))  # 红色文字
            
                # 绘制半透明背景框
                bg_rect = pygame.Rect(650, 220, 140, 30)
                bg_surface = pygame.Surface((140,30), pygame.SRCALPHA)
                bg_surface.fill((255,255,255,128))  # 半透明白色
                self.screen.blit(bg_surface, (650,220))
            
                self.screen.blit(text_surface, (650, 220))
            except Exception as e:
                print(f"文字渲染失败: {e}")
                
        # 显示暂停状态
        if self.paused:
            pause_text = self.res.font.render("游戏暂停(按空格键继续)", True, (255, 0, 0))
            text_rect = pause_text.get_rect(center=(self.screen.get_width()//2, 30))
            self.screen.blit(pause_text, text_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running and self.lives > 0:
            running = self.handle_events()
            if not self.paused:
                self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()