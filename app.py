import streamlit as st
from src.questions import EXIT_QUESTIONS
from src.llm import get_llm
from src.voice import speak, listen
from src.summarizer import generate_summary
from src.storage import save_interview


st.set_page_config(
    page_title="Agentic AI Exit Interview (Voice + Text)",
    layout="wide"
)

st.title("🎤🤖 Agentic AI Exit Interview (Voice + Text)")


try:
    llm = get_llm()
except Exception as e:
    st.error(f"LLM Initialization Error: {e}")
    st.stop()


defaults = {
    "step": 0,
    "responses": {},
    "transcript": [],
    "follow_up_pending": False,
    "current_question": EXIT_QUESTIONS[0],
    "last_spoken_question": None,
    "pending_voice_answer": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value



def get_follow_up(question, answer):
    prompt = f"""
You are an HR exit interviewer.

Original question:
{question}

Employee answer:
{answer}

If the answer is vague or too short, ask ONE concise follow-up question.
If the answer is sufficiently detailed, reply exactly:
NO_FOLLOW_UP
"""
    result = llm.invoke(prompt).content.strip()
    return None if result == "NO_FOLLOW_UP" else result



def process_answer(answer):
    question = st.session_state.current_question

    
    st.session_state.transcript.append({
        "role": "agent",
        "message": question
    })
    st.session_state.transcript.append({
        "role": "employee",
        "message": answer
    })


    if st.session_state.follow_up_pending:
        base_question = EXIT_QUESTIONS[st.session_state.step]

        st.session_state.responses[base_question]["follow_up"] = {
            "question": question,
            "answer": answer
        }

        st.session_state.follow_up_pending = False
        st.session_state.step += 1

    else:
        base_question = EXIT_QUESTIONS[st.session_state.step]

        st.session_state.responses[base_question] = {
            "answer": answer
        }

        follow_up = get_follow_up(base_question, answer)

        if follow_up:
            st.session_state.follow_up_pending = True
            st.session_state.current_question = follow_up
            st.session_state.last_spoken_question = None
        
            st.session_state.pending_voice_answer = ""
        
            voice_key = f"voice_edit_box_{st.session_state.step}"
            if voice_key in st.session_state:
                del st.session_state[voice_key]
        
            return

        st.session_state.step += 1

    
    if st.session_state.step < len(EXIT_QUESTIONS):
        st.session_state.current_question = EXIT_QUESTIONS[
            st.session_state.step
        ]

   
    st.session_state.last_spoken_question = None
    st.session_state.pending_voice_answer = ""



if st.session_state.step < len(EXIT_QUESTIONS):

    question = st.session_state.current_question

    question_number = min(
        st.session_state.step + 1,
        len(EXIT_QUESTIONS)
    )

    title = f"Question {question_number}"
    if st.session_state.follow_up_pending:
        title += " (Follow-up)"

    st.subheader(title)
    st.write(question)

    
    if st.session_state.last_spoken_question != question:
        with st.spinner("🔊 AI is speaking the question..."):
            speak(question)
        st.session_state.last_spoken_question = question

    
    col1, col2 = st.columns(2)


    with col1:
        st.markdown("### ⌨️ Type Your Answer")

        typed_answer = st.text_area(
            "Type your answer",
            key=f"typed_{st.session_state.step}"
        )

        if st.button("Submit Typed Answer"):
            if typed_answer.strip():
                process_answer(typed_answer.strip())
                st.rerun()


    with col2:
        st.markdown("### 🎤 Speak Your Answer")

        
        if st.button("🎤 Start Voice Recording"):
            with st.spinner("Listening... Please speak now."):
                voice_answer = listen()

            if voice_answer.startswith("[Speech Recognition Error]"):
                st.error(voice_answer)
            else:
                st.session_state.pending_voice_answer = voice_answer
                st.rerun()

        
        if st.session_state.pending_voice_answer:

            st.success("Speech recognized successfully.")

            edited_voice_answer = st.text_area(
                "Review or edit the recognized text:",
                value=st.session_state.pending_voice_answer,
                key=f"voice_edit_box_{st.session_state.step}"
            )

            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("✅ Use This Voice Answer"):
                    if edited_voice_answer.strip():
                        process_answer(edited_voice_answer.strip())
                        st.rerun()

            with col_b:
                if st.button("🔄 Record Again"):
                    st.session_state.pending_voice_answer = ""
                    st.rerun()


else:
    st.success("✅ Interview Completed!")

    with st.spinner("Generating AI Summary..."):
        summary = generate_summary(
            llm,
            st.session_state.responses
        )

        save_path = save_interview(
            st.session_state.responses,
            st.session_state.transcript,
            summary
        )

    st.subheader("🧠 AI Summary")
    st.write(summary)

    st.subheader("📋 Structured Responses")
    st.json(st.session_state.responses)

    st.subheader("💬 Full Transcript")
    st.json(st.session_state.transcript)

    st.info(f"Interview saved to: {save_path}")