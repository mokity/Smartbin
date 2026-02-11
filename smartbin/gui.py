import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QSystemTrayIcon, QMenu, QAction, QFileDialog,
                             QMessageBox, QSlider, QComboBox, QListWidget, QListWidgetItem,
                             QGroupBox, QLineEdit, QTextEdit, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QDragEnterEvent, QDropEvent
from pathlib import Path
from typing import List

class FloatingWidget(QWidget):
    files_dropped = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAcceptDrops(True)
        
        self.setFixedSize(100, 100)
        self.setStyleSheet("""
            QWidget {
                background: rgba(59, 130, 246, 200);
                border-radius: 50px;
            }
        """)
        
        self.setup_ui()
        self.is_dragging = False
        self.drag_position = QPoint()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel("📦")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 50px;
                background: transparent;
            }
        """)
        
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        color = QColor(59, 130, 246, 200)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 50, 50)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QWidget {
                    background: rgba(34, 197, 94, 200);
                    border-radius: 50px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QWidget {
                background: rgba(59, 130, 246, 200);
                border-radius: 50px;
            }
        """)
    
    def dropEvent(self, event):
        self.setStyleSheet("""
            QWidget {
                background: rgba(59, 130, 246, 200);
                border-radius: 50px;
            }
        """)
        
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                files.append(url.toLocalFile())
        
        if files:
            self.files_dropped.emit(files)
        
        event.acceptProposedAction()

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("SmartBin 设置")
        self.setFixedSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        target_group = QGroupBox("目标目录")
        target_layout = QHBoxLayout()
        self.target_path = QLineEdit(self.config.config.get('target_directory', ''))
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_directory)
        target_layout.addWidget(self.target_path)
        target_layout.addWidget(browse_btn)
        target_group.setLayout(target_layout)
        
        conflict_group = QGroupBox("文件冲突处理")
        conflict_layout = QHBoxLayout()
        self.conflict_combo = QComboBox()
        self.conflict_combo.addItems(['rename', 'overwrite', 'skip'])
        self.conflict_combo.setCurrentText(self.config.config.get('conflict_strategy', 'rename'))
        conflict_layout.addWidget(QLabel("策略:"))
        conflict_layout.addWidget(self.conflict_combo)
        conflict_group.setLayout(conflict_layout)
        
        transparency_group = QGroupBox("界面透明度")
        transparency_layout = QHBoxLayout()
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(50, 100)
        self.transparency_slider.setValue(int(self.config.config.get('ui_settings', {}).get('transparency', 0.9) * 100))
        self.transparency_label = QLabel(f"{self.transparency_slider.value()}%")
        self.transparency_slider.valueChanged.connect(lambda v: self.transparency_label.setText(f"{v}%"))
        transparency_layout.addWidget(self.transparency_slider)
        transparency_layout.addWidget(self.transparency_label)
        transparency_group.setLayout(transparency_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(target_group)
        layout.addWidget(conflict_group)
        layout.addWidget(transparency_group)
        layout.addWidget(buttons)
        self.setLayout(layout)
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择目标目录")
        if directory:
            self.target_path.setText(directory)
    
    def save_settings(self):
        self.config.config['target_directory'] = self.target_path.text()
        self.config.config['conflict_strategy'] = self.conflict_combo.currentText()
        self.config.config['ui_settings']['transparency'] = self.transparency_slider.value() / 100
        self.config.save_config()
        self.accept()

class HistoryDialog(QDialog):
    def __init__(self, operations_log, parent=None):
        super().__init__(parent)
        self.setWindowTitle("操作历史")
        self.setFixedSize(600, 400)
        self.setup_ui(operations_log)
    
    def setup_ui(self, operations_log):
        layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        
        for op in reversed(operations_log):
            item_text = f"{op['timestamp'][:19]} | {op['operation']} | {Path(op['source']).name} -> {Path(op['destination']).name}"
            item = QListWidgetItem(item_text)
            self.history_list.addItem(item)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.accept)
        
        layout.addWidget(QLabel("最近操作:"))
        layout.addWidget(self.history_list)
        layout.addWidget(buttons)
        self.setLayout(layout)

class SmartBinGUI:
    def __init__(self, config, file_processor, file_recognizer):
        self.config = config
        self.file_processor = file_processor
        self.file_recognizer = file_recognizer
        
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.setup_tray_icon()
        self.setup_floating_widget()
        self.setup_notification()
    
    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon()
        
        icon = self.create_icon()
        self.tray_icon.setIcon(icon)
        
        menu = QMenu()
        
        show_action = QAction("显示图标", self.app)
        show_action.triggered.connect(self.show_floating_widget)
        menu.addAction(show_action)
        
        history_action = QAction("操作历史", self.app)
        history_action.triggered.connect(self.show_history)
        menu.addAction(history_action)
        
        settings_action = QAction("设置", self.app)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        undo_action = QAction("撤销上一步", self.app)
        undo_action.triggered.connect(self.undo_last)
        menu.addAction(undo_action)
        
        menu.addSeparator()
        
        quit_action = QAction("退出", self.app)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
    
    def setup_floating_widget(self):
        self.floating_widget = FloatingWidget()
        
        ui_settings = self.config.config.get('ui_settings', {})
        position = ui_settings.get('position', {'x': 100, 'y': 100})
        self.floating_widget.move(position['x'], position['y'])
        
        transparency = ui_settings.get('transparency', 0.9)
        self.floating_widget.setWindowOpacity(transparency)
        
        self.floating_widget.files_dropped.connect(self.handle_dropped_files)
        self.floating_widget.show()
    
    def setup_notification(self):
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.hide_notification)
    
    def create_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        color = QColor(59, 130, 246)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 64, 64, 16, 16)
        
        painter.setPen(Qt.white)
        font = QFont()
        font.setPointSize(32)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "📦")
        
        painter.end()
        
        return QIcon(pixmap)
    
    def show_floating_widget(self):
        self.floating_widget.show()
        self.floating_widget.raise_()
    
    def hide_floating_widget(self):
        self.floating_widget.hide()
    
    def show_settings(self):
        dialog = SettingsDialog(self.config)
        if dialog.exec_() == QDialog.Accepted:
            self.apply_settings()
    
    def show_history(self):
        dialog = HistoryDialog(self.file_processor.operations_log)
        dialog.exec_()
    
    def undo_last(self):
        result = self.file_processor.undo_last_operation()
        if result and result['success']:
            self.show_notification("撤销成功")
        else:
            self.show_notification("撤销失败: " + (result.get('error', '未知错误')))
    
    def handle_dropped_files(self, files):
        results = self.file_processor.batch_process(files, self.file_recognizer)
        
        success_count = sum(1 for r in results if r['success'])
        fail_count = len(results) - success_count
        
        if success_count > 0:
            message = f"已处理 {success_count} 个文件"
            if fail_count > 0:
                message += f"，失败 {fail_count} 个"
            self.show_notification(message)
        else:
            self.show_notification("处理失败")
    
    def show_notification(self, message):
        self.tray_icon.showMessage("SmartBin", message, QSystemTrayIcon.Information, 3000)
    
    def hide_notification(self):
        pass
    
    def apply_settings(self):
        ui_settings = self.config.config.get('ui_settings', {})
        transparency = ui_settings.get('transparency', 0.9)
        self.floating_widget.setWindowOpacity(transparency)
    
    def quit(self):
        position = self.floating_widget.pos()
        self.config.config['ui_settings']['position'] = {'x': position.x(), 'y': position.y()}
        self.config.save_config()
        self.app.quit()
    
    def run(self):
        return self.app.exec_()