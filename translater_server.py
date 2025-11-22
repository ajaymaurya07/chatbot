from flask import Flask, request, jsonify
from flask_cors import CORS
from langdetect import detect
from googletrans import Translator
import requests

app = Flask(__name__)
CORS(app)

translator = Translator()

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

# Save user's language permanently per session
user_lang_memory = {}


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    sender = data.get("sender", "user")

    # Detect Language (ONLY when it's a normal text message)

    if user_message.startswith("/"):

        # Payload click → don't detect language → use memory
        lang = user_lang_memory.get(sender, "en")
        print("⚡ Payload clicked → Using saved language:", lang)

    else:
        # Detect fresh language from text
        try:
            lang = detect(user_message)
        except:
            lang = "en"

        # Save detected language for future payload clicks
        user_lang_memory[sender] = lang

    print("🌐 User language:", lang)


    # Translate Hindi → English (Only if Hindi)

    if lang == "hi" and not user_message.startswith("/"):
        try:
            translated_message = translator.translate(user_message, src="hi", dest="en").text
        except:
            translated_message = user_message
    else:
        translated_message = user_message

    print("➡️ Message to Rasa:", translated_message)


    # Send message to Rasa

    try:
        rasa_response = requests.post(
            RASA_URL,
            json={"sender": sender, "message": translated_message},
            timeout=10
        ).json()

    except Exception as e:
        print("❌ Rasa Error:", e)
        return jsonify([{"text": "⚠️ Unable to reach chatbot."}])


    # Translate Rasa Response → Hindi if needed

    final_response = []

    for msg in rasa_response:
        text = msg.get("text", "")

        if lang == "hi" and text:
            try:
                text = translator.translate(text, src="en", dest="hi").text
            except:
                pass

        msg["text"] = text

        # Translate buttons also
        if "buttons" in msg:
            new_buttons = []
            for b in msg["buttons"]:
                title = b["title"]
                payload = b["payload"]

                if lang == "hi":
                    try:
                        title = translator.translate(title, src="en", dest="hi").text
                    except:
                        pass

                new_buttons.append({"title": title, "payload": payload})

            msg["buttons"] = new_buttons

        final_response.append(msg)

    return jsonify(final_response)


if __name__ == "__main__":
    app.run(port=5050)
