import sys
import os
import threading
import pyperclip
import keyboard
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon, QMenu, 
                            QAction, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont, QCursor, QPixmap, QColor, QPainter, QBrush, QPen
import time
# 导入自定义模块
from utils.config import get_config, save_config
from utils.llm import translate_text

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("translator.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
def get_selected_text():
    """获取当前选中的文本并进行处理"""
    try:
        old_clipboard = pyperclip.paste()
        time.sleep(0.5)
        keyboard.press_and_release('ctrl+c')
        time.sleep(0.5)  # 增加更多等待时间
        selected_text = pyperclip.paste()
        pyperclip.copy(old_clipboard)
        
        return selected_text
    except Exception as e:
        logging.error(f"获取选中文本时出错: {str(e)}")
        return None
class SignalManager(QObject):
    translation_ready = pyqtSignal(str)
    copy_to_clipboard = pyqtSignal(str)
    show_window = pyqtSignal()
    set_translating = pyqtSignal()
    
signal_manager = SignalManager()

class ConfigWindow(QMainWindow):
    """
        点击设置跳出来的窗口
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("划词翻译 - 设置")
        self.setFixedSize(450, 400)  # 增加窗口高度
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                padding: 5px;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
                background-color: #ffffff;
                selection-background-color: #0078d7;
                font-size: 12px;
                min-height: 25px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 14px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #0063b1;
            }
            QPushButton:pressed {
                background-color: #004e8c;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 15px;
                font-weight: bold;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)  
        
        # 标题
        title_label = QLabel("API 设置")
        title_label.setStyleSheet("font-size: 18px; color: #0078d7; margin-bottom: 15px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建表单布局
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)  
        
        # URL设置
        url_layout = QVBoxLayout()
        url_layout.setSpacing(8)  # 设置标签和输入框之间的间距
        url_label = QLabel("API Base URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入API的URL，例如: https://api.openai.com/v1")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        form_layout.addLayout(url_layout)
        
        # API Key设置
        key_layout = QVBoxLayout()
        key_layout.setSpacing(8)  # 设置标签和输入框之间的间距
        key_label = QLabel("API Key:")
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("输入您的API密钥")
        self.key_input.setEchoMode(QLineEdit.Password)  # 密码模式显示
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_input)
        form_layout.addLayout(key_layout)
        
        # 模型设置
        model_layout = QVBoxLayout()
        model_layout.setSpacing(8)  # 设置标签和输入框之间的间距
        model_label = QLabel("模型:")
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("输入模型名称，例如: gpt-3.5-turbo")
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_input)
        form_layout.addLayout(model_layout)
        
        main_layout.addLayout(form_layout)
        
        # 添加一些空间
        main_layout.addStretch()
        
        # 保存按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_button = QPushButton("保存配置")
        save_button.setFixedWidth(150)
        save_button.clicked.connect(self.save_config)
        button_layout.addWidget(save_button)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
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
        
        if save_config(config):
            QMessageBox.information(self, "成功", "配置已保存")
            self.close()
        else:
            QMessageBox.warning(self, "错误", "保存配置失败")

class TranslationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                border-radius: 10px;
                border: 1px solid #CCCCCC;
            }
            QTextEdit {
                border: 5px solid #F5F5F5;
                background-color: #F5F5F5;
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

def handle_hotkey():
    """处理热键触发的翻译请求，从剪贴板获取文本"""
    try:
        # 直接从剪贴板获取内容
        selected_text = get_selected_text()
        print("selected_text",selected_text)
        logging.info(f"从剪贴板获取内容: {'有内容' if selected_text else '无内容'}")
        
        if selected_text and selected_text.strip():
            # 在主线程中显示窗口和设置状态
            # 这些信号应当只在主线程中触发和处理
            signal_manager.show_window.emit()
            signal_manager.set_translating.emit()
            
            # 在后台线程中执行翻译，避免阻塞UI
            def do_translation():
                try:
                    result = translate_text(selected_text)
                    # 通过信号更新翻译结果
                    signal_manager.translation_ready.emit(result)
                    # 不在线程中使用QSystemTrayIcon，改为设置一个标志
                    logging.info("翻译完成")
                except Exception as e:
                    logging.error(f"翻译线程中发生错误: {str(e)}")
                    signal_manager.translation_ready.emit(f"翻译过程中发生错误: {str(e)}")
            
            # 创建并启动线程
            translation_thread = threading.Thread(target=do_translation)
            translation_thread.daemon = True
            translation_thread.start()
        else:
            # 提示用户先复制文本
            logging.warning("剪贴板中没有内容")
            # 直接在主线程调用通知函数
            tray_icon.showMessage(
                "划词翻译", 
                "剪贴板中没有文本，请先选中并复制(Ctrl+C)文本",
                QSystemTrayIcon.Warning, 
                3000
            )
    except Exception as e:
        logging.error(f"热键处理过程中发生错误: {str(e)}")
        # 直接在主线程调用通知函数
        tray_icon.showMessage(
            "划词翻译出错", 
            f"发生错误: {str(e)}",
            QSystemTrayIcon.Critical, 
            3000
        )



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
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./asset/translator_icon.png")

        # 从本地读取图标
        app_icon = QIcon(icon_path)
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
        signal_manager.show_window.connect(translation_window.show_at_cursor)
        signal_manager.set_translating.connect(lambda: translation_window.text_display.setText("正在翻译..."))
        
        # 添加翻译完成时的通知
        def on_translation_ready(text):
            # 先更新翻译窗口
            translation_window.text_display.setText(text)
        
        # 重新连接translation_ready信号
        signal_manager.translation_ready.disconnect()  # 断开原来的连接
        signal_manager.translation_ready.connect(on_translation_ready)
        
        # 注册热键 - 只使用win+空格
        keyboard.add_hotkey('win+space', handle_hotkey)
        # 启动剪贴板监控线程 感觉没有什么用？？？
        # clipboard_thread = threading.Thread(target=monitor_clipboard)
        # clipboard_thread.daemon = True
        # clipboard_thread.start()
        
        # 启动时显示托盘提示
        tray_icon.showMessage(
            "划词翻译已启动", 
            "使用方法: 按Win+空格翻译",
            QSystemTrayIcon.Information, 
            300
        )
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"发生致命错误: {e}")
        QMessageBox.critical(None, "错误", f"发生致命错误: {e}")
        sys.exit(1) 