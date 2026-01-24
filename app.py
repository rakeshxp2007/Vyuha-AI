
import streamlit as st
from dotenv import load_dotenv
from agent import get_gs1_agent  # Import your agent factory
from opentelemetry import trace as trace_api
from openinference.instrumentation.agno import AgnoInstrumentor


# --- OPIK & TELEMETRY SETUP ---
from opik import track, opik_context
from openinference.instrumentation.agno import AgnoInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

@st.cache_resource
def setup_opik_telemetry():
    # Check if we already have a tracer to avoid "Duplicate Tracer" errors
    provider = trace_api.get_tracer_provider()
    
    # If the provider is just the default "Proxy", it means it hasn't been set up yet
    if not hasattr(provider, "add_span_processor"):
        tracer_provider = TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
        trace_api.set_tracer_provider(tracer_provider)
        AgnoInstrumentor().instrument()
        print("✅ Opik/Agno Telemetry Initialized")

# Initialize immediately
setup_opik_telemetry()

st.set_page_config(page_title="Vyuha-AI GS-1", layout="wide")

load_dotenv()

def apply_custom_style():
    st.markdown("""
        <style>
            .main { background-color: #f8f9fa; }
            .stChatMessage { 
                border-radius: 15px; 
                padding: 15px; 
                margin-bottom: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            section[data-testid="stSidebar"] { 
                background-color: #ffffff; 
                border-right: 1px solid #eee; 
            }
            .sidebar-text { font-size: 0.9rem; color: #666; }
            h1 { color: #1e3a8a; font-weight: 800; }
        </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Component (The Judging Command Center)
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=80)
    st.title("Vyuha Control")
    st.markdown("---")
    
    st.subheader("🚀 Experiment Tracking")
    st.info("Connected to Opik Project: **Vyuha-AI-Prod**")
    
    # Adding a Reset Button (Critical for demos)
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        # Re-initializing the agent clears its internal history too
        st.session_state.agent = get_gs1_agent()
        st.rerun()
    
    st.markdown("---")
    st.markdown('<p class="sidebar-text"><b>System Status:</b> Agent Active ✅</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-text"><b>Subject:</b> General Studies - 1</p>', unsafe_allow_html=True)

# 4. Main Chat UI
apply_custom_style()
st.title("🛡️ Vyuha-AI: GS-1 Expert")

if "agent" not in st.session_state:
    st.session_state.agent = get_gs1_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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
            span.set_attribute("final_answer", full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})