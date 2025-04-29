# 划词翻译工具

一个简单易用的划词翻译工具，支持选中文本后快速翻译。

## 功能特点

- 简洁的用户界面
- 系统托盘常驻
- 快捷键触发翻译
- 自定义API设置
- 支持多种大语言模型

## 使用方法

1. 选中需要翻译的文本
2. 按下快捷键 `Alt+Space`
3. 翻译结果会在小窗口中显示

## 构建应用

本项目提供了两个构建脚本：

### 基本构建 (build.py)

```bash
# 运行基本构建脚本
python build.py
```

这会创建一个单文件的可执行程序，位于`dist`目录下。

### 高级构建 (build_extra.py)

```bash
# 构建单文件应用
python build_extra.py --onefile --windowed

# 构建带图标的应用
python build_extra.py --onefile --windowed --icon=app.ico

# 查看帮助
python build_extra.py --help
```

高级构建提供更多选项：
- `--name`: 指定应用名称
- `--onefile`: 打包为单文件
- `--windowed`: 无控制台窗口
- `--installer`: 创建安装程序(尚未实现)
- `--upx`: 使用UPX压缩(需要安装UPX)

## 系统要求

- Windows 10/11
- Python 3.7+
- 依赖库:
  - PyQt5
  - keyboard
  - pyperclip

## 配置

在首次运行时，你需要在设置中配置:
1. API Base URL: API服务器地址
2. API Key: 你的API密钥 
3. 模型: 要使用的语言模型名称

## 许可证

MIT License
