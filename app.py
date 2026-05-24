import streamlit as st
import fitz
from groq import Groq

# ─── Configuration ───────────────────────────────────────────────
client = Groq(api_key="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")  # Get free key at console.groq.com
MODEL = "llama-3.3-70b-versatile"

# ─── Helper Function ──────────────────────────────────────────────
def ask_ai(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )
    return response.choices[0].message.content

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
            border-radius: 8px;
            margin-top: 0.5rem;
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
    # Extract PDF text
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    for page in pdf:
        full_text += page.get_text()

    # Use up to 4000 characters for better context
    study_text = full_text[:4000]

    with st.expander("📄 View Extracted Text", expanded=False):
        st.write(study_text if study_text.strip() else "No text could be extracted.")

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
                st.error(f"Error: {e}")

    st.divider()

    # ─── 2. Q&A ──────────────────────────────────────────────────
    st.subheader("❓ Ask a Question")
    question = st.text_input("Type your doubt here...", placeholder="e.g. What is photosynthesis?")
    if st.button("Get Answer"):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Finding the answer..."):
                try:
                    prompt = f"""You are a helpful study assistant.
Answer the student's question using the study material provided.
If the answer isn't in the material, answer from your general knowledge and mention that.

Study Material:
{study_text}

Question: {question}"""
                    result = ask_ai(prompt)
                    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()

    # ─── 3. Flashcards ───────────────────────────────────────────
    st.subheader("🃏 Flashcards")
    if st.button("Generate Flashcards"):
        with st.spinner("Creating flashcards..."):
            try:
                prompt = f"""You are a helpful study assistant.
Create 5 flashcards from the study material below.
Format each flashcard exactly like this:

Q: [question]
A: [answer]

Study Material:
{study_text}"""
                result = ask_ai(prompt)
                cards = result.strip().split("\n\n")
                for i, card in enumerate(cards):
                    lines = card.strip().split("\n")
                    if len(lines) >= 2:
                        question_text = lines[0].replace("Q:", "").strip()
                        answer_text = lines[1].replace("A:", "").strip()
                        with st.expander(f"🃏 Card {i+1}: {question_text}"):
                            st.success(f"**Answer:** {answer_text}")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    # ─── 4. Quiz ─────────────────────────────────────────────────
    st.subheader("📝 Quiz Generator")
    if st.button("Generate Quiz"):
        with st.spinner("Creating your quiz..."):
            try:
                prompt = f"""You are a helpful study assistant.
Create 5 multiple choice questions (MCQs) from the study material.
Format each question EXACTLY like this:

Q1: [question]
A) [option]
B) [option]
C) [option]
D) [option]
Answer: [correct letter]

Study Material:
{study_text}"""
                result = ask_ai(prompt)

                # Store quiz in session state so answers can be revealed
                st.session_state["quiz"] = result

            except Exception as e:
                st.error(f"Error: {e}")

    # Display quiz if generated
    if "quiz" in st.session_state:
        quiz_text = st.session_state["quiz"]
        questions = quiz_text.strip().split("\n\n")
        for i, q_block in enumerate(questions):
            lines = [l.strip() for l in q_block.strip().split("\n") if l.strip()]
            if not lines:
                continue
            st.markdown(f"**{lines[0]}**")  # Question
            for line in lines[1:-1]:        # Options
                st.write(line)
            answer_line = lines[-1] if lines[-1].startswith("Answer") else ""
            with st.expander("🔍 Show Answer"):
                st.success(answer_line if answer_line else "See above")
            st.write("")

    st.divider()

    # ─── 5. Key Terms ────────────────────────────────────────────
    st.subheader("🔑 Key Terms & Definitions")
    if st.button("Extract Key Terms"):
        with st.spinner("Extracting key terms..."):
            try:
                prompt = f"""You are a helpful study assistant.
Extract 8 important key terms from the study material and give a simple one-line definition for each.
Format exactly like this:

Term: [term]
Definition: [simple definition]

Study Material:
{study_text}"""
                result = ask_ai(prompt)
                terms = result.strip().split("\n\n")
                for term_block in terms:
                    lines = [l.strip() for l in term_block.strip().split("\n") if l.strip()]
                    if len(lines) >= 2:
                        term = lines[0].replace("Term:", "").strip()
                        definition = lines[1].replace("Definition:", "").strip()
                        st.markdown(f"**🔹 {term}**")
                        st.write(f"{definition}")
                        st.write("")
            except Exception as e:
                st.error(f"Error: {e}")

else:
    # ─── Empty State ─────────────────────────────────────────────
    st.info("👆 Upload a PDF to get started! You can summarize notes, ask questions, generate quizzes, flashcards, and more.")
    st.markdown("""
    ### ✨ Features
    - 🧠 **AI Summary** — Get concise bullet-point summaries
    - ❓ **Q&A** — Ask any doubt from your notes
    - 🃏 **Flashcards** — Auto-generated study cards
    - 📝 **Quiz** — MCQ quiz with answers
    - 🔑 **Key Terms** — Important terms with definitions
    """)