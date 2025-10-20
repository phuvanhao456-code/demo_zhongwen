import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import requests

# -------------------- KHỞI TẠO MÔI TRƯỜNG --------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="Gemini Chat", layout="wide")
st.title("Tsinghua No. 70 ChatAI: Learning Chinese Vocabulary")


# -------------------- HÀM LẤY IP NGƯỜI DÙNG --------------------
def get_user_ip():
    try:
        ip = requests.get("https://api.ipify.org").text
        return ip
    except:
        return "unknown"


user_ip = get_user_ip()
st.caption(f"🌐 Địa chỉ IP của bạn: `{user_ip}`")


# -------------------- HÀM SINH PHẢN HỒI CỦA CHATBOT --------------------
def generate_bot_response(user_input):
    try:
        conversations = [
            {"role": msg["role"], "parts": [msg["content"]]}
            for msg in st.session_state.chat_history
        ]

        conversations.append({"role": "user", "parts": [user_input]})

        model = genai.GenerativeModel("gemini-2.0-flash")
        chat = model.start_chat(history=conversations)
        response = chat.send_message(user_input)

        return response.text
    except Exception as e:
        return f"Đã xảy ra lỗi: {str(e)}"


# -------------------- HÀM LƯU LỊCH SỬ CHAT --------------------
def save_chat_history(ip):
    filename = f"chat_history_{ip}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(st.session_state.chat_history, f, ensure_ascii=False, indent=2)


# -------------------- HÀM TẢI LỊCH SỬ CHAT --------------------
def load_chat_history(ip):
    filename = f"chat_history_{ip}.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


# -------------------- KHỞI TẠO SESSION STATE --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history(user_ip)


# -------------------- HIỂN THỊ LỊCH SỬ CHAT --------------------
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -------------------- Ô NHẬP CÂU HỎI --------------------
prompt = st.chat_input("Nhập câu hỏi của bạn...")

if prompt:
    # Lưu tin nhắn người dùng
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Hiển thị tin nhắn người dùng
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi hàm phản hồi
    response = generate_bot_response(prompt)

    # Hiển thị phản hồi chatbot
    with st.chat_message("assistant"):
        st.markdown(response)

    # Lưu phản hồi vào lịch sử
    st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Lưu file theo IP
    save_chat_history(user_ip)


# -------------------- NÚT XÓA LỊCH SỬ --------------------
if st.button("🗑️ Xóa lịch sử chat"):
    st.session_state.chat_history = []
    filename = f"chat_history_{user_ip}.json"
    if os.path.exists(filename):
        os.remove(filename)
    st.rerun()
