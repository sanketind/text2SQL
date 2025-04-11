import requests
import json

# Test context window
response = requests.post("http://localhost:11434/api/generate", 
    json={
        "model": "llama3.2",
        "prompt": "What is your context window size? Please provide a single number.",
        "stream": False
    }
)

print("\nAsking about context window size:")
result = response.json()
if 'response' in result:
    print(result['response'])
