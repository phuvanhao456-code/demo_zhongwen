import streamlit as st 
import google.generativeai as genai
from dotenv import load_dotenv
import os 
import json 

# KHởi tạo môi trường
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Thiết lập cấu hình trang 
st.set_page_config(page_title="Gemini chat", layout="wide")

# Tiêu đề của ứng dụng
st.title("Tsinghua No. 70 ChatAI: Learning Chinese Vocabulary")

# Tạo hàm xử lý phản hồi của chatbot
def generate_bot_response(user_input):
    try:
        # Tạo conversation history từ session state
        conversations = [
            {"role": msg["role"], "parts": [msg["content"]]}
            for msg in st.session_state.chat_history 
        ] 
        
        # Thêm câu hỏi của user vào coversations 
        conversations.append({"role": "user", "parts": [user_input]})
        # Khởi tạo model Gemini
        model = genai.GenerativeModel("gemini-2.0-flash")
        chat = model.start_chat(history=conversations)
        
        # Truyền câu hỏi của user vào model 
        # response = model.generate_content(user_input)
        response = chat.send_message(user_input)
        
        return response.text
    except Exception as e:
        return f"Đã xảy ra lỗi: {str(e)}"
    

# Hàm lưu lịch sử chat vào file JSON
def save_chat_history():
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.chat_history, f, ensure_ascii=False, indent=2)
        

# Hàm tải lịch sử chat từ file JSON
def load_chat_history():
    try:
        with open("chat_history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Khởi tạo session state để lưu lịch sử chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history()
    
# Hiển thị lịch sử chat 
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# Tạo ô input cho user nhập câu hỏi
prompt = st.chat_input("Nhập câu hỏi của bạn...")

if prompt:
    # Lưu câu hỏi của user vào lịch sử chat
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    
    # Hiển thị tin nhắn của user 
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Gọi hàm generate_bot_response
    response = generate_bot_response(prompt) 
    
    # Hiển thị phản hồi chat bot
    with st.chat_message("assistant"):
        st.markdown(response)
        
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Lưu lịch sử chat
    save_chat_history()
    
# Nút xóa lịch sử chat
if st.button("Xóa lịch sử chat"):
    st.session_state.chat_history = []
    if os.path.exists("chat_history.json"):
        os.remove("chat_history.json")
    st.rerun()

