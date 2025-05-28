import pygame
import os
import random

class ResourceManager:
    def __init__(self):
        pygame.init()
        self.images = {}
        self.sounds = {}
        self.music = None
        self.font = pygame.font.SysFont('SimHei', 24)  # 使用支持中文的字体
        
    def load_image(self, path, name=None, scale=None):
        try:
            image = pygame.image.load(path).convert_alpha()
        
            # 特殊处理背景图
            if name == 'background':
                # 获取当前屏幕尺寸
                display_info = pygame.display.Info()
                target_size = (display_info.current_w, display_info.current_h)
            
                # 等比缩放填充
                img_ratio = image.get_width() / image.get_height()
                screen_ratio = target_size[0] / target_size[1]
            
                if img_ratio > screen_ratio:  # 图片更宽
                    new_height = target_size[1]
                    new_width = int(image.get_width() * (new_height/image.get_height()))
                else:  # 图片更高
                    new_width = target_size[0]
                    new_height = int(image.get_height() * (new_width/image.get_width()))
                
                # 居中裁剪
                image = pygame.transform.smoothscale(image, (new_width, new_height))
                crop_x = (new_width - target_size[0]) // 2
                crop_y = (new_height - target_size[1]) // 2
                image = image.subsurface((crop_x, crop_y, target_size[0], target_size[1]))
        
            elif scale:  # 其他图片的正常缩放
                image = pygame.transform.smoothscale(image, scale)
            
            key = name if name else os.path.basename(path)
            self.images[key] = image
            return image
        
        except Exception as e:
            print(f"图片加载失败 {path}: {e}")
            # 生成与描述完全一致的暖黄替代背景
            if name == 'background':
                surf = pygame.Surface((1280, 720))
                surf.fill((255, 240, 200))  # 精确的暖黄色
                return surf
            return self._create_placeholder(scale if scale else (50, 50))
    
    def _create_placeholder(self, size):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        color = (random.randint(50,200), random.randint(50,200), random.randint(50,200))
        pygame.draw.rect(surf, color, (0, 0, *size))
        return surf
    
    def load_music(self, path):
        try:
            pygame.mixer.music.load(path)
            self.music = path
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            return True
        except Exception as e:
            print(f"音乐加载失败 {path}: {e}")
            return False
    
    def load_sound(self, path, name=None):
        try:
            sound = pygame.mixer.Sound(path)
            key = name if name else os.path.basename(path)
            self.sounds[key] = sound
            return sound
        except Exception as e:
            print(f"音效加载失败 {path}: {e}")
            return None