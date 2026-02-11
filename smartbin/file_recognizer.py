import os
from pathlib import Path
from typing import Dict, Optional, Tuple

class FileRecognizer:
    def __init__(self):
        self.magic_numbers = {
            b'\xFF\xD8\xFF': 'image/jpeg',
            b'\x89PNG\r\n\x1A\n': 'image/png',
            b'GIF87a': 'image/gif',
            b'GIF89a': 'image/gif',
            b'BM': 'image/bmp',
            b'RIFF': 'video/webp',
            b'%PDF': 'application/pdf',
            b'PK\x03\x04': 'application/zip',
            b'PK\x05\x06': 'application/zip',
            b'PK\x07\x08': 'application/zip',
            b'Rar!': 'application/x-rar-compressed',
            b'\x1f\x8b': 'application/gzip',
            b'7z\xBC\xAF\x27\x1C': 'application/x-7z-compressed',
            b'\x25\x21\x50\x53\x2D\x41\x44\x4F\x42\x45': 'application/postscript',
            b'\x38\x42\x50\x53': 'image/vnd.adobe.photoshop',
            b'II*\x00': 'image/tiff',
            b'MM\x00*': 'image/tiff',
            b'\x00\x00\x01\x00': 'application/x-msdownload',
            b'MZ': 'application/x-msdownload',
            b'\x7fELF': 'application/x-executable',
            b'\xCA\xFE\xBA\xBE': 'application/x-mach-binary',
            b'\xFE\xED\xFA': 'application/x-mach-binary',
            b'\xCE\xFA\xED\xFE': 'application/x-mach-binary',
            b'\x4D\x5A': 'application/x-dosexec',
            b'ID3': 'audio/mpeg',
            b'\xFF\xFB': 'audio/mpeg',
            b'\xFF\xFA': 'audio/mpeg',
            b'\xFF\xF3': 'audio/mpeg',
            b'\xFF\xF2': 'audio/mpeg',
            b'OggS': 'audio/ogg',
            b'fLaC': 'audio/flac',
            b'RIFF': 'audio/wav',
            b'\x1A\x45\xDF\xA3': 'video/webm',
            b'\x00\x00\x00\x18ftypmp42': 'video/mp4',
            b'\x00\x00\x00\x1Cftypisom': 'video/mp4',
            b'\x00\x00\x00\x20ftypmp42': 'video/mp4',
            b'\x00\x00\x00\x1CftypM4V': 'video/mp4',
            b'\x1A\x45\xDF\xA3': 'video/webm',
            b'\x1E\xDF\xA3': 'video/webm',
            b'\x00\x00\x00\x14ftypqt': 'video/quicktime',
        }
        
        self.mime_to_category = {
            'image/jpeg': '图片',
            'image/png': '图片',
            'image/gif': '图片',
            'image/bmp': '图片',
            'image/webp': '图片',
            'image/tiff': '图片',
            'image/vnd.adobe.photoshop': '图片',
            'application/pdf': '文档',
            'application/msword': '文档',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '文档',
            'application/vnd.ms-excel': '文档',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '文档',
            'application/vnd.ms-powerpoint': '文档',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '文档',
            'text/plain': '文档',
            'application/zip': '压缩包',
            'application/x-rar-compressed': '压缩包',
            'application/gzip': '压缩包',
            'application/x-7z-compressed': '压缩包',
            'application/x-msdownload': '安装包',
            'application/x-executable': '安装包',
            'application/x-mach-binary': '安装包',
            'application/x-dosexec': '安装包',
            'audio/mpeg': '音频',
            'audio/wav': '音频',
            'audio/ogg': '音频',
            'audio/flac': '音频',
            'video/mp4': '视频',
            'video/webm': '视频',
            'video/quicktime': '视频',
        }
    
    def detect_by_magic_number(self, file_path: str) -> Optional[str]:
        try:
            with open(file_path, 'rb') as f:
                header = f.read(32)
            
            for magic, mime in self.magic_numbers.items():
                if header.startswith(magic):
                    return mime
            
            return None
        except Exception as e:
            print(f"读取文件头失败: {e}")
            return None
    
    def detect_by_extension(self, file_path: str) -> Optional[str]:
        extension = Path(file_path).suffix.lower()
        
        ext_to_mime = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.7z': 'application/x-7z-compressed',
            '.gz': 'application/gzip',
            '.tar': 'application/x-tar',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mkv': 'video/x-matroska',
            '.mov': 'video/quicktime',
            '.webm': 'video/webm',
            '.exe': 'application/x-msdownload',
            '.msi': 'application/x-msdownload',
            '.dmg': 'application/x-apple-diskimage',
            '.py': 'text/x-python',
            '.js': 'text/javascript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.java': 'text/x-java-source',
            '.cpp': 'text/x-c++src',
            '.c': 'text/x-csrc',
            '.h': 'text/x-csrc',
        }
        
        return ext_to_mime.get(extension)
    
    def detect_file_type(self, file_path: str) -> Tuple[str, str, str]:
        mime_by_magic = self.detect_by_magic_number(file_path)
        mime_by_ext = self.detect_by_extension(file_path)
        
        # 特殊处理 Office 2007+ 文件（.docx, .xlsx, .pptx），它们本质上是 zip 压缩文件
        extension = Path(file_path).suffix.lower()
        office_open_xml_extensions = ['.docx', '.xlsx', '.pptx']
        
        if mime_by_magic and mime_by_ext:
            if mime_by_magic != mime_by_ext:
                # 检查是否是 Office Open XML 文件
                if mime_by_magic == 'application/zip' and extension in office_open_xml_extensions:
                    category = self.mime_to_category.get(mime_by_ext, "其他")
                    return category, mime_by_ext, "正常"
                else:
                    return "可疑文件", mime_by_magic, "伪装文件"
            else:
                category = self.mime_to_category.get(mime_by_magic, "其他")
                return category, mime_by_magic, "正常"
        elif mime_by_magic:
            category = self.mime_to_category.get(mime_by_magic, "其他")
            return category, mime_by_magic, "正常"
        elif mime_by_ext:
            category = self.mime_to_category.get(mime_by_ext, "其他")
            return category, mime_by_ext, "正常"
        else:
            return "其他", "application/octet-stream", "未知"
    
    def analyze_content(self, file_path: str) -> Optional[str]:
        try:
            extension = Path(file_path).suffix.lower()
            
            if extension in ['.txt', '.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4096)
                
                keywords = {
                    '财务': ['金额', '发票', '税号', '合同', '账单', '支付', '收款', '银行', '账户'],
                    '法律': ['合同', '协议', '律师', '诉讼', '判决', '法律', '条款', '责任'],
                    '工作': ['报告', '会议', '项目', '任务', '计划', '总结', '方案', '需求'],
                    '学习': ['教程', '笔记', '学习', '课程', '作业', '考试', '复习'],
                }
                
                for category, words in keywords.items():
                    for word in words:
                        if word in content:
                            return category
            
            return None
        except Exception as e:
            print(f"内容分析失败: {e}")
            return None