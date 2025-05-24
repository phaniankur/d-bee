import requests

def get_installed_ollama_models():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        data = response.json()
        models = [model["name"] for model in data.get("models", [])]
        return models
    except requests.exceptions.RequestException as e:
        print("Error fetching models:", e)
        return []
    
# Example usage
models = get_installed_ollama_models()
print("Installed Ollama Models:", models)