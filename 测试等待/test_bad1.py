import keyboard
import pyperclip
import logging
import time
def get_selected_text():
    """获取当前选中的文本"""
    try:
        # 保存当前剪贴板内容
        print("保存当前剪贴板内容")
        old_clipboard = pyperclip.paste()
        
        # 模拟Ctrl+C复制选中文本
        keyboard.press_and_release('ctrl+c')
        
        # 给剪贴板一点时间更新
        import time
        time.sleep(0.1)  # 使用time.sleep替代QTimer
        
        # 获取新的剪贴板内容(即选中的文本)
        selected_text = pyperclip.paste()
        print(selected_text)
        # 恢复原剪贴板内容(可选，视需求而定)
        pyperclip.copy(old_clipboard)
        
        return selected_text
    except Exception as e:
        logging.error(f"获取选中文本时出错: {str(e)}")
        return ""


def main():
    print("正在监听 Win+Space 快捷键... (按 Ctrl+C 退出)")
    
    # 注册 Win+Space 快捷键
    keyboard.add_hotkey('windows+space', get_selected_text)
    
    try:
        # 保持程序运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n程序退出")
    finally:
        # 清理键盘监听
        keyboard.unhook_all()

if __name__ == "__main__":
    main()
