import os
import json
import traceback
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import streamlit as st
from src.mcqgenerator.utils import read_file
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain

# Load environment variables
load_dotenv()
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Load response JSON template
with open('D:/quize/backend/ai/MCQ-Generator-master/Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

st.title("🧠 AI Quiz Generator & Saver")

# === Streamlit Form ===
with st.form("quiz_form"):
    admin_id = st.text_input("👤 Admin ID (e.g., 22MIS7043)")  # updated to string
    title = st.text_input("📘 Quiz Title")
    uploaded_file = st.file_uploader("📄 Upload Book (PDF or TXT)")
    page_from = st.number_input("📄 Page From", min_value=1)
    page_to = st.number_input("📄 Page To", min_value=page_from)
    mcq_count = st.number_input("🔢 No. of MCQs", min_value=3, max_value=50)
    subject = st.text_input("📚 Subject", value="General")
    tone = st.text_input("🎯 Difficulty Level", value="Simple")
    duration = st.number_input("⏱ Duration (minutes)", min_value=1, value=30)
    start_at = st.text_input("🕒 Start Time (YYYY-MM-DD HH:MM)")
    end_at = st.text_input("🕒 End Time (YYYY-MM-DD HH:MM)")
    student_ids = st.text_area("🧑‍🎓 Student IDs (comma-separated)")
    submit = st.form_submit_button("🚀 Generate and Save")

# === On Submit ===
if submit:
    if not all([admin_id, title, uploaded_file, start_at, end_at, student_ids]):
        st.error("❌ Please complete all required fields.")
    else:
        try:
            st.info("📖 Reading uploaded file...")
            text = read_file(uploaded_file)
            lines = text.split("\n")
            selected_text = "\n".join(lines[int(page_from) - 1:int(page_to)])

            st.info("🤖 Generating MCQs...")
            response = generate_evaluate_chain({
                'text': selected_text,
                'number': mcq_count,
                'subject': subject,
                'tone': tone,
                'response_json': json.dumps(RESPONSE_JSON)
            })

            quiz_raw = response.get("quiz", {})

            if isinstance(quiz_raw, str):
                try:
                    quiz_raw = json.loads(quiz_raw)
                except Exception as e:
                    st.error(f"❌ Failed to parse stringified quiz JSON: {e}")
                    st.stop()

            if not isinstance(quiz_raw, dict):
                st.error("⚠️ MCQ data is not valid. Expected dict.")
                st.json(quiz_raw)
                st.stop()

            # Prepare data
            quiz_data = []
            for key in sorted(quiz_raw.keys(), key=lambda x: int(x)):
                q = quiz_raw[key]
                if not all(k in q for k in ["mcq", "options", "correct"]):
                    st.warning(f"⚠️ Skipping invalid question at key {key}")
                    continue

                opts = q["options"]
                options = [opts.get("a", ""), opts.get("b", ""), opts.get("c", ""), opts.get("d", "")]
                correct_index = {"a": 1, "b": 2, "c": 3, "d": 4}.get(q["correct"].lower(), -1)

                if correct_index == -1:
                    st.warning(f"⚠️ Invalid correct answer format at key {key}")
                    continue

                quiz_data.append({
                    "question": q["mcq"],
                    "options": options,
                    "correct": correct_index
                })

            if not quiz_data:
                st.error("❌ No valid questions to save.")
                st.stop()

            df = pd.DataFrame(quiz_data)
            st.success("✅ MCQs Generated!")
            st.dataframe(df)

            # === Save to PostgreSQL ===
            st.info("💾 Saving to PostgreSQL...")
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            cursor = conn.cursor()

            # Save Quiz with adminId
            cursor.execute("""
                INSERT INTO "Quiz" (title, book, "pageFrom", "pageTo", duration, "startAt", "endAt", subject, level, count, status, "adminId")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE', %s)
                RETURNING id
            """, (
                title,
                uploaded_file.name,
                page_from,
                page_to,
                duration,
                start_at,
                end_at,
                subject,
                tone,
                mcq_count,
                admin_id  # ✅ as string
            ))
            quiz_id = cursor.fetchone()[0]

            # Save Questions
            for q in quiz_data:
                cursor.execute("""
                    INSERT INTO "Question" (quizId, body, options, correct, "aiGenerated")
                    VALUES (%s, %s, %s, %s, true)
                """, (
                    quiz_id,
                    q["question"],
                    q["options"],
                    q["correct"]
                ))

            # Save Eligible Students
            for sid in [s.strip() for s in student_ids.split(",") if s.strip()]:
                cursor.execute("""
                    INSERT INTO "QuizEligibility" (quizId, "studentId")
                    VALUES (%s, %s)
                """, (quiz_id, sid))

            conn.commit()
            cursor.close()
            conn.close()

            st.success(f"🎉 Quiz saved successfully! ID: {quiz_id}")

        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error(f"❌ Error saving to database: {e}")
