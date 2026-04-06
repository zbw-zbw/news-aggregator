# 极客热榜 (Geek News Aggregator)

A daily-updated news aggregation website focused on **developer and AI communities**, featuring 6 specialized categories with intelligent classification.

## Features

- **6 Specialized Categories**: AI, 前端 (Frontend), 后端 (Backend), 云原生 (Cloud Native), 区块链 (Blockchain), 其他 (Others)
- **Dynamic Classification**: Articles from mixed sources are automatically classified using keyword-based detection
- **Multiple Source Types**: RSS feeds, YouTube channels, and arXiv papers
- **Hot Score Algorithm**: Time-decay based ranking with source weight factors
- **Responsive Design**: Mobile-first UI with Tailwind CSS
- **Performance Optimized**: Flask-Caching, SQLite indexing, and frontend lazy loading

## Project Structure

```
news-aggregator/
├── backend/
│   ├── app.py              # Flask API with caching
│   ├── crawler.py          # RSS/YouTube/arXiv crawler
│   ├── models.py           # SQLAlchemy models
│   ├── category_classifier.py  # Dynamic classification
│   ├── maintenance.py      # DB maintenance utilities
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue         # Main app with pagination
│   │   ├── main.js
│   │   └── components/
│   │       ├── NewsCard.vue
│   │       └── SkeletonCard.vue
│   └── package.json
└── .github/workflows/
    └── crawler.yml         # Daily crawler automation
```

## Tech Stack

| Module | Technology |
| ------ | ---------- |
| Backend | Python Flask, Flask-Caching, SQLAlchemy |
| Database | SQLite with composite indexes |
| Frontend | Vue 3, Vite, Tailwind CSS |
| Crawler | feedparser, requests |
| Deployment | Render (backend), Vercel (frontend) |
| Automation | GitHub Actions (daily crawler) |

## Local Development

### Prerequisites

- Python 3.9+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows PowerShell
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
python app.py             # Start API server (port 5001)
python crawler.py         # Run crawler manually
```

### Frontend

```bash
cd frontend
npm install
npm run dev               # Start dev server (port 5173)
```

## API Endpoints

| Endpoint | Method | Description |
| -------- | ------ | ----------- |
| `GET /api/news` | GET | Paginated news list with filters |
| `GET /api/news/:id` | GET | Single news item |
| `GET /api/categories` | GET | Category list (static) |
| `GET /api/health` | GET | Health check |
| `POST /api/admin/clear-cache` | POST | Clear API cache |

### Query Parameters for `/api/news`

- `category`: Filter by category (AI, 前端, 后端, 云原生, 区块链, 其他)
- `sort`: `newest` or `hottest` (default: newest)
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

## Data Sources

### Categories & Sources

| Category | Source Count | Example Sources |
| -------- | ------------ | --------------- |
| AI | 18+ | OpenAI Blog, DeepMind, arXiv AI/ML, Hugging Face |
| 前端 | 11+ | MDN Blog, web.dev, JavaScript Weekly, CSS Tricks |
| 后端 | 12+ | 美团技术团队, Martin Fowler, Rust Blog, .NET Blog |
| 云原生 | 10+ | Kubernetes Blog, CNCF, Docker Blog, Istio |
| 区块链 | 7+ | Ethereum Blog, CoinDesk, Bitcoin Magazine |
| 其他 | 6+ | Hacker News, Reddit, 开源中国, InfoQ |

### Source Types

- **RSS**: Standard RSS/Atom feeds
- **YouTube**: Channel RSS feeds (marked with video icon)
- **arXiv**: Academic papers (marked with paper icon)

## Deployment

### Backend (Render)

1. Connect GitHub repository
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app`
4. Environment: `FORCE_INIT_DB_ON_START=1` (first deploy only)

### Frontend (Vercel)

1. Connect GitHub repository
2. Root directory: `frontend`
3. Build command: `npm run build`
4. Environment: `VITE_API_BASE=<backend-url>`

## License

Content belongs to original authors. This site only aggregates and displays titles/summaries with links to original sources.
