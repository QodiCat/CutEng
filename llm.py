import requests
import logging
from config import get_config

# 翻译提示词
TRANSLATION_SYSTEM_PROMPT = """
你是一个翻译助手，请将用户输入的英文单词或短语翻译成中文，并提供简短的解释。
如果是专业术语，请给出该领域的准确翻译。
如果有多种含义，请列出主要的几种含义。
格式如下：
【翻译】: 中文翻译
【释义】: 简短解释
【例句】: 一个简单例句（如有必要）
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