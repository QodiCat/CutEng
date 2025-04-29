import requests
import logging
from config import get_config

# 翻译提示词
TRANSLATION_SYSTEM_PROMPT = """
你是一个翻译助手，可以提供中英相互翻译，如果是英文则翻译为中文，反之亦然
返回结果只有翻译后的内容，不要包含其他内容
"""

def translate_text(text):
    """
    调用大语言模型API进行翻译
    
    Args:
        text: 要翻译的文本
        
    Returns:
        翻译结果或错误信息
    """
    config = get_config()
    api_base_url = config["api_base_url"]
    api_key = config["api_key"]
    model = config["model"]
    
    if not api_key:
        logging.warning("API密钥未设置")
        return "错误: 请先设置API密钥"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
            {"role": "user", "content": f"请翻译: {text}"}
        ]
    }
    
    try:
        logging.info(f"开始翻译: {text[:30]}...")
        response = requests.post(
            f"{api_base_url.rstrip('/')}/chat/completions", 
            headers=headers, 
            json=data, 
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        translation = result["choices"][0]["message"]["content"]
        logging.info("翻译成功")
        return translation
    except requests.exceptions.RequestException as e:
        logging.error(f"API请求错误: {str(e)}")
        return f"翻译出错: API请求失败\n{str(e)}"
    except KeyError as e:
        logging.error(f"API响应解析错误: {str(e)}")
        return f"翻译出错: API响应格式异常\n{str(e)}"
    except Exception as e:
        logging.error(f"未知错误: {str(e)}")
        return f"翻译出错: {str(e)}" 