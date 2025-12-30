import sys
import os
import streamlit as st
import uuid
import asyncio

# --- 🛠️ PATH FIX FOR STREAMLIT CLOUD ---
# This allows imports to work when running from the root or inside the app folder
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Now import without the 'app.' prefix
from llm import call_gemini 

# --- Page Config ---
st.set_page_config(page_title="LLM Sentinel", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sentinel_logs" not in st.session_state:
    st.session_state.sentinel_logs = []

# --- Sidebar: Sentinel Dashboard ---
with st.sidebar:
    st.title("🛡️ Sentinel Control")
    st.markdown("---")
    st.markdown("### [📊 View Datadog Dashboard](https://app.datadoghq.com/dashboard/your-id)")
    st.info("Sentinel is monitoring all traffic for Fraud & Injection.")
    
    st.subheader("Live Security Feed")
    for log in reversed(st.session_state.sentinel_logs):
        color = "red" if log['risk'] == "high" else "green"
        st.markdown(f"**[{log['time']}]** :{color}[{log['status']}]")
        st.caption(f"Trace: `{log['id']}`")

# --- Main UI ---
st.title("🤖 Customer Support Chatbot")
st.caption("Protected by LLM Sentinel Security Proxy")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Sentinel scanning..."):
        # The function returns: response_text, usage, trace_id
        response_text, usage, trace_id = asyncio.run(call_gemini(prompt, is_support_chat=True))
    
    # Handle Sentinel Feedback
    is_blocked = "Access Denied" in response_text
    log_entry = {
        "time": "NOW",
        "id": trace_id,
        "status": "BLOCKED" if is_blocked else "CLEAN",
        "risk": "high" if is_blocked else "low"
    }
    st.session_state.sentinel_logs.append(log_entry)

    # Display Assistant Response
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        if is_blocked:
            st.error(response_text)
        else:
            st.markdown(response_text)
        st.caption(f"Trace ID: {trace_id}")