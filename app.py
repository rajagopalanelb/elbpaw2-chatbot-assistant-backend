from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import traceback

# Load environment variables
load_dotenv()

# Force debug output before app starts
print("🔧 Debug: starting app.py")
print("🔧 OPENAI_API_KEY loaded:", bool(os.getenv("OPENAI_API_KEY")))
print("🔧 OPENAI_ASSISTANT_ID loaded:", os.getenv("OPENAI_ASSISTANT_ID"))

app = Flask(__name__)
CORS(app)

# Assign to OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json.get("message")

        if not user_input:
            print("⚠️ No message provided in request.")
            return jsonify({"error": "No message provided"}), 400

        print("🔹 User input received:", user_input)

        # Step 1: Create a new thread
        thread = openai.beta.threads.create()
        print("✅ Thread created:", thread.id)

        # Step 2: Add user message to the thread
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        print("✅ Message added to thread")

        # Step 3: Run the assistant
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )
        print("🚀 Assistant run started:", run.id)

        # Step 4: Wait for assistant run to complete
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            if run_status.status == "completed":
                print("✅ Assistant run completed")
                break
            elif run_status.status == "failed":
                print("❌ Assistant run failed:", run_status)
                return jsonify({"error": "Assistant run failed"}), 500

        # Step 5: Fetch assistant's reply
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        last_message = messages.data[0].content[0].text.value
        print("✅ Assistant reply:", last_message)

        return jsonify({"reply": last_message})

    except Exception as e:
        print("❌ Exception occurred:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
