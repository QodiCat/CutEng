import sys
import os
import json
import keyboard
import pyperclip
import threading
import requests
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon, QMenu, 
                            QAction, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont, QCursor, QPixmap, QColor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("translator.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "api_base_url": "https://api.openai.com/v1",
    "api_key": "",
    "model": "gpt-3.5-turbo"
}

class SignalManager(QObject):
    translation_ready = pyqtSignal(str)
    copy_to_clipboard = pyqtSignal(str)
    start_translation = pyqtSignal()
    show_notification = pyqtSignal(str, str, object, int)  # 标题、内容、图标类型、显示时间
    show_window = pyqtSignal()
    set_translating = pyqtSignal()
    
signal_manager = SignalManager()

class ConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("划词翻译 - 设置")
        self.setFixedSize(400, 300)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        
        # URL设置
        url_layout = QHBoxLayout()
        url_label = QLabel("API Base URL:")
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # API Key设置
        key_layout = QHBoxLayout()
        key_label = QLabel("API Key:")
        self.key_input = QLineEdit()
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_input)
        layout.addLayout(key_layout)
        
        # 模型设置
        model_layout = QHBoxLayout()
        model_label = QLabel("模型:")
        self.model_input = QLineEdit()
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_input)
        layout.addLayout(model_layout)
        
        # 保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)
        
        # 加载配置
        self.load_config()
        
    def load_config(self):
        config = get_config()
        self.url_input.setText(config["api_base_url"])
        self.key_input.setText(config["api_key"])
        self.model_input.setText(config["model"])
        
    def save_config(self):
        config = {
            "api_base_url": self.url_input.text(),
            "api_key": self.key_input.text(),
            "model": self.model_input.text()
        }
        
        save_config(config)
        QMessageBox.information(self, "成功", "配置已保存")
        self.close()

class TranslationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #CCCCCC;
            }
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 14px;
                color: #333333;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFixedSize(300, 200)
        self.layout.addWidget(self.text_display)
        
        button_layout = QHBoxLayout()
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.hide)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # 复制按钮
        copy_button = QPushButton("复制结果")
        copy_button.clicked.connect(self.copy_result)
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        button_layout.addWidget(copy_button)
        button_layout.addWidget(close_button)
        
        self.layout.addLayout(button_layout)
        
        self.setFixedSize(330, 250)
        signal_manager.translation_ready.connect(self.update_translation)
        
    def show_at_cursor(self):
        cursor_pos = QCursor.pos()
        screen_rect = QApplication.desktop().screenGeometry()
        
        x = min(cursor_pos.x(), screen_rect.width() - self.width())
        y = min(cursor_pos.y(), screen_rect.height() - self.height())
        
        self.move(x, y)
        self.show()
        self.raise_()  # 确保窗口显示在最前面
        self.activateWindow()  # 激活窗口
        
        # 额外的激活措施
        QTimer.singleShot(50, self.force_activate)
    
    def force_activate(self):
        """强制激活窗口"""
        self.raise_()
        self.activateWindow()
        
    def update_translation(self, text):
        self.text_display.setText(text)
        
    def copy_result(self):
        text = self.text_display.toPlainText()
        if text:
            # 通过信号将复制操作分发到主线程
            signal_manager.copy_to_clipboard.emit(text)
            # 显示一个简短的提示
            self.show_copy_feedback()
    
    def show_copy_feedback(self):
        feedback = QLabel("已复制!", self)
        feedback.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            border-radius: 4px;
            padding: 5px;
        """)
        feedback.adjustSize()
        
        # 在窗口中间显示
        feedback.move(
            (self.width() - feedback.width()) // 2,
            (self.height() - feedback.height()) // 2
        )
        
        feedback.show()
        # 1秒后隐藏
        QTimer.singleShot(1000, feedback.deleteLater)
        
    def closeEvent(self, event):
        # 拦截关闭事件，改为隐藏
        event.ignore()
        self.hide()

def get_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG
    else:
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def translate_text(text):
    config = get_config()
    api_base_url = config["api_base_url"]
    api_key = config["api_key"]
    model = config["model"]
    
    if not api_key:
        logging.warning("API密钥未设置")
        return "错误: 请先设置API密钥"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个翻译助手，请将用户输入的英文单词或短语翻译成中文，并提供简短的解释。"},
            {"role": "user", "content": f"请翻译: {text}"}
        ]
    }
    
    try:
        logging.info(f"开始翻译: {text[:30]}...")
        response = requests.post(
            f"{api_base_url.rstrip('/')}/v1/chat/completions", 
            headers=headers, 
            json=data, 
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        translation = result["choices"][0]["message"]["content"]
        logging.info("翻译成功")
        return translation
    except requests.exceptions.RequestException as e:
        logging.error(f"API请求错误: {str(e)}")
        return f"翻译出错: API请求失败\n{str(e)}"
    except KeyError as e:
        logging.error(f"API响应解析错误: {str(e)}")
        return f"翻译出错: API响应格式异常\n{str(e)}"
    except Exception as e:
        logging.error(f"未知错误: {str(e)}")
        return f"翻译出错: {str(e)}"

def handle_hotkey():
    try:
        # 获取剪贴板中的选中文本
        selected_text = pyperclip.paste()
        logging.info(f"获取剪贴板内容: {'有内容' if selected_text else '无内容'}")
        
        if selected_text and selected_text.strip():
            # 通过信号在主线程中执行UI操作
            signal_manager.show_window.emit()
            signal_manager.set_translating.emit()
            
            # 在后台线程中执行翻译，避免阻塞UI
            def do_translation():
                try:
                    result = translate_text(selected_text)
                    signal_manager.translation_ready.emit(result)
                    # 通过信号发送托盘通知
                    signal_manager.show_notification.emit(
                        "翻译完成", 
                        f"原文: {selected_text[:20]}...\n结果已显示在小窗口中",
                        QSystemTrayIcon.Information, 
                        3000
                    )
                except Exception as e:
                    logging.error(f"翻译线程中发生错误: {str(e)}")
                    signal_manager.translation_ready.emit(f"翻译过程中发生错误: {str(e)}")
            
            threading.Thread(target=do_translation).start()
        else:
            # 如果剪贴板为空，显示提示
            signal_manager.show_notification.emit(
                "划词翻译", 
                "剪贴板中没有文本，请先选中并复制(Ctrl+C)文本",
                QSystemTrayIcon.Warning, 
                3000
            )
    except Exception as e:
        logging.error(f"热键处理过程中发生错误: {str(e)}")
        signal_manager.show_notification.emit(
            "划词翻译出错", 
            f"发生错误: {str(e)}",
            QSystemTrayIcon.Critical, 
            3000
        )

def translate_clipboard():
    """复制当前选中文本并直接翻译，一步完成划词翻译"""
    # 模拟复制操作
    keyboard.press_and_release('ctrl+c')
    # 给剪贴板一点时间复制文本
    # 使用Qt的计时器在主线程中执行
    signal_manager.start_translation.emit()

def monitor_clipboard():
    while True:
        try:
            # 这个线程只是为了保持应用运行
            import time
            time.sleep(0.5)
        except:
            break

if __name__ == "__main__":
    # 全局异常处理
    def exception_hook(exctype, value, traceback):
        print(f"未捕获的异常: {exctype}, {value}")
        sys.__excepthook__(exctype, value, traceback)
        # 对于严重错误，可以显示错误消息
        if exctype not in (KeyboardInterrupt,):  # 忽略键盘中断
            QMessageBox.critical(None, "错误", f"发生错误: {value}")
    
    sys.excepthook = exception_hook
    
    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        # 创建系统托盘图标
        tray_icon = QSystemTrayIcon()
        
        # 创建一个简单的图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))  # 透明背景
        
        # 在pixmap上绘制一个简单的图标
        from PyQt5.QtGui import QPainter, QBrush, QPen
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆形背景
        painter.setBrush(QBrush(QColor(52, 152, 219)))  # 蓝色背景
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        
        # 绘制字母T
        painter.setPen(QPen(QColor(255, 255, 255), 4))  # 白色粗笔
        painter.drawLine(20, 20, 44, 20)  # 横线
        painter.drawLine(32, 20, 32, 44)  # 竖线
        
        painter.end()
        
        # 创建图标并设置
        app_icon = QIcon(pixmap)
        tray_icon.setIcon(app_icon)
        app.setWindowIcon(app_icon)
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        config_action = QAction("设置")
        quit_action = QAction("退出")
        
        tray_menu.addAction(config_action)
        tray_menu.addAction(quit_action)
        
        tray_icon.setContextMenu(tray_menu)
        tray_icon.show()
        
        # 创建窗口
        config_window = ConfigWindow()
        translation_window = TranslationWindow()
        
        # 连接信号
        config_action.triggered.connect(config_window.show)
        quit_action.triggered.connect(app.quit)
        signal_manager.copy_to_clipboard.connect(lambda text: pyperclip.copy(text))
        signal_manager.start_translation.connect(lambda: QTimer.singleShot(100, handle_hotkey))
        signal_manager.show_notification.connect(
            lambda title, msg, icon, duration: tray_icon.showMessage(title, msg, icon, duration)
        )
        signal_manager.show_window.connect(translation_window.show_at_cursor)
        signal_manager.set_translating.connect(lambda: translation_window.text_display.setText("正在翻译..."))
        
        # 注册热键
        # Alt+空格: 使用剪贴板中已有的内容翻译
        keyboard.add_hotkey('alt+space', handle_hotkey)
        # Alt+C: 一步完成选中、复制、翻译
        keyboard.add_hotkey('alt+c', translate_clipboard)
        
        # 启动剪贴板监控线程
        clipboard_thread = threading.Thread(target=monitor_clipboard)
        clipboard_thread.daemon = True
        clipboard_thread.start()
        
        # 启动时显示托盘提示
        tray_icon.showMessage(
            "划词翻译已启动", 
            "划词方式1: 选中文本 → 复制(Ctrl+C) → Alt+空格\n划词方式2: 选中文本 → Alt+C",
            QSystemTrayIcon.Information, 
            5000
        )
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"发生致命错误: {e}")
        QMessageBox.critical(None, "错误", f"发生致命错误: {e}")
        sys.exit(1) 