import requests
import json

def run_custom_chat(endpoint, message):
    payload = {
        "model": "phi3",
        "messages": [{"role": "user", "content": message}]
    }
    try:
        resp = requests.post(endpoint, json=payload, timeout=60, stream=True)
        # If Ollama streams JSON lines, we need to collect and parse each one
        chunks = []
        for line in resp.iter_lines(decode_unicode=True):
            if line.strip():
                try:
                    obj = json.loads(line)
                    # For chat, usually 'message'->'content' holds the latest chunk
                    if "message" in obj and "content" in obj["message"]:
                        chunks.append(obj["message"]["content"])
                    elif "response" in obj:
                        chunks.append(obj["response"])
                except Exception:
                    # Ignore non-JSON lines
                    pass
        return "".join(chunks) if chunks else resp.text
    except Exception as e:
        return f"Error: {e}"
