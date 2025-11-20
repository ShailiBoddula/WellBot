import streamlit as st
import requests

# ✅ Streamlit Page Config
st.set_page_config(page_title="WellBot Chat", page_icon="💬")
st.cache_data.clear()

BACKEND_BASE = "http://127.0.0.1:8000"

# ✅ Process URL token first
params = st.query_params  # ✅ Updated

# ✅ Handle token & language from URL
if "token" in params:
    st.session_state["token"] = params["token"]

if "selected_language" not in st.session_state:
    st.session_state["selected_language"] = params.get("lang", "en")

# ✅ If still no token — stop
if "token" not in st.session_state:
    st.error("❌ Session expired. Please login again.")
    st.stop()

language = st.session_state["selected_language"]

# ✅ UI Title
st.title("🤖 WellBot — Wellness Assistant")

# ✅ Chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for i, msg in enumerate(st.session_state["messages"]):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        # Add feedback buttons for assistant messages
        if msg["role"] == "assistant":
            message_id = st.session_state.get(f"message_id_{i}")
            if message_id:
                col1, col2, col3 = st.columns([1, 1, 1])

                with col1:
                    if st.button("👍 Helpful", key=f"helpful_{i}"):
                        # Submit positive feedback
                        feedback_payload = {
                            "message_id": message_id,
                            "feedback_type": "positive"
                        }
                        headers = {
                            "Authorization": f"Bearer {st.session_state['token']}",
                            "Content-Type": "application/json"
                        }
                        try:
                            requests.post(f"{BACKEND_BASE}/feedback", json=feedback_payload, headers=headers)
                            st.success("Thank you for the feedback!")
                        except:
                            st.error("Feedback submission failed")

                with col2:
                    if st.button("👎 Not helpful", key=f"not_helpful_{i}"):
                        # Submit negative feedback
                        feedback_payload = {
                            "message_id": message_id,
                            "feedback_type": "negative"
                        }
                        headers = {
                            "Authorization": f"Bearer {st.session_state['token']}",
                            "Content-Type": "application/json"
                        }
                        try:
                            requests.post(f"{BACKEND_BASE}/feedback", json=feedback_payload, headers=headers)
                            st.success("Thank you for the feedback!")
                        except:
                            st.error("Feedback submission failed")

                with col3:
                    if st.button("💬 Comment", key=f"comment_{i}"):
                        # Show comment input
                        comment = st.text_input("Add a comment (optional)", key=f"comment_input_{i}")
                        if st.button("Submit Comment", key=f"submit_comment_{i}"):
                            feedback_payload = {
                                "message_id": message_id,
                                "feedback_type": "comment",
                                "feedback_comment": comment
                            }
                            headers = {
                                "Authorization": f"Bearer {st.session_state['token']}",
                                "Content-Type": "application/json"
                            }
                            try:
                                requests.post(f"{BACKEND_BASE}/feedback", json=feedback_payload, headers=headers)
                                st.success("Comment submitted!")
                            except:
                                st.error("Comment submission failed")

# ✅ Send message to backend
def send_message(prompt):
    token = st.session_state["token"]

    payload = {
        "message": prompt,
        "language": st.session_state["selected_language"]
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(f"{BACKEND_BASE}/chat", json=payload, headers=headers, timeout=40)

        if res.status_code == 200:
            d = res.json()
            reply = d.get("reply") or d.get("response") or "..."
            # Store message_id for feedback
            st.session_state[f"message_id_{len(st.session_state['messages'])}"] = d.get("message_id")
            return reply

        elif res.status_code == 401:
            st.error("❌ Session expired. Please login again.")
            st.stop()

        return f"⚠️ Server error {res.status_code}"

    except Exception as e:
        return f"⚠️ Connection issue: {e}"

# ✅ Input placeholder dynamically changes
placeholder_text = (
    "How can I help you?" if language == "en"
    else "मैं आपकी कैसे मदद कर सकता हूँ?"
)

prompt = st.chat_input(placeholder_text)

if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)

    reply = send_message(prompt)

    with st.chat_message("assistant"):
        st.write(reply)

    st.session_state["messages"].append({"role": "assistant", "content": reply})
    st.rerun()

# ✅ Language Switch UI
st.markdown("---")
st.subheader("🌐 भाषा / Language")

col1, col2 = st.columns(2)

with col1:
    if st.button("🇬🇧 English"):
        st.session_state["selected_language"] = "en"
        st.query_params["lang"] = "en"  # ✅ update URL param
        st.rerun()

with col2:
    if st.button("🇮🇳 हिंदी"):
        st.session_state["selected_language"] = "hi"
        st.query_params["lang"] = "hi"  # ✅ update URL param
        st.rerun()
