from dataclasses import field

from kayaku import config


@config("library.service.openai")
class OpenAIConfig:
    """OpenAI 配置"""

    api_keys: list[str] = field(default_factory=list)
    """ OpenAI API Key """

    chatgpt_temperature: float = 1
    """ ChatGPT Temperature """

    chatgpt_cache: int = 4
    """ ChatGPT 缓存对话数量 """

    chatgpt_max_token: int = 2000
    """ ChatGPT 最大 Token 数量 """

    chatgpt_model: str = "gpt-3.5-turbo"
    """ ChatGPT 模型 """
