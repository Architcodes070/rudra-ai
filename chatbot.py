import streamlit as st
from openai import OpenAI
import os
import time
import json
from dotenv import load_dotenv

# load env
load_dotenv()

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Rudra AI", page_icon="🔥", layout="centered")

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Rudra AI"
    }
)
    


# ---------------- SESSION INIT ----------------
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}
    st.session_state.current_chat = "Chat 1"

# ---------------- USER DATA ----------------
USER_FILE = "user_data.json"

def load_user():
    try:
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

user_data = load_user()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🔥 Rudra AI")

    chat_names = list(st.session_state.chats.keys())

    if st.session_state.current_chat not in chat_names:
        st.session_state.current_chat = chat_names[0]

    current_index = chat_names.index(st.session_state.current_chat)

    selected_chat = st.selectbox("Chats", chat_names, index=current_index)
    st.session_state.current_chat = selected_chat

    if st.button("➕ New Chat"):
        new_name = f"Chat {len(chat_names) + 1}"
        st.session_state.chats[new_name] = []
        st.session_state.current_chat = new_name
        st.rerun()

    style = st.radio("Response Style", ["Short", "Detailed"])
    uploaded_file = st.file_uploader("Upload File", type=["txt", "png", "jpg", "jpeg"])

# ---------------- SYSTEM PROMPT ----------------
def get_system_prompt():
    return f"""
You are Rudra AI.
Created by Archit Tiwari.

User Name: {user_data.get("name", "")}
Goal: {user_data.get("goal", "")}
"""

# ---------------- UI ----------------
st.title("🔥 Rudra AI")
st.caption("Not just AI. Controlled Intelligence.")

messages = st.session_state.chats[st.session_state.current_chat]

# ---------------- FILE ----------------
if uploaded_file is not None:
    if uploaded_file.type.startswith("image"):
        st.image(uploaded_file)
        messages.append({"role": "user", "content": "Describe this image"})
    else:
        content = uploaded_file.read().decode("utf-8", errors="ignore")
        messages.append({"role": "user", "content": content[:2000]})

# ---------------- CHAT ----------------
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask Rudra AI...")

if user_input:
    if style == "Short":
        user_input += " Answer briefly."
    else:
        user_input += " Explain in detail."

    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role": "system", "content": get_system_prompt()}] + messages
        )

        reply = response.choices[0].message.content

    except Exception:
        reply = "Something went wrong. Try again."

    messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.write(reply)