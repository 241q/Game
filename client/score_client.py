import json
import threading
import urllib.request

API_URL = "http://127.0.0.1:8000/scores"


def submit_score(player, score):
    print("hi i submitted")

    def send():
        data = json.dumps({"player": player, "score": score}).encode("utf-8")
        request = urllib.request.Request(
            API_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(request, timeout=3).close()
        except OSError as error:  # server down, timeout, etc.
            print(f"Could not save score: {error}")

    threading.Thread(target=send, daemon=True).start()