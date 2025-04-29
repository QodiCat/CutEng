import os
import sys
import shutil
import subprocess
import platform

def build_exe():
    """
    打包项目为单个可执行文件，使用PyInstaller
    """
    print("=" * 50)
    print("开始构建可执行文件...")
    print("=" * 50)
    
    # 确保PyInstaller已安装
    try:
        import PyInstaller
        print("PyInstaller已安装✓")
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
        print("PyInstaller安装完成✓")
    
    # 清理之前的构建
    build_dir = os.path.join(os.getcwd(), "build")
    dist_dir = os.path.join(os.getcwd(), "dist")
    spec_file = os.path.join(os.getcwd(), "translator.spec")
    
    for path in [build_dir, dist_dir, spec_file]:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            print(f"已清理: {path}")
    
    # 确定入口文件
    entry_file = os.path.join(os.getcwd(), "translator.py")
    if not os.path.exists(entry_file):
        print(f"错误: 入口文件 {entry_file} 不存在!")
        return
    
    # 准备打包命令
    app_name = "划词翻译"
    icon_file = "--icon=app.ico" if os.path.exists("app.ico") else ""
    
    # 构建PyInstaller命令
    cmd = [
        sys.executable, 
        "-m", "PyInstaller",
        "--name", app_name,
        "--onefile",  # 单文件模式
        "--windowed",  # 无控制台窗口
        "--clean",
        "--noconfirm",
        icon_file,
        # 添加额外数据文件
        "--add-data", f"config.json{os.pathsep}.",
        # 添加额外模块
        "--hidden-import", "keyboard",
        "--hidden-import", "pyperclip",
        entry_file
    ]
    
    # 过滤空字符串
    cmd = [item for item in cmd if item]
    
    print("执行打包命令:", " ".join(cmd))
    subprocess.check_call(cmd)
    
    print("\n" + "=" * 50)
    print(f"构建完成! 可执行文件位于: {os.path.join(dist_dir, app_name + ('.exe' if platform.system() == 'Windows' else ''))}")
    print("=" * 50)

if __name__ == "__main__":
    build_exe() 