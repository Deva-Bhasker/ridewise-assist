import sqlite3
import os
from typing import Dict, Any, List, Optional

# Check for database in data/ or current directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "ridewise.db")
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(BASE_DIR, "ridewise.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------- CUSTOMER ROLE (STRICT ACCESS CONTROL) -----------------

def get_customer_profile(customer_id: str) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT customer_id, full_name, email, phone, city, date_of_birth,
                   kyc_status, customer_tier, created_at
            FROM customers WHERE customer_id = ?
        """, (customer_id,))
        row = cursor.fetchone()
        return dict(row) if row else {"error": f"Customer '{customer_id}' not found."}

def get_customer_bookings(customer_id: str) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.booking_id, b.vehicle_id, v.model, v.vehicle_type, v.hub_name,
                   v.hourly_rate, v.daily_rate,
                   b.booked_at, b.scheduled_start, b.scheduled_end,
                   b.actual_return_at, b.cancelled_at, b.booking_status, b.return_battery_pct
            FROM bookings b
            LEFT JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            WHERE b.customer_id = ?
            ORDER BY b.booked_at DESC
        """, (customer_id,))
        return [dict(r) for r in cursor.fetchall()]

def get_customer_payments(customer_id: str) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.payment_id, p.booking_id, p.payment_type, p.amount,
                   p.gst_amount, p.payment_method, p.payment_status, p.transaction_ref,
                   p.paid_at, p.remarks
            FROM payments p
            JOIN bookings b ON p.booking_id = b.booking_id
            WHERE b.customer_id = ?
            ORDER BY p.paid_at DESC
        """, (customer_id,))
        return [dict(r) for r in cursor.fetchall()]

def get_customer_damages(customer_id: str) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.report_id, d.booking_id, d.vehicle_id, d.damage_category,
                   d.severity, d.description, d.assessed_cost, d.claim_status, d.reported_at
            FROM damage_reports d
            JOIN bookings b ON d.booking_id = b.booking_id
            WHERE b.customer_id = ?
            ORDER BY d.reported_at DESC
        """, (customer_id,))
        return [dict(r) for r in cursor.fetchall()]

# ----------------- SUPPORT AGENT ROLE (OPERATIONAL VISIBILITY) -----------------

def get_agent_booking_details(booking_id: str) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.*, c.full_name, c.customer_tier, c.phone, c.email, c.kyc_status,
                   v.model, v.vehicle_type, v.hourly_rate, v.daily_rate, v.hub_name
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            WHERE b.booking_id = ?
        """, (booking_id,))
        row = cursor.fetchone()
        if not row:
            return {"error": f"Booking '{booking_id}' not found."}
        
        cursor.execute("SELECT * FROM payments WHERE booking_id = ?", (booking_id,))
        payments = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM damage_reports WHERE booking_id = ?", (booking_id,))
        damages = [dict(r) for r in cursor.fetchall()]
        
        res = dict(row)
        res["payments"] = payments
        res["damages"] = damages
        return res

def get_fleet_summary(hub_name: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if hub_name:
            cursor.execute("""
                SELECT vehicle_id, registration_no, vehicle_type, model, hub_name, status, hourly_rate
                FROM vehicles WHERE hub_name LIKE ?
            """, (f"%{hub_name}%",))
        else:
            cursor.execute("""
                SELECT hub_name, status, count(*) as vehicle_count
                FROM vehicles GROUP BY hub_name, status
            """)
        return [dict(r) for r in cursor.fetchall()]

def get_damage_reports_summary() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT report_id, booking_id, vehicle_id, damage_category, severity,
                   assessed_cost, claim_status, reported_at
            FROM damage_reports ORDER BY reported_at DESC LIMIT 30
        """)
        return [dict(r) for r in cursor.fetchall()]
