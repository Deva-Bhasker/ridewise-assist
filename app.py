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

# Dynamic Contextual Follow-up Suggestions
def get_contextual_suggestions(role: str, history: list) -> list:
    """Generates follow-up query suggestions based on conversation history."""
    if not history:
        # Default starter pills for turn 0
        if role == "Customer":
            return [
                "📋 Check my customer tier & upcoming bookings",
                "💰 Cancellation refund under Policy v2 (15 July booking)",
                "⏱️ Gold tier late return calculation rules"
            ]
        else:
            return [
                "📊 Hub-wise fleet breakdown by vehicle status",
                "🔍 Drilldown into booking B-1653",
                "⚠️ Summarize recent damage claims & disputes"
            ]

    # Analyze latest conversation topic
    last_user = history[-2]["content"].lower() if len(history) >= 2 and history[-2]["role"] == "user" else ""
    last_assistant = history[-1]["content"].lower() if history[-1]["role"] == "assistant" else ""
    combined = f"{last_user} {last_assistant}"

    if role == "Customer":
        if "cancel" in combined or "refund" in combined:
            return [
                "💳 When will the refund credit to my account?",
                "🔒 What happens to my refundable security deposit?",
                "⏰ What if I cancel less than 2 hours before pickup?"
            ]
        elif "late" in combined or "delay" in combined or "tier" in combined:
            return [
                "🔋 What fee applies if EV battery is under 10%?",
                "🛵 What is the hourly rate and late fee for Ather 450X?",
                "🛡️ Does Gold tier grace period apply if I am 35 mins late?"
            ]
        elif "booking" in combined or "vehicle" in combined or "b-" in combined:
            return [
                "❌ How much refund if I cancel this booking now?",
                "⏱️ What late fee applies if I return 1 hour late?",
                "📍 Which hub do I need to return the vehicle to?"
            ]
        elif "damage" in combined or "scratch" in combined:
            return [
                "⚖️ How do I dispute an unfair damage claim?",
                "🔑 How much is charged for a lost vehicle key?",
                "💼 Will damage costs be deducted from my deposit?"
            ]
        else:
            return [
                "🛵 What are the rental charging rules per 24 hours?",
                "🔋 Where can I charge an EV in Bengaluru?",
                "📞 How do I contact RideWise emergency support?"
            ]
    else:  # Support Agent Contextual Follow-ups
        if "damage" in combined or "claim" in combined:
            return [
                "⚖️ List only claims with status 'DISPUTED'",
                "💵 What is the repair cost for high-severity damage?",
                "📝 Look up the booking linked to the latest report"
            ]
        elif "hub" in combined or "fleet" in combined or "vehicle" in combined:
            return [
                "🔧 Which specific vehicles are in MAINTENANCE status?",
                "📍 Show vehicle availability in Koramangala hub",
                "⚡ How many EV scooters vs EV bikes are active?"
            ]
        elif "b-" in combined or "booking" in combined:
            return [
                "💰 Check payment status and gateway ref for this booking",
                "🛠️ Were any damage reports filed for this booking?",
                "⏱️ Was the vehicle returned on time or late?"
            ]
        else:
            return [
                "📊 Overview of all 7 Bengaluru hubs",
                "⚠️ Vehicles currently under maintenance",
                "📋 List recent completed bookings"
            ]

st.write("💡 **Suggested Next Steps:**")
suggestions = get_contextual_suggestions(role, st.session_state.history)
sugg_cols = st.columns(len(suggestions))

for idx, sugg_text in enumerate(suggestions):
    if sugg_cols[idx].button(sugg_text, use_container_width=True, key=f"sugg_{idx}_{len(st.session_state.history)}"):
        # Strip leading emoji for clean prompt
        clean_prompt = sugg_text
        if len(sugg_text) > 2 and sugg_text[2] == " ":
            clean_prompt = sugg_text[3:]
        st.session_state.suggested_prompt = clean_prompt

# Determine active prompt (from input or quick button)
chat_input_val = st.chat_input("Ask about bookings, rental charges, late penalties, refunds, or fleet operations...")
prompt = chat_input_val or st.session_state.suggested_prompt

if prompt:
    # Clear suggested prompt state
    st.session_state.suggested_prompt = None

    # Append user message
    st.session_state.history.append({"role": "user", "content": prompt})

    # Render and generate Assistant Response
    with st.chat_message("user"):
        st.markdown(prompt)

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

    # Instantly trigger rerun so dynamic suggestions update on a single click!
    st.rerun()
