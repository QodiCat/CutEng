import os
import json
import logging

# 配置文件路径和默认设置
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "api_base_url": "https://api.openai.com/v1",
    "api_key": "",
    "model": "gpt-3.5-turbo"
}

def get_config():
    """读取配置文件，如果不存在则返回默认配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"读取配置文件失败: {str(e)}")
            return DEFAULT_CONFIG
    else:
        return DEFAULT_CONFIG

def save_config(config):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        logging.error(f"保存配置文件失败: {str(e)}")
        return False 