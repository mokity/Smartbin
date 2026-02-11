import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import hashlib

class FileProcessor:
    def __init__(self, config):
        self.config = config
        self.operations_log = []
    
    def process_file(self, file_path: str, category: str) -> Dict:
        source_path = Path(file_path)
        
        if not source_path.exists():
            return {
                'success': False,
                'error': '文件不存在',
                'source': str(source_path)
            }
        
        target_dir = self.config.get_target_directory() / category
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = target_dir / source_path.name
        
        # 检查文件冲突策略
        strategy = self.config.config.get('conflict_strategy', 'rename')
        if target_path.exists() and strategy == 'skip':
            return {
                'success': True,
                'source': str(source_path),
                'destination': str(target_path),
                'category': category,
                'error': '文件已存在，已跳过'
            }
        
        target_path = self._get_unique_target_path(source_path, target_dir)
        
        try:
            shutil.move(str(source_path), str(target_path))
            
            operation = {
                'timestamp': datetime.now().isoformat(),
                'operation': 'move',
                'source': str(source_path),
                'destination': str(target_path),
                'category': category,
                'file_size': source_path.stat().st_size,
                'file_hash': self._calculate_file_hash(target_path)
            }
            
            self.operations_log.append(operation)
            return {
                'success': True,
                'source': str(source_path),
                'destination': str(target_path),
                'category': category,
                'operation': operation
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': str(source_path)
            }
    
    def _get_unique_target_path(self, source_path: Path, target_dir: Path) -> Path:
        target_path = target_dir / source_path.name
        
        if not target_path.exists():
            return target_path
        
        strategy = self.config.config.get('conflict_strategy', 'rename')
        
        if strategy == 'overwrite':
            return target_path
        else:  # rename
            counter = 1
            stem = source_path.stem
            suffix = source_path.suffix
            
            while True:
                new_name = f"{stem}({counter}){suffix}"
                new_path = target_dir / new_name
                
                if not new_path.exists():
                    return new_path
                
                counter += 1
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def undo_last_operation(self) -> Optional[Dict]:
        if not self.operations_log:
            return None
        
        last_op = self.operations_log.pop()
        
        try:
            source_path = Path(last_op['destination'])
            target_path = Path(last_op['source'])
            
            if source_path.exists():
                shutil.move(str(source_path), str(target_path))
                return {
                    'success': True,
                    'operation': last_op
                }
            else:
                return {
                    'success': False,
                    'error': '源文件不存在',
                    'operation': last_op
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'operation': last_op
            }
    
    def batch_process(self, file_paths: List[str], recognizer) -> List[Dict]:
        results = []
        
        for file_path in file_paths:
            category, mime_type, status = recognizer.detect_file_type(file_path)
            
            if status == "伪装文件":
                results.append({
                    'success': False,
                    'error': f'检测到伪装文件: {mime_type}',
                    'source': file_path
                })
                continue
            
            result = self.process_file(file_path, category)
            results.append(result)
        
        return results
    
    def get_operation_history(self, limit: int = 100) -> List[Dict]:
        return self.operations_log[-limit:]
    
    def clear_history(self):
        self.operations_log.clear()