import streamlit as st
from src.agent import run_conversation

st.set_page_config(page_title="RideWise Assist", page_icon="🛵", layout="wide")

# Sidebar Controls
st.sidebar.title("🛵 RideWise Assist")
st.sidebar.markdown("**NeoStats AI Engineer Intern Hackathon**")
st.sidebar.divider()

role = st.sidebar.radio("Select Role:", ["Customer", "Support Agent"], key="session_role")

customer_id = ""
if role == "Customer":
    customer_id = st.sidebar.text_input("Enter Customer ID:", value="CUST0001", help="e.g. CUST0001, CUST0002")
    st.sidebar.info(f"Active Session: Customer `{customer_id}`")
else:
    st.sidebar.info("Active Session: Support Desk Employee")

if st.sidebar.button("🔄 Start New Conversation", use_container_width=True):
    st.session_state.history = []
    st.rerun()

# State initialization
if "history" not in st.session_state:
    st.session_state.history = []

# Title
st.title(f"RideWise Assist — {role}" + (f" ({customer_id})" if customer_id else ""))
st.caption("Answers from RideWise's SQLite database and official policy documents.")

# Render Chat History
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📌 Evidence & References"):
                for src in msg["sources"]:
                    st.markdown(f"- `{src}`")

# Chat Input
if prompt := st.chat_input("Ask about bookings, rental charges, late penalties, refunds, or fleet operations..."):
    # Append and render user message
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Checking data and policy rules..."):
            try:
                # Format history for LLM
                api_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.history[:-1]]
                answer, sources = run_conversation(role, customer_id, api_history, prompt)
                st.markdown(answer)
                if sources:
                    with st.expander("📌 Evidence & References"):
                        for src in sources:
                            st.markdown(f"- `{src}`")
                st.session_state.history.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            except Exception as e:
                err_msg = f"⚠️ System Error: {str(e)}"
                st.error(err_msg)
                st.session_state.history.append({"role": "assistant", "content": err_msg})
