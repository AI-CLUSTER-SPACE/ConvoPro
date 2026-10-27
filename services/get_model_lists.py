from config.settings import Settings

settings = Settings()

def get_ollama_model_lists():
    model_list = settings.OLLAMA_MODELS
    ollama_models = [model.strip() for model in model_list.split(",") if model.strip()]
    return ollama_models