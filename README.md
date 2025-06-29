# PubX Real Estate Agent

A Netlify-hosted, MCP-enabled real estate chat agent with comprehensive lead management and voice capabilities.

## 🏗️ Architecture

- **Backend**: Supabase (PostgreSQL + Auth + Edge Functions)
- **API**: Netlify Functions (FastAPI + LangGraph)
- **Frontend**: React + Framer Motion + TailwindCSS
- **Deployment**: Netlify with CI/CD
- **Voice**: Twilio + ElevenLabs integration

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Supabase CLI
- Netlify CLI

### Setup
1. Clone the repository
2. Install dependencies: `npm install && pip install -r requirements.txt`
3. Set up environment variables (see `infra/env.example`)
4. Run Supabase migrations: `supabase db push`
5. Deploy to Netlify: `netlify deploy --prod`

## 📁 Project Structure

```
pubx-real-estate/
├─ .netlify/functions/     # Netlify serverless functions
├─ supabase/              # Database + Edge Functions
├─ web/                   # React frontend
│  ├─ widget/            # Chat widget component
│  └─ admin/             # Admin dashboard
├─ infra/                # Configuration files
└─ tests/                # Test suites
```

## 🔧 Modules

- **A**: Supabase backend (tables, RLS, vector store)
- **B**: Chat orchestrator (LangGraph + FastAPI)
- **C**: MCP registry (tool discovery)
- **D**: Tool endpoints (CRM, Calendar, Crawler, Voice)
- **E**: Lead scoring (cron job)
- **F**: Admin dashboard (React + Supabase Auth)
- **G**: Chat widget (React + Framer Motion)
- **H**: Voice bridge (Twilio integration)
- **I**: DevOps (CI/CD + observability)

## 🌐 Live Demo

[Coming soon - Netlify deployment]

## 📝 License

MIT 