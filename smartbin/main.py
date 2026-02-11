import sys
import os

from smartbin.config import Config
from smartbin.file_recognizer import FileRecognizer
from smartbin.file_processor import FileProcessor
from smartbin.gui import SmartBinGUI

def main():
    print("正在启动 SmartBin 智能归档箱...")
    
    config = Config()
    recognizer = FileRecognizer()
    processor = FileProcessor(config)
    
    print(f"目标目录: {config.get_target_directory()}")
    print("初始化文件识别引擎...")
    print("初始化文件处理器...")
    
    gui = SmartBinGUI(config, processor, recognizer)
    
    print("SmartBin 已启动！")
    print("将文件拖拽到悬浮图标上进行自动分类整理。")
    
    return gui.run()

if __name__ == "__main__":
    sys.exit(main())