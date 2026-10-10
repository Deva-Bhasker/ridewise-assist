import os
import re
from openai import OpenAI
from src.config import ENDPOINT, API_KEY, MODEL_NAME
from src import db
from src.policies import search_policy_docs

client = OpenAI(
    base_url=ENDPOINT,
    api_key=API_KEY
)

def run_conversation(role: str, customer_id: str, history: list, user_message: str):
    """
    Executes role-bounded, verified conversation using dynamic context injection
    against the NeoStats LLM endpoint.
    """
    sources = []
    data_context = ""

    # 1. Gather Role-Based Data Context (Strict Access Control)
    if role == "Customer":
        # Strictly pull ONLY this customer's data
        profile = db.get_customer_profile(customer_id)
        bookings = db.get_customer_bookings(customer_id)
        payments = db.get_customer_payments(customer_id)
        damages = db.get_customer_damages(customer_id)

        data_context = f"""
AUTHENTICATED CUSTOMER DATA (STRICT ENFORCEMENT FOR {customer_id}):
- Profile: {profile}
- Bookings: {bookings}
- Payments & Refunds: {payments}
- Damage Reports: {damages}
"""
        sources.append(f"Database: Records for customer '{customer_id}'")

        system_prompt = f"""
You are RideWise Assist, the AI assistant for RideWise mobility rentals.
CURRENT USER: CUSTOMER
LOGGED-IN CUSTOMER ID: {customer_id}

STRICT SECURITY & PRIVACY RULES:
1. You may ONLY discuss and disclose information belonging to customer '{customer_id}' and public RideWise policies.
2. You MUST NOT reveal or look up details for any other customer. If the user asks about someone else or internal operations, politely decline:
   "I can only access information for your account ({customer_id}) and RideWise's published customer policies."

BUSINESS RULES & CALCULATIONS:
1. Cancellation & Refunds:
   - Always check the booking's `booked_at` date!
   - Bookings made BEFORE 1 July 2026, 00:00 IST follow Policy v1 (RW-POL-02):
     * >=24 hours before pickup: 100% refund
     * 6 to <24 hours before pickup: 50% refund
     * <6 hours before pickup: 0% refund
   - Bookings made ON OR AFTER 1 July 2026, 00:00 IST follow Policy v2 (RW-POL-03):
     * >=48 hours before pickup: 100% refund
     * 12 to <48 hours before pickup: 75% refund
     * 2 to <12 hours before pickup: 25% refund
     * <2 hours before pickup: 0% refund
   - Cancellation by RideWise (e.g. KYC not verified): Always 100% refund regardless of timing.
   - No-show (failure to collect within 60 mins without cancelling): 0% refund.
2. Late Return Penalty (RW-POL-04):
   - 1.5x hourly rate for every late hour or part of an hour (e.g. 15 mins late counts as 1 full late hour).
   - Tiers & Grace Period (Annexure A):
     * STANDARD / SILVER: 0 minutes grace period.
     * GOLD: 30 minutes grace period (<= 30 mins late = ₹0 fee).
     * CAUTION: If a GOLD member is MORE than 30 minutes late, the grace period does NOT reduce lateness; full lateness is charged from minute 1.
3. EV Low-Battery Fee (RW-POL-04 / RW-POL-05):
   - Battery level at return below 10%: Flat ₹150 charging fee.
   - 10% or above: ₹0 fee (exactly 10% is not below 10%).
   - Separate from late return fee; both can apply to the same rental.
4. Damage Claims:
   - OPEN: Under review; customer not charged yet.
   - CHARGED: Assessed cost charged (+ 18% GST).
   - DISPUTED: Under review; NOT charged until resolved.
   - WAIVED: Not charged (₹0).
5. GST: 18% GST applies to all rental charges, penalties, and damage costs. When a refund is issued, GST is refunded in the same proportion.
6. TRANSPARENCY: Always cite document codes (e.g. RW-POL-01, RW-POL-03, RW-POL-04) and show mathematical calculation steps.
"""

    else:  # Support Agent Role
        # Support agent has fleet and operational visibility
        booking_match = re.search(r'\b(B-\d{4})\b', user_message, re.IGNORECASE)
        fleet_match = any(hub.lower() in user_message.lower() for hub in ["koramangala", "indiranagar", "jayanagar", "hsr", "electronic city", "whitefield", "hebbal"])
        
        specific_booking_data = ""
        if booking_match:
            bid = booking_match.group(1).upper()
            bdetails = db.get_agent_booking_details(bid)
            specific_booking_data = f"\nSPECIFIC BOOKING DETAILS FOR {bid}:\n{bdetails}\n"
            sources.append(f"Database: Booking Details for '{bid}'")

        fleet_summary = db.get_fleet_summary()
        damage_summary = db.get_damage_reports_summary()

        data_context = f"""
OPERATIONAL DATA (SUPPORT AGENT ACCESS):
{specific_booking_data}
- Fleet Summary by Hub & Status: {fleet_summary}
- Recent Damage Reports & Claims: {damage_summary[:15]}
"""
        sources.append("Database: Operational Fleet Summary & Damage Reports")

        system_prompt = """
You are RideWise Assist, an operations assistant for RideWise SUPPORT AGENTS and hub operations staff.
CURRENT USER: SUPPORT AGENT

DIRECTIVES:
1. Provide operational information across RideWise hubs, vehicles, customer bookings, and damage claims.
2. Provide transparent, verified answers citing specific booking IDs, vehicle IDs, and policy documents (RW-POL-01 to RW-POL-05).
3. If assisting with customer disputes or charges, calculate the exact breakdown (rental charge, late fees, low battery fees, assessed damage costs, and 18% GST).
"""

    # 2. Gather Relevant Policy Context
    policy_context = search_policy_docs(user_message)
    sources.append("Policy Documents (RW-POL-01 to RW-POL-05)")

    # 3. Assemble Messages
    context_block = f"""
RELEVANT RIDEWISE POLICIES:
{policy_context}

DATA RECORDS:
{data_context}
"""

    messages = [
        {"role": "system", "content": f"{system_prompt}\n\n{context_block}"}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # 4. Call NeoStats-hosted LLM
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.1
    )

    answer = response.choices[0].message.content
    return answer, sources
