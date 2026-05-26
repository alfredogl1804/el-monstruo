"""
Prueba de conectividad para DeepSeek API.
"""

import json
import os

import requests


def test_deepseek():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY no está configurada.")
        return

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "What is the capital of France?"}],
        "max_tokens": 50,
    }

    print(f"Testing DeepSeek API at {url}...")
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
    test_deepseek()
