import streamlit as st
import os
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
    # 1. Check if we already set up (prevent double-init)
    if not trace_api.get_tracer_provider():
        
        # 2. Point to Opik Cloud (Not Localhost!)
        endpoint = "https://www.opik.ai/api/v1/otlp/v1/traces" 
        
        headers = {
            "opik-api-key": os.getenv("OPIK_API_KEY"),
            "opik-workspace": os.getenv("OPIK_WORKSPACE")
        }

        # 3. Create the Exporter
        exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
        
        tracer_provider = TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
        trace_api.set_tracer_provider(tracer_provider)
        
        # 4. Instrument Agno
        AgnoInstrumentor().instrument()
        print("✅ Opik Deep Tracing Enabled (Cloud Mode)")

# Run the setup ONCE
try:
    setup_opik_telemetry()
except Exception as e:
    print(f"⚠️ Telemetry skipped: {e}")

# FIX 1: Removed the duplicate 'setup_opik_telemetry()' call that was here

st.set_page_config(page_title="Vyuha-AI", 
                   layout="wide",
                   initial_sidebar_state="expanded")
load_dotenv()

# --- CONSTANTS & DESIGN CONFIG ---
LOGO_PATH = "./assets/Logo-Vyuha.png"
SIDEBAR_LOGO_WIDTH = 180 
THEME_COLOR = "#1C2E69"

# --- CUSTOM CSS ---
def apply_custom_style():
    st.markdown(f"""
        <style>
            .stApp, [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stBottomBlockContainer"] {{
                background-color: {THEME_COLOR} !important;
            }}
            header[data-testid="stHeader"] {{
                background-color: {THEME_COLOR} !important;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }}
            [data-testid="stHeaderActionElements"] {{ visibility: hidden; }}
            section[data-testid="stSidebar"] {{
                border-right: 1px solid rgba(255,255,255,0.1);
                box-shadow: 15px 0 25px rgba(0,0,0,0.5) !important;
                z-index: 100;
            }}
            [data-testid="stSidebarContent"] {{
                display: flex; flex-direction: column; align-items: center; text-align: center;
            }}
            h1, h2, h3, p, span, label, .stMarkdown {{ color: white !important; }}
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
    try:
        with open(LOGO_PATH, "rb") as f:
            encoded_logo = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""<div style="display: flex; justify-content: center; margin-top: 20px; margin-bottom: 10px;">
                <img src="data:image/png;base64,{encoded_logo}" width="{SIDEBAR_LOGO_WIDTH}"></div>""", 
            unsafe_allow_html=True
        )
    except:
        st.markdown("<div style='text-align:center;'>🛡️</div>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; margin-bottom: 0;'>Vyuha-AI</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    st.markdown("---")
    st.caption("System Status: Agent Active ✅")

# --- STATE MANAGEMENT (CRITICAL FIX) ---

# FIX 2: Removed the logic that deleted the agent. 
# We WANT the agent to persist so it remembers the conversation and loads faster.
if "agent" not in st.session_state: 
    with st.spinner("Initializing Supervisor Team..."):
        st.session_state.agent = get_supervisor_team()
        print("✅ Supervisor Team Loaded Successfully") 

if "messages" not in st.session_state: 
    st.session_state.messages = []

# Message Display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)
        if "word_count" in msg: 
            st.markdown(f'<p class="word-count">Words: {msg["word_count"]}</p>', unsafe_allow_html=True)

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
            
            # 1. GET FINAL ANSWER
            # While this runs, Streamlit will now correctly LOCK the input box
            with st.spinner("Writing the answer..."):
                try:
                    response = st.session_state.agent.run(prompt, stream=False)
                    final_text = response.content
                except Exception as e:
                    final_text = f"Error: {str(e)}"

            # 2. TYPEWRITER EFFECT
            for word in final_text.split(" "):
                full_res += word + " "
                # FIX 3: Enable HTML here so images render during typing if needed
                placeholder.markdown(full_res + "▌", unsafe_allow_html=True)
                time.sleep(0.02) 
            
            # Remove cursor and Final Render
            placeholder.markdown(full_res, unsafe_allow_html=True)

            # 3. WORD COUNT LOGIC
            clean_text = re.sub(r'[*#|_`]', '', full_res).strip()
            # Remove image links from word count to be accurate
            clean_text = re.sub(r'!\[.*?\]\(.*?\)', '', clean_text)
            w_count = len(clean_text.split())

            if w_count > 260:
                st.markdown(f'<p class="word-count" style="color: #ff4b4b;">Words: {w_count} (Limit Exceeded)</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p class="word-count" style="color: #00c04b;">Words: {w_count} (Perfect)</p>', unsafe_allow_html=True)

            span.set_attribute("final_answer", full_res)
    
    st.session_state.messages.append({"role": "assistant", "content": full_res, "word_count": w_count})