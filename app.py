import streamlit as st
import base64
from dotenv import load_dotenv
from agent import get_gs1_agent
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
        print("✅ Opik/Agno Telemetry Initialized")

setup_opik_telemetry()

st.set_page_config(page_title="Vyuha-AI", layout="wide")
load_dotenv()

# --- CONSTANTS ---
LOGO_PATH = "/Users/electromarine/Hackathon/ProjectAlpha/Logo/Logo-Vyuha.png"
BANNER_PATH = "/Users/electromarine/Hackathon/ProjectAlpha/Logo/Banner-Vyuha.png"

# --- HELPER: IMAGE TO BASE64 FOR BACKGROUND ---
def get_base64_of_bin_file(bin_file):
    """
    Reads a binary file and returns the base64 string.
    Required because CSS cannot read local file paths directly.
    """
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

def apply_custom_style():
    # Get Base64 string of the logo for the watermark
    bin_str = get_base64_of_bin_file(LOGO_PATH)
    
    # CSS for Watermark
    # We use a pseudo-element (::before) on .stApp to apply opacity 
    # only to the background image, not the text.
    watermark_css = ""
    if bin_str:
        watermark_css = f"""
            .stApp::before {{
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: url("data:image/png;base64,{bin_str}");
                background-repeat: no-repeat;
                background-position: center;
                background-size: 40%; /* Adjust size of watermark here */
                opacity: 0.2; /* 0.2 opacity = 80% transparency */
                z-index: -1;
                background-attachment: fixed;
            }}
        """

    st.markdown(f"""
        <style>
            {watermark_css}
            .main {{ background-color: transparent; }} /* Make main bg transparent to see watermark */
            .stChatMessage {{ 
                border-radius: 15px; 
                padding: 15px; 
                margin-bottom: 10px;
                background-color: rgba(255, 255, 255, 0.85); /* Slight white backing for readability */
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }}
            section[data-testid="stSidebar"] {{ 
                background-color: #ffffff; 
                border-right: 1px solid #eee; 
            }}
            section[data-testid="stSidebar"] .stImage {{
                margin-top: 20px;
            }}
            .sidebar-text {{ font-size: 0.9rem; color: #666; }}
            h1 {{ color: #1e3a8a; font-weight: 800; }}
            .word-count {{
                font-size: 0.8rem;
                color: #666;
                text-align: right;
                margin-top: -10px;
                margin-bottom: 10px;
                font-style: italic;
            }}
        </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image(LOGO_PATH, use_container_width=True)
    except Exception:
        st.image("https://img.icons8.com/fluency/96/shield.png", width=80)

    st.title("Vyuha Control")
    st.markdown("---")
    st.subheader("🚀 Experiment Tracking")
    st.info("Connected to Opik Project: **Vyuha-AI-Prod**")
    
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = get_gs1_agent()
        st.rerun()
    
    st.markdown("---")
    st.markdown('<p class="sidebar-text"><b>System Status:</b> Agent Active ✅</p>', unsafe_allow_html=True)

# --- MAIN UI ---
apply_custom_style()

# Banner (Mid-Narrow Strip)
col1, col2, col3 = st.columns([1, 10, 1]) 
with col2:
    try:
        st.image(BANNER_PATH, use_container_width=True)
    except Exception:
        pass

st.title("🛡️ Vyuha-AI: GS-1 Expert")

if "agent" not in st.session_state:
    st.session_state.agent = get_gs1_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Check if this message has a saved word count (optional, for history)
        if "word_count" in msg:
             st.markdown(f'<p class="word-count">Words: {msg["word_count"]}</p>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask a GS-1 question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        with trace_api.get_tracer(__name__).start_as_current_span("Vyuha-Query") as span:
            span.set_attribute("user_query", prompt)
            
            response_stream = st.session_state.agent.run(prompt, stream=True)
            for chunk in response_stream:
                if hasattr(chunk, 'content') and chunk.content:
                    full_response += chunk.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            
            # --- NEW: Word Count Calculation ---
            word_count = len(full_response.split())
            st.markdown(f'<p class="word-count">Words: {word_count}</p>', unsafe_allow_html=True)
            
            span.set_attribute("final_answer", full_response)
            span.set_attribute("word_count", word_count)

    # Save content AND word count to history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": full_response,
        "word_count": word_count 
    })