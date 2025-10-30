import streamlit as st
import time
from datetime import datetime
import requests

API_URL = "http://127.0.0.1:8000/chat"

# Cấu hình trang
st.set_page_config(
    page_title="Chat AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh để giống ChatGPT
st.markdown("""
<style>
    /* Tổng thể */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #202123;
    }
    
    [data-testid="stSidebar"] .element-container {
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* Nút trong sidebar */
    [data-testid="stSidebar"] button {
        background-color: transparent;
        border: 1px solid #565869;
        color: #ffffff;
        border-radius: 6px;
        width: 100%;
        padding: 12px;
        margin: 4px 0;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: #40414f;
        border-color: #565869;
    }
    
    /* Chat messages */
    .user-message {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 12px;
        margin: 16px 0;
        border-left: 4px solid #19c37d;
    }
    
    .ai-message {
        background-color: #f7f7f8;
        padding: 16px 20px;
        border-radius: 12px;
        margin: 16px 0;
        border-left: 4px solid #ab68ff;
    }
    
    .message-header {
        font-weight: 600;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .user-header {
        color: #19c37d;
    }
    
    .ai-header {
        color: #ab68ff;
    }
    
    .message-content {
        color: #202123;
        line-height: 1.6;
        font-size: 16px;
    }
    
    /* Welcome screen */
    .welcome-container {
        text-align: center;
        padding: 60px 20px;
    }
    
    .welcome-title {
        font-size: 32px;
        font-weight: 600;
        color: #202123;
        margin-bottom: 16px;
    }
    
    .welcome-subtitle {
        font-size: 16px;
        color: #666;
        margin-bottom: 40px;
    }
    
    .example-prompt {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .example-prompt:hover {
        border-color: #10a37f;
        background-color: #f9f9f9;
    }
    
    .example-prompt h4 {
        color: #202123;
        margin-bottom: 8px;
    }
    
    .example-prompt p {
        color: #666;
        font-size: 14px;
    }
    
    /* Input area */
    .stTextInput input {
        border-radius: 12px;
        border: 1px solid #d1d5db;
        padding: 16px;
    }
    
    .stTextInput input:focus {
        border-color: #10a37f;
        box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.1);
    }
    
    /* Main chat area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    /* Model selector */
    .stSelectbox {
        margin-bottom: 20px;
    }
    
    /* Ẩn footer và menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Timestamp */
    .timestamp {
        font-size: 12px;
        color: #999;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

if 'chat_title' not in st.session_state:
    st.session_state.chat_title = "Cuộc trò chuyện mới"

# Hàm tạo ID cho chat
def generate_chat_id():
    return f"chat_{int(time.time() * 1000)}"

# Hàm lưu chat hiện tại
def save_current_chat():
    if st.session_state.current_chat_id and len(st.session_state.messages) > 0:
        chat_title = st.session_state.messages[0]['content'][:30] + "..." if len(st.session_state.messages) > 0 else "Cuộc trò chuyện mới"
        
        chat_data = {
            'id': st.session_state.current_chat_id,
            'title': chat_title,
            'messages': st.session_state.messages.copy(),
            'timestamp': datetime.now().strftime("%H:%M - %d/%m/%Y")
        }
        
        # Cập nhật hoặc thêm mới
        existing_index = None
        for i, chat in enumerate(st.session_state.chat_history):
            if chat['id'] == st.session_state.current_chat_id:
                existing_index = i
                break
        
        if existing_index is not None:
            st.session_state.chat_history[existing_index] = chat_data
        else:
            st.session_state.chat_history.insert(0, chat_data)

# Hàm bắt đầu chat mới
def start_new_chat():
    save_current_chat()
    st.session_state.messages = []
    st.session_state.current_chat_id = generate_chat_id()
    st.session_state.chat_title = "Cuộc trò chuyện mới"

# Hàm load chat
def load_chat(chat_id):
    save_current_chat()
    for chat in st.session_state.chat_history:
        if chat['id'] == chat_id:
            st.session_state.messages = chat['messages'].copy()
            st.session_state.current_chat_id = chat_id
            st.session_state.chat_title = chat['title']
            break

# Sidebar
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Nút tạo chat mới
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        start_new_chat()
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📝 Lịch sử chat")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Hiển thị lịch sử chat
    if st.session_state.chat_history:
        for chat in st.session_state.chat_history:
            is_current = chat['id'] == st.session_state.current_chat_id
            button_label = f"{'📌 ' if is_current else '💬 '}{chat['title']}"
            
            if st.button(button_label, key=chat['id'], use_container_width=True):
                load_chat(chat['id'])
                st.rerun()
            
            # Hiển thị timestamp
            st.markdown(f"<p style='font-size: 11px; color: #999; margin-left: 12px; margin-top: -8px;'>{chat['timestamp']}</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: #999; font-size: 14px; text-align: center;'>Chưa có lịch sử chat</p>", unsafe_allow_html=True)

# Main content
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # Header
    st.markdown("### 💬 Chat AI")
    st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #e5e5e5;'>", unsafe_allow_html=True)
    
    # Hiển thị welcome screen nếu chưa có tin nhắn
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="welcome-container">
            <h1 class="welcome-title" style="color: black;">Chào bạn! Tôi có thể giúp gì cho bạn?</h1>
            <p class="welcome-subtitle">Hãy bắt đầu cuộc trò chuyện bằng cách gửi tin nhắn</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Example prompts
        st.markdown("#### 💡 Gợi ý câu hỏi")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("📚 Giải thích về trí tuệ nhân tạo", use_container_width=True):
                user_message = "Giải thích về trí tuệ nhân tạo"
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                st.rerun()
            
            if st.button("🍳 Gợi ý món ăn cho bữa tối", use_container_width=True):
                user_message = "Gợi ý món ăn cho bữa tối"
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                st.rerun()
        
        with col_b:
            if st.button("✨ Viết một bài thơ về mùa xuân", use_container_width=True):
                user_message = "Viết một bài thơ về mùa xuân"
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                st.rerun()
            
            if st.button("🗺️ Giúp tôi lên kế hoạch du lịch", use_container_width=True):
                user_message = "Giúp tôi lên kế hoạch du lịch"
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                st.rerun()
    
    # Hiển thị tin nhắn
    else:
        # Container cho messages
        messages_container = st.container()
        
        with messages_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        <div class="message-header user-header">
                            👤 Bạn
                        </div>
                        <div class="message-content">
                            {message['content']}
                        </div>
                        <div class="timestamp">{message.get('timestamp', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="ai-message">
                        <div class="message-header ai-header">
                            🤖 AI Assistant
                        </div>
                        <div class="message-content">
                            {message['content']}
                        </div>
                        <div class="timestamp">{message.get('timestamp', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    user_input = st.chat_input("Nhập tin nhắn của bạn...")
    
    if user_input:
        # Khởi tạo chat ID nếu chưa có
        if st.session_state.current_chat_id is None:
            st.session_state.current_chat_id = generate_chat_id()
        
        # Thêm tin nhắn người dùng
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        # send request
        response = requests.post(API_URL, json={"message": user_input})
        
        # Tạo phản hồi AI
        with st.spinner("Đang suy nghĩ..."):
            ai_response = response.json().get("response", "Xin lỗi, tôi chưa có phản hồi.")
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
        
        # Lưu chat
        save_current_chat()
        
        # Rerun để cập nhật UI
        st.rerun()

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #999; font-size: 12px;'>Được phát triển với ❤️ bằng Streamlit</p>", unsafe_allow_html=True)