
import keyboard
import pyperclip
import logging
import time
import threading

def get_selected_text():
    """获取当前选中的文本并进行处理"""
    try:
        old_clipboard = pyperclip.paste()
        time.sleep(0.5)
        keyboard.press_and_release('ctrl+c')
        time.sleep(0.5)  # 增加更多等待时间
        selected_text = pyperclip.paste()
        if selected_text == old_clipboard:
            print("未检测到新选中的文本 - 请确保已选择文本")
            return None
        pyperclip.copy(old_clipboard)
        print(selected_text)
        return selected_text
    except Exception as e:
        logging.error(f"获取选中文本时出错: {str(e)}")
        return None

def main():
    print("正在监听 Win+Space 快捷键... (按 Ctrl+C 退出)")
    keyboard.add_hotkey('windows+space', get_selected_text)
    try:
        keyboard.wait('ctrl+c')  
        print("\n程序退出")
    except KeyboardInterrupt:
        print("\n程序被中断退出")
    finally:
        keyboard.unhook_all()
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()