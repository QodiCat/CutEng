import subprocess
import sys
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("build.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def check_files():
    """检查必要的文件是否存在"""
    required_files = ['translator.py', 'config.py', 'llm.py', '__init__.py']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logging.error(f"缺少必要文件: {', '.join(missing_files)}")
        return False
    
    return True

def build_exe():
    """构建EXE文件"""
    logging.info("开始构建EXE文件...")
    
    if not check_files():
        logging.error("构建失败: 文件不完整")
        return False
    
    # 检查PyInstaller是否安装
    try:
        import PyInstaller
    except ImportError:
        logging.info("正在安装PyInstaller...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        except Exception as e:
            logging.error(f"安装PyInstaller失败: {str(e)}")
            return False
    
    # 构建命令
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=CutEng划词翻译',
        '--hidden-import=llm',
        '--hidden-import=config',
        'translator.py'
    ]
    
    try:
        # 运行构建命令
        subprocess.check_call(cmd)
        logging.info("构建完成! 可执行文件位于 dist/CutEng划词翻译.exe")
        return True
    except Exception as e:
        logging.error(f"构建过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = build_exe()
    if not success:
        sys.exit(1) 