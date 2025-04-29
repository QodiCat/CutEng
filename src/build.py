import os
import sys
import shutil
import subprocess
import argparse

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)

def build_exe(one_file=False, console=False, icon=True):
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 确保PyInstaller已安装
    try:
        import PyInstaller
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--name=CutEng划词翻译",
        "--noconfirm",
    ]
    
    # 添加图标
    if icon:
        icon_path = os.path.join("assets", "translator_icon.png")
        if os.path.exists(icon_path):
            # 转换PNG为ICO (如果需要)
            try:
                from PIL import Image
                ico_path = os.path.join("assets", "translator_icon.ico")
                if not os.path.exists(ico_path):
                    print("转换PNG图标为ICO...")
                    img = Image.open(icon_path)
                    img.save(ico_path)
                cmd.extend(["--icon", ico_path])
            except ImportError:
                print("警告: 未安装Pillow, 无法转换图标。将使用原始PNG图标。")
                cmd.extend(["--icon", icon_path])
        else:
            print(f"警告: 图标文件 {icon_path} 不存在")
    
    # 添加数据文件
    cmd.extend([
        "--add-data", f"assets{os.pathsep}assets",
        "--add-data", f"utils{os.pathsep}utils"
    ])
    
    # 是否打包成单个文件
    if one_file:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")
    
    # 是否显示控制台
    if not console:
        cmd.append("--noconsole")
    
    # 主脚本
    cmd.append("main.py")
    
    # 执行命令
    print("执行命令:", " ".join(cmd))
    subprocess.check_call(cmd)
    
    print("\n构建完成!")
    print("可执行文件位于 dist 目录")

def create_installer(name="CutEng划词翻译安装程序"):
    """创建安装程序 (使用NSIS)"""
    print("创建安装程序功能尚未实现...")
    # 此处可以添加使用NSIS或其他工具创建安装程序的代码

def main():
    parser = argparse.ArgumentParser(description="构建CutEng划词翻译应用")
    parser.add_argument("--clean", action="store_true", help="清理构建目录")
    parser.add_argument("--onefile", action="store_true", help="打包成单个文件")
    parser.add_argument("--console", action="store_true", help="显示控制台窗口")
    parser.add_argument("--no-icon", action="store_false", dest="icon", help="不使用图标")
    parser.add_argument("--installer", action="store_true", help="创建安装程序")
    
    args = parser.parse_args()
    
    # 清理目录
    if args.clean:
        clean_build_dirs()
    
    # 构建可执行文件
    build_exe(one_file=args.onefile, console=args.console, icon=args.icon)
    
    # 创建安装程序
    if args.installer:
        create_installer()

if __name__ == "__main__":
    main() 