from config import settings
import time
import functools

def retry_on_quota(retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if "429" in str(e) or "quota" in str(e).lower():
                        print(f"Quota Hit. Retrying in {delay}s... (Attempt {i+1}/{retries})")
                        time.sleep(delay)
                    else:
                        raise e
            raise last_exception
        return wrapper
    return decorator

def get_llm():
    """Returns a LangChain chat model based on the configured provider with lazy imports."""
    provider = settings.llm_provider.lower()
    api_key = settings.llm_api_key
    model = settings.llm_model

    print(f"--- LLM Factory Injection ---")
    print(f"Provider: {provider}")
    print(f"Model ID: {model}")
    print(f"API Key Present: {'Yes' if api_key else 'No'}")
    print(f"-----------------------------")

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, api_key=api_key)
    elif provider == "google" or provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Use api_key if provided, otherwise let it fall back to environment variables
        kwargs = {
            "model": model,
            "convert_system_message_to_human": True,
            "max_retries": 1
        }
        if api_key:
            kwargs["api_key"] = api_key
            
        return ChatGoogleGenerativeAI(**kwargs)
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model, api_key=api_key)
    elif provider == "grok":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model, 
            api_key=api_key, 
            base_url="https://api.x.ai/v1"
        )
    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
