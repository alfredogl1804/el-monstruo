"""
Diagnóstico aislado para Perplexity API (403 Forbidden).
"""
import os
import requests
import json

def test_perplexity():
    api_key = os.environ.get("SONAR_API_KEY")
    if not api_key:
        print("ERROR: SONAR_API_KEY no está configurada.")
        return

    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "max_tokens": 50
    }
    
    print(f"Testing Perplexity API at {url}...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS! Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("FAILED. Response Body:")
            print(response.text)
    except Exception as e:
        print(f"Exception during request: {e}")

if __name__ == "__main__":
    test_perplexity()
