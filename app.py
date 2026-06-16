import os
import time
import streamlit as st
import fitz
from groq import Groq

# ─── Configuration ───────────────────────────────────────────────
# Set your key as environment variable: export GROQ_API_KEY="your_key"
# OR paste directly only for local testing (never share/upload this file)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "paste_your_key_here_for_local_testing_only")
client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

# ─── Helper Function with Retry ───────────────────────────────────
def ask_ai(prompt: str, max_tokens: int = 2048) -> str:
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                st.warning(f"Rate limit hit. Retrying in 10 seconds... (attempt {attempt + 1}/3)")
                time.sleep(10)
            else:
                raise e

# ─── Page Config ─────────────────────────────────────────────────
st.set_page_config(page_title="StudyMate AI", page_icon="📚", layout="centered")

# ─── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
    <style>
        .main { background-color: #f9f9fb; }
        .stButton>button {
            background-color: #4F46E5;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1.5em;
            font-weight: bold;
            border: none;
        }
        .stButton>button:hover { background-color: #4338CA; }
        .result-box {
            background-color: #ffffff;
            border-left: 4px solid #4F46E5;
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin-top: 0.5rem;
            color: #1a1a2e;
        }
        .pdf-info {
            background-color: #EEF2FF;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
            color: #4F46E5;
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────
st.title("📚 StudyMate AI")
st.caption("Your smart study assistant — upload notes, get summaries, ask questions & take quizzes!")
st.divider()

# ─── File Upload ─────────────────────────────────────────────────
uploaded_file = st.file_uploader("📎 Upload your PDF notes", type=["pdf"])

if uploaded_file:

    # ─── Extract PDF Text ────────────────────────────────────────
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    for page in pdf:
        full_text += page.get_text()

    # ─── Handle Scanned / Empty PDF ──────────────────────────────
    if not full_text.strip():
        st.error("❌ No text could be extracted. This might be a scanned or image-based PDF. Please upload a digital/text-based PDF.")
        st.stop()

    # ─── Show PDF Info ───────────────────────────────────────────
    st.markdown(
        f'<div class="pdf-info">📄 {len(pdf)} page(s) · {len(full_text):,} characters extracted · ✅ {uploaded_file.name}</div>',
        unsafe_allow_html=True
    )

    # ─── Warn if text is truncated ───────────────────────────────
    MAX_CHARS = 8000
    if len(full_text) > MAX_CHARS:
        st.warning(f"⚠️ Your PDF has {len(full_text):,} characters. Only the first {MAX_CHARS:,} are sent to AI for processing.")

    study_text = full_text[:MAX_CHARS]

    # ─── Clear old quiz if new file uploaded ─────────────────────
    if "last_file" not in st.session_state or st.session_state["last_file"] != uploaded_file.name:
        st.session_state.pop("quiz", None)
        st.session_state["last_file"] = uploaded_file.name

    with st.expander("📄 View Extracted Text", expanded=False):
        st.write(study_text)

    st.divider()

    # ─── 1. Summary ──────────────────────────────────────────────
    st.subheader("🧠 AI Summary")
    if st.button("Generate Summary"):
        with st.spinner("Summarizing your notes..."):
            try:
                prompt = f"""You are a helpful study assistant.
Summarize the following study material in clear, simple bullet points.
Keep it concise and easy to understand for a student.

Study Material:
{study_text}"""
                result = ask_ai(prompt)
                st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error: {e}")

    st.divider()

    # ─── 2. Q&A ──────────────────────────────────────────────────
    st.subheader("❓ Ask a Question")
    question = st.text_input("Type your doubt here...", placeholder="e.g. What is photosynthesis?")
    if st.button("Get Answer"):
        if not question.strip():
            st.warning("⚠️ Please enter a question first.")
        else:
            with st.spinner("Finding the answer..."):
                try:
                    prompt = f"""You are a helpful study assistant.
Answer the student's question using the study material provided.
If the answer isn't in the material, answer from your general knowledge and clearly mention that.

Study Material:
{study_text}

Question: {question}"""
                    result = ask_ai(prompt)
                    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    st.divider()

    # ─── 3. Flashcards ───────────────────────────────────────────
    st.subheader("🃏 Flashcards")
    if st.button("Generate Flashcards"):
        with st.spinner("Creating flashcards..."):
            try:
                prompt = f"""You are a helpful study assistant.
Create 5 flashcards from the study material below.
Format each flashcard EXACTLY like this with a blank line between each:

Q: [question]
A: [answer]

Study Material:
{study_text}"""
                result = ask_ai(prompt)
                cards = result.strip().split("\n\n")
                found = 0
                for i, card in enumerate(cards):
                    lines = card.strip().split("\n")
                    if len(lines) >= 2:
                        question_text = lines[0].replace("Q:", "").strip()
                        answer_text = lines[1].replace("A:", "").strip()
                        if question_text and answer_text:
                            with st.expander(f"🃏 Card {found + 1}: {question_text}"):
                                st.success(f"**Answer:** {answer_text}")
                            found += 1
                if found == 0:
                    st.warning("Could not parse flashcards. Try again.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    st.divider()

    # ─── 4. Quiz ─────────────────────────────────────────────────
    st.subheader("📝 Quiz Generator")
    if st.button("Generate Quiz"):
        with st.spinner("Creating your quiz..."):
            try:
                prompt = f"""You are a helpful study assistant.
Create 5 multiple choice questions (MCQs) from the study material.
Format each question EXACTLY like this with a blank line between each question:

Q1: [question]
A) [option]
B) [option]
C) [option]
D) [option]
Answer: [correct letter]

Study Material:
{study_text}"""
                result = ask_ai(prompt)
                st.session_state["quiz"] = result
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # ─── Display Quiz ────────────────────────────────────────────
    if "quiz" in st.session_state:
        quiz_text = st.session_state["quiz"]
        questions = quiz_text.strip().split("\n\n")
        for i, q_block in enumerate(questions):
            lines = [l.strip() for l in q_block.strip().split("\n") if l.strip()]
            if not lines or len(lines) < 3:
                continue
            st.markdown(f"**{lines[0]}**")
            for line in lines[1:-1]:
                st.write(line)
            answer_line = lines[-1] if lines[-1].startswith("Answer") else "See above"
            with st.expander("🔍 Show Answer"):
                st.success(answer_line)
            st.write("")

    st.divider()

    # ─── 5. Key Terms ────────────────────────────────────────────
    st.subheader("🔑 Key Terms & Definitions")
    if st.button("Extract Key Terms"):
        with st.spinner("Extracting key terms..."):
            try:
                prompt = f"""You are a helpful study assistant.
Extract 8 important key terms from the study material and give a simple one-line definition for each.
Format EXACTLY like this with a blank line between each term:

Term: [term]
Definition: [simple definition]

Study Material:
{study_text}"""
                result = ask_ai(prompt)
                terms = result.strip().split("\n\n")
                found = 0
                for term_block in terms:
                    lines = [l.strip() for l in term_block.strip().split("\n") if l.strip()]
                    if len(lines) >= 2:
                        term = lines[0].replace("Term:", "").strip()
                        definition = lines[1].replace("Definition:", "").strip()
                        if term and definition:
                            st.markdown(f"**🔹 {term}**")
                            st.write(definition)
                            st.write("")
                            found += 1
                if found == 0:
                    st.warning("Could not extract key terms. Try again.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ─── Empty State ─────────────────────────────────────────────────
else:
    st.info("👆 Upload a PDF to get started!")
    st.markdown("""
    ### ✨ Features
    - 🧠 **AI Summary** — Concise bullet-point summaries
    - ❓ **Q&A** — Ask any doubt from your notes
    - 🃏 **Flashcards** — Auto-generated study cards
    - 📝 **Quiz** — MCQ quiz with hidden answers
    - 🔑 **Key Terms** — Important terms with definitions
    """)
    st.markdown("""
    ### 🚀 How to Use
    1. Upload any **digital PDF** (textbook, notes, slides)
    2. Click any feature button
    3. AI generates content instantly!

    > ⚠️ Scanned/image PDFs are not supported — only digital text PDFs work.
    """)