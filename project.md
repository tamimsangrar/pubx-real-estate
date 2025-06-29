Goal: build a Netlify-hosted, MCP-enabled real-estate chat agent.
Modules: A–I (see sections above). Each module = independent deploy + tests.
0. Repository skeleton
real-estate-agent/
├─ .netlify/
│  └─ functions/
│     ├─ chat.py
│     ├─ mcp.py
│     ├─ crm_upsert_lead.py
│     ├─ calendar_block_tentative.py
│     ├─ crawler_fetch_listings.py
│     └─ voice_connect_call.py
├─ supabase/
│  ├─ migrations/
│  └─ edge-functions/
│     └─ lead_score.ts
├─ web/
│  ├─ widget/                 # tiny React chat bubble
│  └─ admin/                  # React (Supabase Auth)
├─ infra/
│  ├─ netlify.toml
│  └─ env.example
├─ tests/
│  ├─ unit/
│  └─ integration/
└─ README.md

1. Supabase backend (Module A)
Item	Detail
Tables	leads(id, name, email, phone, source, created_at)
lead_scores(id, lead_id, score, reason)
settings(id, key, value_json)
RLS	Public anon key: INSERT only on leads ; no SELECT.
Service role: full access (used by Netlify Functions).
Vector store	listings(id, address, price, url, embedding vector(1536))
Edge Functions	lead_score.ts (runs on cron every 5 min)
Logic: rule-based → writes to lead_scores.
Tests	tests/unit/test_sql_constraints.py – ensure NOT NULL / unique keys.
tests/integration/test_rls.py – verify anon key can insert but not read.

2. Chat orchestrator (Module B)
File: .netlify/functions/chat.py

Concern	Implementation
Framework	FastAPI handler inside Netlify Synchronous Function.
LangGraph	Nodes: intent_router → retrieval → llm_tool_call → tool_router
LLM	gpt-3.5-turbo default, gpt-4o only when tool call emitted.
Tool discovery	load_tools_from_mcp() → GET /.netlify/functions/mcp. Cached 600 s.
Streaming	Convert OpenAI stream=True iterator to ReadableStream (yield SSE).
Unit tests	tests/unit/test_intent_router.py (mock model).
Integration tests	tests/integration/test_chat_mcp_tools.py
✧ spin up local FastAPI + stub tool endpoints; assert JSON calls.

3. MCP registry (Module C)
File: .netlify/functions/mcp.py

Task	Detail
Library	fastmcp==0.3.*
Registration pattern	Each function exports metadata via @tool() decorator; FastMCP aggregates and returns the YAML/JSON manifest.
Cold-start	Stateless; <300 ms on Netlify.
Tests	tests/unit/test_manifest_validates.py – JSON-schema validate every tool.

4. Tool endpoints (Modules D1–D5)
ID	Path	Input schema	Success payload	Smoke-test
D1 crm.upsertLead	/crm_upsert_lead	{name,email,phone}	{lead_id}	Insert row, assert 200.
D2 calendar.blockTentative	/calendar_block_tentative	{lead_id,datetime_start,datetime_end}	{event_id, meet_url}	Use Google Calendar sandbox; ensure status tentative.
D3 crawler.fetchListings	/crawler_fetch_listings	{url}	{listing_id,summary}	Mock Playwright; expect summary & vector embed.
D4 voice.connectCall	/voice_connect_call (Background)	{lead_id}	{call_sid}	Twilio test creds; place call to echo service.
D5 leadScore.getLatest	Supabase Edge Function	{lead_id}	{score,reason}	Fetch row; returns 404 if pending.

All functions require Authorization: Bearer SERVICE_ROLE_KEY except public-insert tools, enforced via Netlify env vars.

5. Lead-scoring job (Module E)
File: supabase/edge-functions/lead_score.ts

Cron every 5 min (supabase.functions.schedule).

Query new leads without score.

Rule rubric (P1):
price budget ≥ median ±20 % → +40 points
verified phone (E.164) → +30
email domain ≠ tempmail → +20
answered ≥3 profile questions → +10

Insert into lead_scores.

Notify chat orchestrator via Supabase Realtime channel if score ≥ 70.

Test: trigger function locally with sample JSON; assert correct score.

6. Admin dashboard (Module F)
Feature	Stack
Auth	Supabase Auth (email link)
Pages	/leads (table + filter by score)
/settings (edit system prompt, thresholds)
State	React Query • TailwindCSS
Testing	Cypress E2E: login → change threshold → Supabase row updated.

7. Front-end chat widget (Module G)
Aspect	Detail
Bundle size	Optimized for performance (React + Vite)
API	POST /api/chat streaming SSE
Theme	CSS variables so host site can tweak colors
Local test	Storybook story renders widget with framer animations

8. Voice bridge (Module H)
File: .netlify/functions/voice_connect_call.py (Background)

Fetch lead data.

Call Twilio Function URL that bridges ElevenLabs TTS ↔ Google STT.

Stream audio; on hang-up POST transcript to lead_notes table.

Load test: run 5 parallel calls using Twilio test numbers; all return call_sid.

9. DevOps / CI/CD (Module I)
Item	Implementation
Netlify	env vars set per context (prod, preview).
GitHub Actions	Lint → pytest → supabase migrations → netlify-cli deploy --alias pr-###.
Secrets	Use Netlify encrypted vars; Supabase service key NOT committed.
Observability	OTLP traces from LangGraph → Grafana Cloud free tier; dashboard JSON committed to /infra/.

10. End-to-end test matrix
Scenario	Modules exercised	Expected
A New visitor asks FAQ	B → (no tools)	Text answer ≤1 s.
B Lead capture + score	B → D1 → E → B	Agent responds with "Thanks, I've put a hold ...".
C Calendar booking race	B → D2 twice (same slot)	Second call returns 409 Conflict; LLM apologizes.
D Voice escalation	B → D4	Outbound call rings; transcript saved.

All four pass in CI before a merge to main.

11. Suggested development order
Module A (DB + RLS)

Module B (+ C stub) – respond with echo message.

Module D1 & unit tests – hook into B.

Module E – cron locally, verify score update.

Module D2 – Google sandbox calendar.

Module G – static widget; connect to B.

Module F – minimal admin UI.

Module D3/D4 – crawler, voice.

Module I – tighten CI/CD, observability.

