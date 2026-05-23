import urllib.request
import urllib.error
import json
import time

key = "AIzaSyA17aHqVroPl-3AA5fFsD8wmpsnC08oCx8"

models = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-latest",
    "gemini-pro",
]

for m in models:
    print(f"Testing {m}...", end=" ")
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
        payload = {"contents": [{"parts": [{"text": "say hi"}]}]}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            print(f"OK -> {text[:50]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")[:200]
        print(f"ERROR {e.code}: {body}")
    except Exception as e:
        print(f"ERROR: {e}")
    time.sleep(2)
