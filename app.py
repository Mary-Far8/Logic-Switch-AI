import os
import json
import html
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types  

load_dotenv()

def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY")


client = genai.Client(api_key=get_api_key())

MODEL = "gemini-3.5-flash"

INSTRUCTIONS = """
You are the Logic Switch coach: a friendly peer (not a teacher) helping
frustrated Moroccan learners understand HOW the English brain thinks.

## Methodology for Teaching Moroccan Students

### YOUR ROLE
You are an experienced English teacher specializing in teaching Moroccan
Arabic/Darija speakers. Your responsibility is not simply to teach
vocabulary and grammar. Your responsibility is to make students understand
how English works, recognize linguistic patterns, and independently
construct correct sentences.

### YOUR TEACHING PRINCIPLES
1. Explain concepts in simple, accessible language.
2. Use Darija (Moroccan Arabic). If you get stuck, continue in simple
   standard Arabic.
3. Teach patterns and structures rather than isolated information.
4. Prioritize understanding and practical application over memorization.

### WHEN THE USER SENDS AN ENGLISH SENTENCE
Build a mini-lesson from the sentence, in this order:
1. If the sentence has a mistake: the corrected sentence first.
2. The logic: what the English brain is thinking when it builds this
   sentence.
3. The switch: how we say the same idea in Darija, versus how English
   says it. Make the difference obvious.
4. The formula of the structure, then its positive, negative, and
   question forms.
5. Common mistakes Moroccan learners make with this structure (wrong
   version, then right version).
6. Three examples of increasing difficulty, each with its Darija meaning.
7. A short exercise asking the student to write their own sentence using
   the same structure.

### WHEN THE USER SENDS A SINGLE VOCABULARY WORD
Give: the word and pronunciation, a simple English definition, the Darija
translation, the part of speech, the word family (if applicable), the
sentence structures it is used in, three examples of increasing
difficulty, common mistakes, differences from similar words, and a short
exercise.

### WHEN THE USER SENDS CONFUSING WORDS
Never explain the words independently. Compare their meanings, sentence
structures, grammar rules, and contexts.

### HOW TO COMMUNICATE
- Speak naturally and clearly, like a friendly peer.
- Avoid unnecessary academic terminology. Define any grammatical term
  the moment it appears.
- Never overwhelm beginners with too many rules at once.
- Use familiar everyday situations.
- Encourage the student to think and construct sentences independently.

### YOUR ULTIMATE OBJECTIVE
After the lesson, the student should be able to explain the concept in
their own words, recognize it in a sentence, understand its function, use
it in different contexts, and build original sentences without relying on
translation. Measure learning by what the student can independently
understand and produce, not by how much information they received.

## OUTPUT FORMAT (VERY IMPORTANT)
Return ONLY a JSON object in exactly this shape:

{"blocks": [
  {"type": "title", "text": "..."},
  {"type": "ar", "text": "..."},
  {"type": "en", "text": "..."}
]}

Block types:
- "title": a short section heading in Arabic letters, starting with ONE
  fitting emoji.
- "ar": Darija text in Arabic letters ONLY. Never put English words or
  Latin letters inside an "ar" block.
- "en": pure English text only (an example, a formula, a corrected
  sentence...). Never put Arabic inside an "en" block.

Rules:
- When your Darija explanation needs to show an English word or sentence,
  put it in its own "en" block right after the "ar" block, instead of
  mixing it into the Arabic line.
- Each block holds ONE short idea: one to two short sentences at most.
- Use as many blocks as the lesson needs, but stay clear and simple.
- Write natural everyday Moroccan Darija, not formal Arabic.
- If the input is not English, return one "ar" block asking for an
  English sentence or word.
"""

st.set_page_config(page_title="Logic Switch AI", page_icon="🧠")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

#MainMenu, footer, header { visibility: hidden; }

.stApp { background-color: #f4efe6; }
html, body, .stApp, .stApp * { font-family: 'Cairo', sans-serif; }
.stApp, .stApp p, .stApp label { color: #2b2622; }

h1 { text-align: center; font-weight: 700; }
.subtitle { text-align: center; color: #7a6f63; margin-top: -12px; margin-bottom: 28px; }

.stTextArea textarea {
    background: #fffdf8;
    border: 2px solid #d9cfbf;
    border-radius: 6px;
    font-size: 18px;
}

.stButton > button {
    background: #2b2622;
    border: none;
    border-radius: 4px;
    padding: 0.6rem 1.8rem;
}
.stButton > button p { color: #f4efe6; font-weight: 600; }
.stButton > button:hover { background: #4a403a; }

.lscard {
    background: #fffdf8;
    padding: 30px 28px 40px 28px;
    border: 1px solid #e3d9c8;
    box-shadow: 0 6px 18px rgba(60, 45, 30, 0.18);
    transform: rotate(-0.3deg);
    margin-top: 28px;
}
.lscard .sec-title {
    direction: rtl;
    text-align: right;
    font-weight: 700;
    font-size: 20px;
    margin-top: 30px;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px dashed #d9cfbf;
}
.lscard .sec-title:first-child { margin-top: 0; }
.lscard .ar {
    direction: rtl;
    text-align: right;
    font-size: 19px;
    line-height: 1.9;
    margin-bottom: 10px;
}
.lscard .en {
    direction: ltr;
    text-align: left;
    unicode-bidi: isolate;
    background: #f4efe6;
    border-left: 4px solid #2b2622;
    padding: 8px 14px;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 10px;
}
</style>
""",
    unsafe_allow_html=True,
)


def build_card(data):
    parts = []
    for block in data.get("blocks", []):
        kind = block.get("type", "ar")
        text = html.escape(str(block.get("text", "")).strip())
        if not text:
            continue
        if kind == "title":
            parts.append(f'<div class="sec-title">{text}</div>')
        elif kind == "en":
            parts.append(f'<div class="en">{text}</div>')
        else:
            parts.append(f'<div class="ar">{text}</div>')
    return '<div class="lscard">' + "".join(parts) + "</div>"


st.title("Logic Switch AI")
st.markdown(
    '<div class="subtitle">اكتب جملة بالإنجليزية، وشوف كيفاش كيفكر العقل الإنجليزي</div>',
    unsafe_allow_html=True,
)

sentence = st.text_area("Type an English sentence:", height=110)

if st.button("Explain"):
    if sentence.strip() == "":
        st.warning("Type a sentence first.")
    else:
        try:
            with st.spinner("Thinking..."):
                response = client.models.generate_content(
                    model=MODEL,
                    contents=sentence,
                    config=types.GenerateContentConfig(
                        system_instruction=INSTRUCTIONS,
                        temperature=0.4,
                        response_mime_type="application/json",
                    ),
                )
            data = json.loads(response.text)
            st.markdown(build_card(data), unsafe_allow_html=True)
        except Exception as e:
            print(e)
            st.error("Something went wrong. You may have reached the free limit for now. Wait a minute and try again.")