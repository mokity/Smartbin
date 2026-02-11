import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".smartbin"
        self.config_file = self.config_dir / "config.json"
        self.log_file = self.config_dir / "operations.log"
        self.db_file = self.config_dir / "smartbin.db"
        
        self.default_config = {
            "target_directory": str(Path.home() / "Desktop"),
            "default_categories": {
                "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
                "文档": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
                "视频": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
                "音频": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
                "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "代码": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h"],
                "安装包": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"],
                "其他": []
            },
            "custom_rules": [],
            "conflict_strategy": "rename",
            "enable_content_analysis": False,
            "hot_zones": {
                "enabled": False,
                "zones": []
            },
            "ui_settings": {
                "transparency": 0.9,
                "icon_size": 64,
                "position": {"x": 100, "y": 100}
            }
        }
        
        self.config = {}
        self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
                self.config = self.default_config.copy()
        else:
            self.config = self.default_config.copy()
            self.save_config()
        
        # 不再提前创建所有文件夹，只在需要时创建
    
    def save_config(self):
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def ensure_directories(self):
        target_dir = Path(self.config["target_directory"])
        for category in self.config["default_categories"].keys():
            category_dir = target_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
    
    def get_category_for_extension(self, extension):
        extension = extension.lower()
        for category, extensions in self.config["default_categories"].items():
            if extension in extensions:
                return category
        return "其他"
    
    def add_custom_rule(self, rule):
        self.config["custom_rules"].append(rule)
        self.save_config()
    
    def get_target_directory(self):
        return Path(self.config["target_directory"])