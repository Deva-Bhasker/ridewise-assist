"""
Policy repository containing extracted and structured clauses from the 5 RideWise documents:
1. RW-POL-01: Rental Agreement & Terms (v3.0)
2. RW-POL-02: Cancellation & Refund Policy (v1)
3. RW-POL-03: Cancellation & Refund Policy (v2)
4. RW-POL-04: Late Return & Damage Penalty Schedule (v2.1)
5. RW-POL-05: EV User Guide & FAQ (v1.4)
"""

POLICIES = {
    "RW-POL-01": """
DOCUMENT: RW-POL-01 (Rental Agreement & Terms, Version 3.0, Effective 1 January 2025)
- Eligibility: Minimum 18 years old, valid driving licence for vehicle class. Single account per customer.
- KYC Status:
  * VERIFIED: Book and pick up any vehicle.
  * PENDING: Book in advance, vehicle released only after KYC is verified. If still pending at scheduled pickup time, RideWise cancels booking with 100% refund.
  * REJECTED: Cannot rent. Existing bookings cancelled by RideWise with 100% refund.
- Hubs: 7 hubs in Bengaluru (Koramangala, Indiranagar, Jayanagar, HSR Layout, Electronic City, Whitefield, Hebbal). Pick up and return to the SAME hub.
- Rental Duration: Whole hours, minimum 2 hours.
- Rental Charge Rule: The cheaper combination always applies:
  * Full 24-hour blocks charged at daily rate;
  * Remaining hours charged at hourly rate, capped at one daily rate.
- Security Deposit:
  * Bike / EV Bike: ₹1,000 for any rental.
  * Scooter / EV Scooter: ₹500 for rentals of 24 hours or more.
  * No GST on deposit. Returned to original payment method within 3 working days of vehicle return. Processed by payment gateway (not recorded in RideWise payment records). Unpaid penalties may be recovered from it.
- Customer Tiers: STANDARD, SILVER, GOLD (based on rental history; tier benefits in Annexure A of RW-POL-04).
- No-shows: Customer does not pick up vehicle within 60 minutes of scheduled start time nor cancels prior to pickup. Rental charge is NOT refunded. No extra fee.
- Customer Responsibilities: Safe riding, follow traffic laws, helmet compulsory, no lending vehicle. Customer responsible for traffic fines.
- GST: 18% added to rental charges, penalties and fees. Refunded in same proportion when refund is issued.
- Support Contact: support@ridewise.example | +91 80 4000 1234 (7:00 AM - 11:00 PM IST daily).
""",

    "RW-POL-02": """
DOCUMENT: RW-POL-02 (Cancellation & Refund Policy, Version 1, Effective 1 January 2025)
- Scope: Applies to bookings made BEFORE 1 July 2026, 00:00 IST (decided strictly by booked_at timestamp, not cancellation or rental time).
- Customer Cancellation:
  * 24 hours or more before scheduled pickup: 100% refund of rental charge.
  * 6 hours or more, but less than 24 hours before pickup: 50% refund of rental charge.
  * Less than 6 hours before pickup: No refund (0%).
- Cancellation by RideWise: 100% refund in all cases (e.g. KYC pending/rejected or vehicle unavailable).
- No-shows: No refund (0%).
- Refund Processing: Initiated within 3 working days, credited within 5 to 7 working days. GST refunded proportionally. Deposits returned in full.
""",

    "RW-POL-03": """
DOCUMENT: RW-POL-03 (Cancellation & Refund Policy, Version 2, Effective 1 July 2026, 00:00 IST)
- Scope: Replaces Version 1 for all bookings made ON OR AFTER 1 July 2026, 00:00 IST (decided strictly by booked_at timestamp).
- Customer Cancellation:
  * 48 hours or more before scheduled pickup: 100% refund of rental charge.
  * 12 hours or more, but less than 48 hours before pickup: 75% refund of rental charge.
  * 2 hours or more, but less than 12 hours before pickup: 25% refund of rental charge.
  * Less than 2 hours before pickup: No refund (0%).
- Cancellation by RideWise: 100% refund in all cases.
- No-shows: No refund (0%).
- Refund Processing: Initiated within 3 working days, credited within 5 to 7 working days. GST refunded proportionally. Deposits returned in full.
""",

    "RW-POL-04": """
DOCUMENT: RW-POL-04 (Late Return & Damage Penalty Schedule, Version 2.1, Effective 1 January 2025)
- Late Return Fee:
  * Lateness measured from scheduled return time to actual return time.
  * Each late hour or part-hour charged at 1.5 times the vehicle's hourly rate (e.g. 20 mins late = 1 hour charged; 1 hr 10 min late = 2 hours charged).
- Customer Tier Grace Periods (Annexure A):
  * STANDARD: None (0 minutes).
  * SILVER: None (0 minutes).
  * GOLD: 30 minutes grace period (up to and including 30 minutes late: ₹0 late fee).
  * CRITICAL EXCEPTION: If a GOLD return is MORE than 30 minutes late, the grace period DOES NOT reduce the lateness; full lateness is charged from minute 1.
- Hourly Rate & Late Fee (1.5x) reference:
  * Royal Enfield Classic 350 (Bike): ₹120/hr -> Late fee ₹180/hr
  * Honda CB350 (Bike): ₹130/hr -> Late fee ₹195/hr
  * KTM Duke 200 (Bike): ₹140/hr -> Late fee ₹210/hr
  * Bajaj Pulsar NS200 (Bike): ₹100/hr -> Late fee ₹150/hr
  * Yamaha FZ-S (Bike): ₹90/hr -> Late fee ₹135/hr
  * TVS Apache RTR 160 (Bike): ₹85/hr -> Late fee ₹127.50/hr
  * Honda Activa 6G (Scooter): ₹60/hr -> Late fee ₹90/hr
  * Suzuki Access 125 (Scooter): ₹60/hr -> Late fee ₹90/hr
  * TVS Jupiter (Scooter): ₹55/hr -> Late fee ₹82.50/hr
  * Yamaha Fascino 125 (Scooter): ₹55/hr -> Late fee ₹82.50/hr
  * Honda Dio (Scooter): ₹55/hr -> Late fee ₹82.50/hr
  * Ather 450X (EV scooter): ₹80/hr -> Late fee ₹120/hr
  * Ola S1 Pro (EV scooter): ₹75/hr -> Late fee ₹112.50/hr
  * TVS iQube (EV scooter): ₹70/hr -> Late fee ₹105/hr
  * Bajaj Chetak (EV scooter): ₹70/hr -> Late fee ₹105/hr
  * Revolt RV400 (EV bike): ₹90/hr -> Late fee ₹135/hr
  * Ultraviolette F77 (EV bike): ₹200/hr -> Late fee ₹300/hr
  * Oben Rorr (EV bike): ₹100/hr -> Late fee ₹150/hr
- EV Low-Battery Charging Fee:
  * Battery level at return below 10%: ₹150 flat fee per rental.
  * 10% or above: No fee (Exactly 10% is not below 10%, so ₹0 fee).
  * This fee is in addition to any late return fee on the same rental.
- Damage Assessment & Claim Statuses:
  * OPEN: Damage reported; assessment or review in progress. Customer NOT charged yet.
  * CHARGED: Assessed cost confirmed and charged. Customer pays assessed cost + 18% GST.
  * DISPUTED: Customer has disputed claim; under review. NOT charged until resolved.
  * WAIVED: RideWise decided not to charge (₹0).
  * Lost keys: Treated as damage and charged at replacement cost.
- GST: All penalties attract 18% GST.
""",

    "RW-POL-05": """
DOCUMENT: RW-POL-05 (EV User Guide & FAQ, Version 1.4)
- Electric fleet models: Ather 450X (3.7 kWh), Ola S1 Pro (4.0 kWh), TVS iQube (3.4 kWh), Bajaj Chetak (3.2 kWh), Revolt RV400 (3.24 kWh), Oben Rorr (4.4 kWh), Ultraviolette F77 (7.1 kWh).
- Before riding: Check dashboard battery. Every EV leaves hub with at least 80% charge.
- Charging: Free charging at any RideWise hub. Home charging allowed using supplied cable with properly earthed 15A socket.
- Breakdown: Call +91 80 4000 1234. Free towing if vehicle fault; recovery charge if user ran out of charge due to negligence.
- Battery Return: Return to same hub. <10% incurs ₹150 low-battery fee.
"""
}

def search_policy_docs(query: str) -> str:
    query_lower = query.lower()
    matches = []
    for doc_id, text in POLICIES.items():
        # Match keywords in document
        keywords = [k for k in query_lower.split() if len(k) > 2]
        if any(kw in text.lower() for kw in keywords):
            matches.append(text)
    if matches:
        return "\n\n".join(matches)
    # If no keyword matched, return general terms & penalty schedule
    return f"{POLICIES['RW-POL-01']}\n\n{POLICIES['RW-POL-04']}"
