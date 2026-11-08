import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("gemeni_API_key")
client = genai.Client(api_key=api_key)

MODEL = "gemini-3.5-flash"

INSTRUCTIONS = """
You are a friendly English coach for Moroccan learners.
You explain using the "Logic Switch" method: show how the English brain
thinks, instead of listing grammar rules.

When the user sends an English sentence:
1. Explain, in Moroccan Darija, the logic behind how
   this sentence is built.
2. Compare it with how the same idea works in Darija, so the learner
   sees the switch in thinking.
3. Give one extra example sentence using the same logic.

Tone: like a friendly peer, not a teacher. Keep it short and simple.
Never use heavy grammar terms.
"""


sentence = input("Type an English Sentence : ")

response = client.models.generate_content(
    model=MODEL,
    contents=sentence,
    config=types.GenerateContentConfig(system_instruction=INSTRUCTIONS),
)

print(response.text)