import streamlit as st
from src.agent import run_conversation
from src import db

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
    st.sidebar.info("Active Session: **Support Desk Employee**")

if st.sidebar.button("🔄 Start New Conversation", use_container_width=True):
    st.session_state.history = []
    st.session_state.suggested_prompt = None
    st.rerun()

# State initialization
if "history" not in st.session_state:
    st.session_state.history = []
if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = None

# Title & Header
st.title(f"RideWise Assist — {role}" + (f" ({customer_id})" if customer_id else ""))
st.caption("AI-powered assistant bridging RideWise SQLite operational records and legal policy documents.")

# Live Status Header Badge for Customer Role
if role == "Customer" and customer_id:
    profile = db.get_customer_profile(customer_id)
    if "error" not in profile:
        bookings = db.get_customer_bookings(customer_id)
        latest_b = bookings[0] if bookings else None
        
        tier = profile.get('customer_tier', 'STANDARD')
        kyc = profile.get('kyc_status', 'UNKNOWN')
        name = profile.get('full_name', 'Valued Customer')
        city = profile.get('city', 'Bengaluru')
        
        # Color coding badges
        tier_color = "🟡" if tier == "GOLD" else ("⚪" if tier == "SILVER" else "🔵")
        kyc_icon = "✅" if kyc == "VERIFIED" else ("⏳" if kyc == "PENDING" else "❌")
        
        latest_info = "No active bookings"
        if latest_b:
            b_status = latest_b.get('booking_status', 'N/A')
            status_desc = {"UPC": "Upcoming", "ONG": "Ongoing", "CMP": "Completed", "CNL_U": "Cancelled", "CNL_S": "Cancelled by RideWise", "NSH": "No-show"}.get(b_status, b_status)
            latest_info = f"Booking **{latest_b.get('booking_id')}** ({latest_b.get('model')}) — *{status_desc}*"

        st.info(
            f"👤 **Customer:** `{name}` ({city}) | "
            f"{tier_color} **Tier:** `{tier}` | "
            f"{kyc_icon} **KYC:** `{kyc}` | "
            f"🛵 **Latest:** {latest_info}"
        )
    else:
        st.warning(f"⚠️ {profile.get('error')}")
    st.divider()

# Operational KPI Header for Support Agent
if role == "Support Agent":
    fleet_rows = db.get_fleet_summary()
    total_active = sum(r['vehicle_count'] for r in fleet_rows if r['status'] == 'ACTIVE')
    total_maint = sum(r['vehicle_count'] for r in fleet_rows if r['status'] == 'MAINTENANCE')
    total_ret = sum(r['vehicle_count'] for r in fleet_rows if r['status'] == 'RETIRED')
    total_fleet = total_active + total_maint + total_ret

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Fleet", f"{total_fleet} vehicles")
    col2.metric("Active & Available", f"{total_active} vehicles", delta="Ready to rent")
    col3.metric("Under Maintenance", f"{total_maint} vehicles", delta="-Maintenance pool", delta_color="inverse")
    col4.metric("Retired Vehicles", f"{total_ret} vehicles")
    st.divider()

# Render Chat History
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📌 Evidence & References"):
                for src in msg["sources"]:
                    st.markdown(f"- `{src}`")

# Quick-Prompt Starter Buttons (Preset Keywords for Evaluator)
st.write("💡 **Quick Test Prompts:**")
quick_cols = st.columns(3)

if role == "Customer":
    if quick_cols[0].button("📋 Check Tier & Bookings", use_container_width=True):
        st.session_state.suggested_prompt = "What is my current customer tier, and what is the status of my latest booking?"
    if quick_cols[1].button("💰 Policy v2 Cancellation", use_container_width=True):
        st.session_state.suggested_prompt = "I booked a vehicle on 15 July 2026. If I cancel 10 hours before pickup, what refund do I get under Policy v2?"
    if quick_cols[2].button("⏱️ Gold Tier Late Return", use_container_width=True):
        st.session_state.suggested_prompt = "I am a Gold tier member. If I return 20 minutes late vs 35 minutes late, how is my late fee calculated?"
else:  # Support Agent Quick Prompts
    if quick_cols[0].button("📊 Hub Fleet Breakdown", use_container_width=True):
        st.session_state.suggested_prompt = "Give me a vehicle count breakdown across all 7 hubs by status."
    if quick_cols[1].button("🔍 Drilldown Booking B-1653", use_container_width=True):
        st.session_state.suggested_prompt = "Look up full booking, vehicle, and payment details for booking B-1653."
    if quick_cols[2].button("⚠️ Recent Damage Claims", use_container_width=True):
        st.session_state.suggested_prompt = "Summarize recent damage reports and list which ones are currently DISPUTED vs CHARGED."

# Determine active prompt (from input or quick button)
chat_input_val = st.chat_input("Ask about bookings, rental charges, late penalties, refunds, or fleet operations...")
prompt = chat_input_val or st.session_state.suggested_prompt

if prompt:
    # Reset suggested prompt so it doesn't re-trigger on next rerun
    st.session_state.suggested_prompt = None

    # Render User Message
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Checking database records and policy documents..."):
            try:
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
