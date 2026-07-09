# HCP CRM - AI-First Log Interaction Module

A comprehensive Customer Relationship Management system designed for Healthcare Professional interactions with AI-powered assistance using LangGraph and Groq LLMs.

## Features

### Core Functionality
- **Dual Interface**: Log interactions via structured form OR conversational AI chat
- **AI-Powered Assistance**: LangGraph agent with Groq LLM integration
- **Complete CRUD Operations**: Create, read, update, and delete HCP interactions
- **Sentiment Analysis**: Track HCP sentiment for better relationship management
- **Follow-up Management**: Schedule and track follow-up actions

### LangGraph Tools
1. **Log Interaction**: AI-powered interaction logging with summarization
2. **Edit Interaction**: Modify existing interaction records
3. **Get HCP Details**: Retrieve comprehensive HCP information
4. **Get Interaction History**: View past interactions with HCPs
5. **Schedule Follow-up**: Plan and track future interactions
6. **Generate Meeting Notes**: AI-generated structured meeting summaries

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI Framework**: LangGraph with LangChain
- **LLM**: Groq (gemma2-9b-it, llama-3.3-70b-versatile)
- **Database**: MySQL/PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (implemented but configurable)

### Frontend
- **Framework**: React 18
- **State Management**: Redux Toolkit
- **Styling**: Google Inter font with custom CSS
- **API Client**: Axios with interceptors

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- MySQL/PostgreSQL
- Groq API Key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend


2. Navigate to frontend

```bash
cd frontend
```

Install packages

```bash
npm install
```

Run

```bash
npm run dev
```

Frontend runs at

```
http://localhost:5173
```

---
