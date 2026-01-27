import streamlit as st
import re
import base64
import time
from dotenv import load_dotenv
from agent import get_gs1_agent, get_supervisor_team
from opentelemetry import trace as trace_api
from openinference.instrumentation.agno import AgnoInstrumentor

# --- OPIK & TELEMETRY SETUP ---
from opik import track, opik_context
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

@st.cache_resource
def setup_opik_telemetry():
    provider = trace_api.get_tracer_provider()
    if not hasattr(provider, "add_span_processor"):
        tracer_provider = TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
        trace_api.set_tracer_provider(tracer_provider)
        AgnoInstrumentor().instrument()

setup_opik_telemetry()
st.set_page_config(page_title="Vyuha-AI", 
                   layout="wide",
                   initial_sidebar_state="expanded")
load_dotenv()

# --- CONSTANTS & DESIGN CONFIG ---
LOGO_PATH = "./assets/Logo-Vyuha.png"

# 🛠️ MANUAL DESIGN OVERRIDES
SIDEBAR_LOGO_WIDTH = 180   # Change this to resize the centered sidebar logo
THEME_COLOR = "#1C2E69"    # Unified Navy Blue (Your matched color)


# --- CUSTOM CSS: THE "HARD-CENTER" ENGINE ---
def apply_custom_style():
    st.markdown(f"""
        <style>
            /* 1. Global Backgrounds (Body, Sidebar, Header, and Bottom Bar) */
            .stApp, 
            [data-testid="stSidebar"], 
            [data-testid="stHeader"], 
            [data-testid="stBottomBlockContainer"] {{
                background-color: {THEME_COLOR} !important;
            }}
            
            /* 2. Unified Header (Fixes the black/white top bar) */
            header[data-testid="stHeader"] {{
                background-color: {THEME_COLOR} !important;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }}

            /* Hide 'Deploy', 'Rerun', and 'GitHub' icons specifically */
            [data-testid="stHeaderActionElements"] {{
                visibility: hidden;
            }}

            /* 3. Restore the Deep Sidebar Shadow */
            section[data-testid="stSidebar"] {{
                border-right: 1px solid rgba(255,255,255,0.1);
                box-shadow: 15px 0 25px rgba(0,0,0,0.5) !important;
                z-index: 100;
            }}

            /* 4. Force Centering for Sidebar Content */
            [data-testid="stSidebarContent"] {{
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
            }}

            /* 5. Chat Input and Typography */
            h1, h2, h3, p, span, label, .stMarkdown {{ 
                color: white !important; 
            }}
            
            [data-testid="stChatInput"] {{
                background-color: {THEME_COLOR} !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
            }}

            .stChatMessage {{ 
                background-color: rgba(255, 255, 255, 0.05) !important;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            .word-count {{ color: #00d4ff !important; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# --- SIDEBAR ---
with st.sidebar:
    # Centered Logo using Base64 for absolute control
    try:
        with open(LOGO_PATH, "rb") as f:
            encoded_logo = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; margin-top: 20px; margin-bottom: 10px;">
                <img src="data:image/png;base64,{encoded_logo}" width="{SIDEBAR_LOGO_WIDTH}">
            </div>
            """, 
            unsafe_allow_html=True
        )
    except:
        st.markdown("<div style='text-align:center;'>🛡️</div>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; margin-bottom: 0;'>Vyuha-AI</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Centered Button using column-trick
    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    st.markdown("---")
    st.caption("System Status: Agent Active ✅")

# --- STATE MANAGEMENT ---
if "agent" in st.session_state:
    del st.session_state.agent 

# 2. Load the Supervisor Team
if "agent" not in st.session_state: 
    st.session_state.agent = get_supervisor_team()
    print("✅ Supervisor Team Loaded Successfully") 

# 3. Initialize Chat History (Keep this!)
if "messages" not in st.session_state: 
    st.session_state.messages = []

# Message Display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "word_count" in msg: st.markdown(f'<p class="word-count">Words: {msg["word_count"]}</p>', unsafe_allow_html=True)

# Input Logic
if prompt := st.chat_input("Enter your UPSC GS-1 query..."):
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): 
        st.markdown(prompt)

    # 2. Assistant Logic
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_res = ""
        
        with trace_api.get_tracer(__name__).start_as_current_span("Vyuha-Query") as span:
            
            # 1. GET FINAL ANSWER (Non-Streaming)
            with st.spinner("Supervisor is auditing the answer..."):
                try:
                    response = st.session_state.agent.run(prompt, stream=False)
                    final_text = response.content
                except Exception as e:
                    final_text = f"Error: {str(e)}"

            # 2. TYPEWRITER EFFECT (Text Only)
            for word in final_text.split(" "):
                full_res += word + " "
                placeholder.markdown(full_res + "▌")
                time.sleep(0.02) 
            
            # Remove cursor at the end
            placeholder.markdown(full_res)

            # 3. RENDER IMAGE (Runs ONCE after typing is done)
            # This prevents the app from trying to reload the image 200 times
            image_match = re.search(r'!\[.*?\]\((.*?)\)', full_res)
            if image_match:
                image_url = image_match.group(1)
                st.image(image_url, caption="Generated Diagram", use_container_width=True)

            # 4. WORD COUNT LOGIC
            clean_text = full_res.replace(prompt, "").strip()
            clean_text = re.sub(r'[*#|_`]', '', clean_text)
            w_count = len(clean_text.split())

            if w_count > 260:
                st.markdown(f'<p class="word-count" style="color: #ff4b4b;">Words: {w_count} (Limit Exceeded)</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p class="word-count" style="color: #00c04b;">Words: {w_count} (Perfect)</p>', unsafe_allow_html=True)

            span.set_attribute("final_answer", full_res)
    
    st.session_state.messages.append({"role": "assistant", "content": full_res, "word_count": w_count})