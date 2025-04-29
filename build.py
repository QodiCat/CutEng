import subprocess
import sys

def build_exe():
    """构建EXE文件"""
    print("正在构建EXE文件...")
    
    # 检查PyInstaller是否安装
    try:
        import PyInstaller
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # 构建命令
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=CutEng划词翻译',
        'translator.py'
    ]
    
    # 运行构建命令
    subprocess.check_call(cmd)
    
    print("\n构建完成! 可执行文件位于 dist/CutEng划词翻译.exe")

if __name__ == "__main__":
    build_exe() 