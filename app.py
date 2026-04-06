import streamlit as st
import re
from datetime import datetime
import csv
import json
import io

st.set_page_config(
    page_title="Quiet Time & Creative Thinking Assessment",
    page_icon="🧠",
    layout="centered"
)

default_questions = [
    "How much quiet time do you usually get each day?",
    "Can you stay focused in a quiet environment?",
    "Does being alone help you think more clearly?",
    "Do quiet moments help you create new ideas?",
    "How refreshing is quiet time for your mind?",
    "Can you protect your quiet time from interruptions?",
    "Do you choose reflection over distractions during free time?",
    "Do you use quiet time to understand yourself better?",
    "Does silence help you solve problems more easily?",
    "Do you feel more imaginative after peaceful time alone?",
    "Do you write down ideas during calm moments?",
    "Can you create a peaceful space for yourself when needed?",
    "Do you give yourself quiet time when you feel stressed?",
    "Is your daily routine balanced with both activity and calm time?",
    "Can a quiet environment support your creativity?",
    "Do peaceful moments help you plan your future goals?",
    "Does quiet time reduce your mental tiredness?",
    "Can quiet time improve your mood during the day?",
    "Does silence help you think in a deeper way?",
    "How valuable is quiet time in your daily life?"
]

options = [
    ("Very often", 0),
    ("Often", 1),
    ("Sometimes", 2),
    ("Rarely", 3)
]


def load_questions_from_file(file_path: str):
    loaded_questions = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    loaded_questions.append(line)
    except FileNotFoundError:
        return default_questions

    return loaded_questions if loaded_questions else default_questions


def validate_name(name: str) -> bool:
    allowed_extra = {" ", "-", "'"}
    for ch in name:
        if not (ch.isalpha() or ch in allowed_extra):
            return False
    return len(name.strip()) > 0


