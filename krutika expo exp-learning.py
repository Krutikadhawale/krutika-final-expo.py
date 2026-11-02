"""
English to Hindi Translator (no installation needed)
----------------------------------------------------
Sirf Python ki built-in libraries use hoti hain, koi pip install nahi.
Bas internet on hona chahiye.
"""

import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HISTORY_FILE = "translation_history.txt"
MAX_CHARS = 450
history = []


def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def google_translate(text):
    url = (
        "https://translate.googleapis.com/translate_a/single?client=gtx"
        "&sl=en&tl=hi&dt=t&q=" + urllib.parse.quote(text)
    )
    data = http_get_json(url)
    return "".join(part[0] for part in data[0] if part[0])


def mymemory_translate(text):
    url = (
        "https://api.mymemory.translated.net/get?q="
        + urllib.parse.quote(text)
        + "&langpair=en|hi"
    )
    data = http_get_json(url)
    return data["responseData"]["translatedText"]


def split_into_chunks(text, limit=MAX_CHARS):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks, current = [], ""
    for sentence in sentences:
        while len(sentence) > limit:
            cut = sentence.rfind(" ", 0, limit)
            cut = cut if cut != -1 else limit
            if current:
                chunks.append(current)
                current = ""
            chunks.append(sentence[:cut])
            sentence = sentence[cut:].strip()
        if len(current) + len(sentence) + 1 <= limit:
            current = (current + " " + sentence).strip()
        else:
            chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks


def translate(text):
    result = []
    for chunk in split_into_chunks(text):
        try:
            result.append(google_translate(chunk))
        except Exception:
            result.append(mymemory_translate(chunk))  # backup
    return " ".join(result)


def save_history(original, translated):
    history.append((original, translated))
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{stamp}]\n{original}\n=> {translated}\n\n")


def main():
    print("===== English to Hindi Translator =====")
    print("Commands: history | exit")

    while True:
        try:
            sentence = input("\nEnter English sentence: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nThank you!")
            break

        if not sentence:
            print("Please enter a sentence.")
            continue
        if sentence.lower() in ("exit", "quit"):
            print("Thank you!")
            break
        if sentence.lower() == "history":
            if not history:
                print("Abhi tak koi translation nahi hui.")
            for i, (src, dst) in enumerate(history, 1):
                print(f"{i}. {src}\n   => {dst}")
            continue

        try:
            result = translate(sentence)
            print("Hindi Translation:", result)
            save_history(sentence, result)
        except Exception as e:
            print("Translation fail hui (internet check karo):", e)


if __name__ == "__main__":
    main()