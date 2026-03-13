# News Aggregator

A daily-updated news aggregation website focused on **Programmer Circle** and **AI Circle**.

## Project Structure

```
news-aggregator/
├── backend/           # Flask API and crawler
│   ├── app.py         # Flask application
│   ├── crawler.py     # RSS crawler script
│   ├── models.py      # SQLAlchemy models
│   └── requirements.txt
├── frontend/          # Vue 3 frontend
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── components/
│   │       └── NewsCard.vue
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── .github/
    └── workflows/
        └── crawler.yml  # Daily crawler automation
```

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py             # Start API server
python crawler.py         # Run crawler manually
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Deployment

- **Backend**: Deploy to Render (free tier)
- **Frontend**: Deploy to Vercel (free tier)
- **Crawler**: Runs automatically via GitHub Actions daily at 00:00 UTC

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/news` | GET | Get paginated news list |
| `/api/news/:id` | GET | Get single news item |
| `/api/categories` | GET | Get all categories |
| `/api/health` | GET | Health check |

## License

Content belongs to original authors. This site only aggregates and displays titles/summaries with links to original sources.