def validate_dob(dob: str) -> bool:
    try:
        datetime.strptime(dob, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def validate_student_id(student_id: str) -> bool:
    return student_id.isdigit()


def get_psychological_state(total_score: int) -> str:
    if 0 <= total_score <= 10:
        return "Excellent quiet time balance and strong creative development."
    elif 11 <= total_score <= 20:
        return "Good creative development through quiet time."
    elif 21 <= total_score <= 30:
        return "Moderate quiet time habits; improvement is recommended."
    elif 31 <= total_score <= 40:
        return "Weak quiet time routine; creativity may be affected."
    elif 41 <= total_score <= 50:
        return "Poor quiet time balance and reduced creativity."
    else:
        return "Very poor quiet time balance; immediate improvement needed."


def result_as_txt(result_data: dict) -> str:
    return (
        f"Name: {result_data['name']}\n"
        f"Date of Birth: {result_data['dob']}\n"
        f"Student ID: {result_data['student_id']}\n"
        f"Total Score: {result_data['total_score']}\n"
        f"Psychological State: {result_data['state']}\n"
    )


def result_as_csv(result_data: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Date of Birth", "Student ID", "Total Score", "Psychological State"])
    writer.writerow([
        result_data["name"],
        result_data["dob"],
        result_data["student_id"],
        result_data["total_score"],
        result_data["state"]
    ])
    return output.getvalue()


def result_as_json(result_data: dict) -> str:
    return json.dumps(result_data, indent=4)


def survey_questions_as_txt(questions_list: list[str]) -> str:
    return "\n".join(f"{i}. {q}" for i, q in enumerate(questions_list, start=1))


questions = load_questions_from_file("questions.txt")

if "page" not in st.session_state:
    st.session_state.page = "home"

if "student_data" not in st.session_state:
    st.session_state.student_data = {}

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "total_score" not in st.session_state:
    st.session_state.total_score = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "completed" not in st.session_state:
    st.session_state.completed = False


def go_home():
    st.session_state.page = "home"


def start_new():
    st.session_state.page = "student_info"
    st.session_state.current_question = 0
    st.session_state.total_score = 0
    st.session_state.answers = {}
    st.session_state.completed = False
    st.session_state.student_data = {}


st.title("Quiet Time & Creative Thinking Assessment")

if st.session_state.page == "home":
    st.write("Please answer all questions honestly.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start New Questionnaire", use_container_width=True):
            start_new()

    with col2:
        if st.button("Load Existing Result", use_container_width=True):
            st.session_state.page = "load_result"

    st.markdown("---")
    st.subheader("Save Survey Questions")
    survey_txt = survey_questions_as_txt(questions)
    st.download_button(
        label="Download Survey Questions (.txt)",
        data=survey_txt,
        file_name="survey_questions.txt",
        mime="text/plain",
        use_container_width=True
    )

elif st.session_state.page == "student_info":
    st.subheader("Student Details")

    with st.form("student_form"):
        name = st.text_input("Surname and Given Name")
        dob = st.text_input("Date of Birth (DD/MM/YYYY)")
        student_id = st.text_input("Student ID Number")
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not validate_name(name):
            st.error("Invalid name format. Use only letters, spaces, hyphens, and apostrophes.")
        elif not validate_dob(dob):
            st.error("Invalid date format. Use DD/MM/YYYY.")
        elif not validate_student_id(student_id):
            st.error("Student ID must contain only digits.")
        else:
            st.session_state.student_data = {
                "name": name.strip(),
                "dob": dob.strip(),
                "student_id": student_id.strip()
            }
            st.session_state.page = "questionnaire"
            st.rerun()

    if st.button("Back to Home"):
        go_home()

elif st.session_state.page == "questionnaire":
    q_index = st.session_state.current_question
    total_questions = len(questions)

    st.subheader(f"Question {q_index + 1} of {total_questions}")
    st.write(questions[q_index])

    answer_key = f"question_{q_index}"
    current_value = st.session_state.answers.get(answer_key, None)

    selected_label = st.radio(
        "Choose one answer:",
        [opt[0] for opt in options],
        index=[opt[0] for opt in options].index(current_value) if current_value in [opt[0] for opt in options] else None,
        key=f"radio_{q_index}"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Back", disabled=(q_index == 0), use_container_width=True):
            if q_index > 0:
                st.session_state.current_question -= 1
                st.rerun()

    with col2:
        next_label = "Finish" if q_index == total_questions - 1 else "Next"
        if st.button(next_label, use_container_width=True):
            if selected_label is None:
                st.warning("Please choose an answer before continuing.")
            else:
                st.session_state.answers[answer_key] = selected_label

                if q_index < total_questions - 1:
                    st.session_state.current_question += 1
                    st.rerun()
                else:
                    total_score = 0
                    for i in range(total_questions):
                        saved_label = st.session_state.answers.get(f"question_{i}")
                        for label, score in options:
                            if saved_label == label:
                                total_score += score
                                break

                    st.session_state.total_score = total_score
                    st.session_state.completed = True
                    st.session_state.page = "result"
                    st.rerun()

elif st.session_state.page == "result":
    result_data = {
        "name": st.session_state.student_data["name"],
        "dob": st.session_state.student_data["dob"],
        "student_id": st.session_state.student_data["student_id"],
        "total_score": st.session_state.total_score,
        "state": get_psychological_state(st.session_state.total_score)
    }

    st.subheader("Final Result")
    st.write(f"**Name:** {result_data['name']}")
    st.write(f"**Student ID:** {result_data['student_id']}")
    st.write(f"**Date of Birth:** {result_data['dob']}")
    st.write(f"**Total Score:** {result_data['total_score']}")
    st.write(f"**Psychological State:** {result_data['state']}")

    st.markdown("---")
    st.subheader("Download Result")

    txt_data = result_as_txt(result_data)
    csv_data = result_as_csv(result_data)
    json_data = result_as_json(result_data)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download TXT",
            data=txt_data,
            file_name="questionnaire_result.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        st.download_button(
            "Download CSV",
            data=csv_data,
            file_name="questionnaire_result.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col3:
        st.download_button(
            "Download JSON",
            data=json_data,
            file_name="questionnaire_result.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("Download Survey Questions")
    survey_txt = survey_questions_as_txt(questions)
    st.download_button(
        label="Download Survey Questions (.txt)",
        data=survey_txt,
        file_name="survey_questions.txt",
        mime="text/plain"
    )

    if st.button("Return to Home"):
        go_home()
        st.rerun()

elif st.session_state.page == "load_result":
    st.subheader("Load Existing Result")

    uploaded_file = st.file_uploader(
        "Upload a saved TXT, CSV, or JSON result file",
        type=["txt", "csv", "json"]
    )

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        content = uploaded_file.read().decode("utf-8")

        st.success("File loaded successfully.")
        st.text_area("File Content", content, height=250)

        if file_extension == "json":
            try:
                parsed = json.loads(content)
                st.markdown("### Parsed Result")
                st.write(parsed)
            except json.JSONDecodeError:
                st.warning("This JSON file could not be parsed.")

    if st.button("Back to Home"):
        go_home()
        st.rerun()