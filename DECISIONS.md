# Architecture Decisions & Engineering Report — RideWise Assist

### 1. What were your three most important design decisions, and why?
1. **Hard Code-Enforced Role-Based Access Control (RBAC):**
   Rather than relying purely on LLM system prompt instructions to maintain data confidentiality, data access tools programmatically scope queries to `session_customer_id`. A user in the Customer role physically cannot invoke tools or execute queries retrieving another customer's data or internal fleet operational metrics.
2. **Explicit Policy Versioning and Cutoff Logic:**
   Cancellation and refund calculations depend strictly on the `booked_at` timestamp (< 1 July 2026 for Policy v1 vs >= 1 July 2026 for Policy v2). By structuring policy clauses and rules around the booking timestamp, the assistant avoids hallucinating v1 terms for newer bookings or vice-versa.
3. **Structured Knowledge Base with Direct Document Citations:**
   Rather than introducing a non-deterministic vector database with local embedding model overhead, the 5 official policy documents (`RW-POL-01` to `RW-POL-05`) are pre-indexed with exact document references. Every response cites the precise policy document and record ID, fulfilling the Transparency and Verifiability criteria.

### 2. Which alternatives did you consider and reject?
- **Unconstrained Text-to-SQL:**
  We rejected letting the LLM generate and execute raw SQL queries. Autonomous text-to-SQL is prone to prompt injection (jailbreaking role boundaries) and syntax hallucinations on multi-table joins. Parameterized functions guarantee safe, deterministic query execution.
- **Complex Multi-Agent Frameworks (e.g., CrewAI / AutoGen):**
  We considered a multi-agent debate architecture (e.g., separate Critic and Retriever agents), but rejected it because multi-turn autonomous loops introduce significant latency, unpredictability, and rate-limiting risks under live panel evaluation. A single, focused ReAct loop with function calling provides reliable low-latency responses.

### 3. Where does your assistant currently fail or behave poorly?
- **Ambiguous Relative Timestamps in Natural Language:**
  When a user refers to "yesterday's booking" without specifying a `booking_id` or date, the assistant relies on the latest booking in the customer's history. If multiple bookings were made on the same date, it must prompt for clarification.
- **Unstructured Visual Damage Verification:**
  While the assistant correctly reports the status of damage claims (`OPEN`, `CHARGED`, `DISPUTED`, `WAIVED`) and applies the schedule costs, it cannot evaluate photographic evidence or inspect vehicle damage directly.

### 4. What would you build next with one more week?
- **Production Authentication & Session Tokens:** Replace manual role and ID entry with a secure OAuth2 / JWT authentication flow.
- **Dispute Resolution & Action Workflow:** Enable Support Agents to directly approve waivers, dispute resolutions, and payment gateway refunds from within the assistant interface via an audited human-in-the-loop workflow.
- **Automated Regression Suite:** Implement an automated test harness (using DeepEval or Ragas) with 100+ evaluation questions testing policy boundaries, mathematical calculations, and security leak vectors.
