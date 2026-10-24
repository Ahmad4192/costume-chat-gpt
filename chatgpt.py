import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from openai import OpenAI
import uuid
import time

# Page Configuration
st.set_page_config(
    page_title="Custom ChatGPT Studio",
    page_icon="🤖",
    layout="wide"
)

# Custom Styling (Image Jaisa Card UI)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f7f9fc 0%, #edf2f7 100%);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 1.5rem;
    }
    .login-card {
        background: #ffffff;
        border-radius: 28px;
        padding: 2.5rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        text-align: center;
        max-width: 480px;
        margin: auto;
    }
    .robot-icon {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
    }
    .card-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .card-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }
    .feature-tags {
        display: flex;
        justify-content: center;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 1.5rem;
    }
    .tag {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 5px 12px;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #475569;
    }
    
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #8b5cf6, #ec4899);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# API Key Validate karne ka function
def verify_openai_key(key):
    try:
        client = OpenAI(api_key=key)
        # Ek chhota sa models list call karke check karte hain ki key kaam kar rahi hai ya nahi
        client.models.list()
        return True, "Key verified successfully!"
    except Exception as e:
        return False, str(e)

# Session States
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

PERSONAS = {
    "🌟 Helpful & Smart Assistant": "You are an intelligent, highly polite, and extremely helpful AI assistant.",
    "💻 Elite Code Expert": "You are a master software engineer. Provide clean, well-commented code and debug precisely.",
    "💼 Professional Business Advisor": "You are a top-tier business consultant. Provide strategic, structured, and practical advice.",
    "✍️ Creative Copywriter": "You are an engaging creative writer with natural tone and persuasive communication."
}

# ----------------- SCREEN 1: LOGIN & VERIFICATION -----------------
if not st.session_state.is_authenticated:
    st.markdown("""
        <div class="login-container">
            <div class="login-card">
                <div class="robot-icon">🤖</div>
                <div class="card-title">Welcome to <br>your Custom ChatGPT</div>
                <div class="card-subtitle">Plug in your OpenAI API key to unlock your personal AI studio.</div>
                <div class="feature-tags">
                    <span class="tag">⚡ Streaming replies</span>
                    <span class="tag">💾 Saved chats</span>
                    <span class="tag">🎭 Custom persona</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        api_input = st.text_input("🔑 OpenAI API Key", type="password", placeholder="sk-proj-...")
        chosen_persona = st.selectbox("🎭 Select AI Persona (Behaviour):", list(PERSONAS.keys()))
        
        if st.button("✨ Unlock the magic", use_container_width=True):
            clean_key = api_input.strip()
            if not clean_key:
                st.warning("⚠️ Meharbani karke pehle apni API Key enter karein.")
            else:
                with st.spinner("🔍 OpenAI ke sath key verify ki ja rahi hai..."):
                    is_valid, err_msg = verify_openai_key(clean_key)
                
                if is_valid:
                    st.success("✅ Zabardast! API Key bilkul theek hai aur verify ho gayi hai.")
                    time.sleep(1.2)
                    st.session_state.api_key = clean_key
                    st.session_state.selected_persona = chosen_persona
                    st.session_state.is_authenticated = True
                    
                    first_chat_id = str(uuid.uuid4())[:8]
                    st.session_state.chat_sessions[first_chat_id] = {
                        "title": "New Chat",
                        "messages": []
                    }
                    st.session_state.current_chat_id = first_chat_id
                    st.rerun()
                else:
                    st.error("❌ Invalid API Key! OpenAI ne is key ko accept nahi kiya. Dobara check karein.")

        st.caption("🔒 Aapki key browser session me safe hai aur disk par save nahi hoti.")

# ----------------- SCREEN 2: MAIN CHAT & SAVED HISTORY -----------------
else:
    with st.sidebar:
        st.header("💬 Saved Chats")
        
        if st.button("➕ New Chat", use_container_width=True):
            new_id = str(uuid.uuid4())[:8]
            st.session_state.chat_sessions[new_id] = {
                "title": f"Chat {len(st.session_state.chat_sessions) + 1}",
                "messages": []
            }
            st.session_state.current_chat_id = new_id
            st.rerun()

        st.divider()

        # Chat sessions list
        for chat_id, data in list(st.session_state.chat_sessions.items()):
            label = data["title"]
            if chat_id == st.session_state.current_chat_id:
                label = f"👉 {label}"
            if st.button(label, key=f"btn_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()

        st.divider()
        st.subheader("⚙️ Behaviour & Controls")
        active_persona = st.selectbox(
            "Current Behaviour:",
            list(PERSONAS.keys()),
            index=list(PERSONAS.keys()).index(st.session_state.selected_persona)
        )
        temperature = st.slider("Creativity (Temperature):", 0.0, 1.0, 0.7, 0.1)

        if st.button("🔒 Logout (Change Key)", use_container_width=True):
            st.session_state.is_authenticated = False
            st.session_state.api_key = ""
            st.session_state.chat_sessions = {}
            st.session_state.current_chat_id = None
            st.rerun()

    # Current Active Chat
    current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
    
    st.title(f"🤖 {current_chat['title']}")
    st.caption(f"Active Role: {active_persona}")

    # Messages show karna
    for msg in current_chat["messages"]:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(msg.content)

    # Chat Input
    if user_prompt := st.chat_input("Apna sawal yahan type karein..."):
        current_chat["messages"].append(HumanMessage(content=user_prompt))
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Title auto update karna pehle sawal par
        if len(current_chat["messages"]) == 1:
            current_chat["title"] = user_prompt[:20] + "..."

        system_prompt = SystemMessage(content=PERSONAS[active_persona])
        conversation = [system_prompt] + current_chat["messages"]

        try:
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=temperature,
                api_key=st.session_state.api_key
            )
            
            with st.chat_message("assistant"):
                placeholder = st.empty()
                streamed_text = ""
                for chunk in llm.stream(conversation):
                    streamed_text += chunk.content
                    placeholder.markdown(streamed_text + "▌")
                placeholder.markdown(streamed_text)

            current_chat["messages"].append(AIMessage(content=streamed_text))

        except Exception as e:
            st.error(f"Error: {str(e)}")