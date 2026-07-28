from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key = os.getenv("HACKCLUB_API_KEY"),
    base_url = "https://ai.hackclub.com/proxy/v1"
)

models = {
    "1": "anthropic/claude-opus-4.8",
    "2": "anthropic/claude-opus-4.8-fast",
    "3": "qwen/qwen3.7-max",
    "4": "google/gemini-3.5-flash"
}


print("Available Models:")
print("1. Claude Opus 4.8")
print("2. Claude Opus 4.8 Fast")
print("3. Qwen 3.7 Max")
print("4. Gemini 3.5 Flash")

choice = input("\nChoose model: ")

if choice not in models:
    print("Invalid choice!")
    exit()

MODEL = models[choice]

prompt = input("Ask anything: ")

response = client.chat.completions.create(
    model = MODEL,
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print("\n=========================")
print(f"Model: {MODEL}")
print("============================")
print(response.choices[0].message.content)