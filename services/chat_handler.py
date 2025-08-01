import requests
import json


def run_custom_chat(endpoint, user_input, api_token=None, model_name='qwen:1.8b'):
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": user_input}]
    }
    try:
        resp = requests.post(endpoint, json=payload, timeout=60, stream=True)
        chunks = []
        for line in resp.iter_lines(decode_unicode=True):
            if line.strip():
                try:
                    obj = json.loads(line)
                    if "message" in obj and "content" in obj["message"]:
                        chunks.append(obj["message"]["content"])
                    elif "response" in obj:
                        chunks.append(obj["response"])
                except Exception:
                    pass
        # Only join and return the collected chunks
        return "".join(chunks) if chunks else "No response received."
    except Exception as e:
        return f"Error: {e}"
