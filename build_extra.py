import os
import sys
import shutil
import subprocess
import platform
import argparse
import time
from pathlib import Path

def ensure_module_installed(module_name, package_name=None):
    """确保指定模块已安装"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"{module_name} 已安装 ✓")
        return True
    except ImportError:
        print(f"正在安装 {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"{package_name} 安装完成 ✓")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ 安装 {package_name} 失败")
            return False

def check_dependencies():
    """检查并确保所有依赖已安装"""
    dependencies = [
        ("PyInstaller", "pyinstaller"),
        ("keyboard", "keyboard"),
        ("pyperclip", "pyperclip"),
        ("PyQt5", "pyqt5")
    ]
    
    all_installed = True
    for module, package in dependencies:
        if not ensure_module_installed(module, package):
            all_installed = False
    
    return all_installed

def cleanup_previous_build():
    """清理之前的构建文件和目录"""
    paths_to_clean = [
        Path("build"),
        Path("dist"),
        Path("translator.spec")
    ]
    
    for path in paths_to_clean:
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"已清理: {path}")
            except Exception as e:
                print(f"清理 {path} 时出错: {e}")

def collect_project_files():
    """收集项目的关键文件"""
    project_files = {
        "entry_file": Path("translator.py"),
        "config_file": Path("config.json"),
        "icon_file": Path("app.ico")
    }
    
    # 检查入口文件是否存在
    if not project_files["entry_file"].exists():
        print(f"❌ 错误: 入口文件 {project_files['entry_file']} 不存在!")
        return None
    
    # 如果配置文件不存在，创建一个默认配置
    if not project_files["config_file"].exists():
        try:
            import json
            default_config = {
                "api_base_url": "",
                "api_key": "",
                "model": "gpt-3.5-turbo"
            }
            with open(project_files["config_file"], "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4)
            print(f"创建了默认配置文件: {project_files['config_file']}")
        except Exception as e:
            print(f"创建默认配置文件失败: {e}")
    
    return project_files

def build_executable(project_files, options):
    """使用PyInstaller构建可执行文件"""
    app_name = options["app_name"]
    icon_param = f"--icon={project_files['icon_file']}" if project_files["icon_file"].exists() else ""
    
    # 构建基本命令
    cmd = [
        sys.executable, 
        "-m", "PyInstaller",
        "--name", app_name,
        "--clean",
        "--noconfirm"
    ]
    
    # 根据选项添加命令行参数
    if options["onefile"]:
        cmd.append("--onefile")
    
    if options["windowed"]:
        cmd.append("--windowed")
    
    if icon_param:
        cmd.append(icon_param)
    
    # 添加数据文件
    if project_files["config_file"].exists():
        cmd.extend(["--add-data", f"{project_files['config_file']}{os.pathsep}."])
    
    # 添加需要的模块
    for module in ["keyboard", "pyperclip", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets"]:
        cmd.extend(["--hidden-import", module])
    
    # 添加入口文件
    cmd.append(str(project_files["entry_file"]))
    
    # 过滤空参数
    cmd = [item for item in cmd if item]
    
    # 执行命令
    print("\n" + "=" * 50)
    print("执行打包命令:", " ".join(cmd))
    print("=" * 50 + "\n")
    
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败，错误代码: {e.returncode}")
        return False

def create_installer(options):
    """创建安装程序(如果需要)"""
    if not options["create_installer"]:
        return
    
    try:
        import inno_setup_compiler
        # 这里添加创建安装程序的代码
        print("创建安装程序功能尚未实现")
    except ImportError:
        print("要创建安装程序，请先安装 inno-setup-compiler 包")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="构建划词翻译应用程序")
    parser.add_argument("--name", default="划词翻译", help="应用程序名称")
    parser.add_argument("--onefile", action="store_true", help="构建为单文件")
    parser.add_argument("--windowed", action="store_true", help="无控制台窗口")
    parser.add_argument("--installer", action="store_true", help="创建安装程序")
    parser.add_argument("--upx", action="store_true", help="使用UPX压缩")
    
    args = parser.parse_args()
    
    options = {
        "app_name": args.name,
        "onefile": args.onefile,
        "windowed": args.windowed,
        "create_installer": args.installer,
        "use_upx": args.upx
    }
    
    start_time = time.time()
    
    print("=" * 50)
    print(f"开始构建 {options['app_name']} 应用程序...")
    print("=" * 50)
    
    # 1. 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，构建中止")
        return
    
    # 2. 清理之前的构建
    cleanup_previous_build()
    
    # 3. 收集项目文件
    project_files = collect_project_files()
    if not project_files:
        return
    
    # 4. 构建可执行文件
    if not build_executable(project_files, options):
        return
    
    # 5. 创建安装程序(如果需要)
    create_installer(options)
    
    elapsed_time = time.time() - start_time
    
    # 6. 完成信息
    dist_dir = Path("dist")
    exe_name = f"{options['app_name']}{'.exe' if platform.system() == 'Windows' else ''}"
    exe_path = dist_dir / exe_name
    
    print("\n" + "=" * 50)
    print(f"✅ 构建完成! 耗时: {elapsed_time:.2f} 秒")
    print(f"可执行文件位于: {exe_path}")
    print("=" * 50)

if __name__ == "__main__":
    main() 