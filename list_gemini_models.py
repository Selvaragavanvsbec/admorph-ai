from google import genai
from config import settings

def list_models():
    api_key = settings.llm_api_key
    if not api_key:
        print("Error: No LLM_API_KEY found in settings.")
        return
    
    client = genai.Client(api_key=api_key)
    
    print(f"Checking models for API key: {api_key[:5]}...{api_key[-5:]}")
    try:
        # The new SDK might have a different way to list models
        # But usually we can just try to list them
        print("\nAvailable Gemini Models:")
        for model in client.models.list():
            print(f"- {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
