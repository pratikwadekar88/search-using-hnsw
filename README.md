# Semantic Job Search System

A production-ready job search application powered by **vector similarity search** using PostgreSQL's pgvector extension. The system uses AI embeddings to enable intelligent semantic matching between user queries and job listings.

## 🌟 Features

- **Semantic Search**: Find relevant jobs even when search terms don't exactly match
- **AI-Powered**: Uses `all-MiniLM-L6-v2` sentence transformer model for embeddings
- **Fast Vector Search**: HNSW index for approximate nearest neighbor search
- **Modern Stack**: Django REST API + Angular frontend
- **Pluggable**: Django app can be integrated into your existing projects
- **Auto-Embeddings**: Vector embeddings generated automatically on job creation

## 🏗️ Architecture

```
searchFeature/
├── backend/                    # Django REST API
│   ├── job_search/            # Pluggable Django app
│   │   ├── models.py          # Job model with VectorField
│   │   ├── views.py           # Semantic search API
│   │   ├── serializers.py     # DRF serializers
│   │   └── management/
│   │       └── commands/
│   │           └── seed_jobs.py   # Sample data
│   ├── job_search_project/    # Django project
│   ├── manage.py
│   └── requirements.txt
├── frontend/                   # Angular application
│   └── job-search-frontend/
└── venv/                      # Python virtual environment
```

## 📋 Prerequisites

- **Python 3.10+**
- **Node.js 18+** & npm
- **PostgreSQL 14+** with pgvector extension

## 🚀 Quick Start

### 1. Set Up PostgreSQL with pgvector

```bash
# On macOS with Homebrew
brew install postgresql@16
brew services start postgresql@16

# Connect to PostgreSQL
psql postgres

# In psql:
CREATE DATABASE job_search_db;
\c job_search_db
CREATE EXTENSION vector;
\q
```

See [DATABASE_SETUP.md](DATABASE_SETUP.md) for detailed instructions.

### 2. Backend Setup

```bash
cd backend

# Activate virtual environment
source ../venv/bin/activate

# Install dependencies (already done during setup)
pip install -r requirements.txt

# Update .env file with your database credentials if needed
# DB_NAME, DB_USER, DB_PASSWORD are already set

# Run migrations
python manage.py migrate

# Seed sample data
python manage.py seed_jobs

# Start Django server
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### 3. Frontend Setup

```bash
cd frontend/job-search-frontend

# Install dependencies  
npm install

# Start Angular development server
npm start
```

The frontend will be available at `http://localhost:4200`

## 📖 API Documentation

### Endpoints

#### Search Jobs (Semantic)
```http
GET /api/jobs/search/?q=python developer&limit=20&threshold=0.7
```

**Parameters:**
- `q` (required): Search query
- `limit` (optional): Max results (default: 20)
- `threshold` (optional): Similarity threshold 0-1 (default: 0.7, lower = stricter)

**Response:**
```json
{
  "query": "python developer",
  "count": 5,
  "results": [
    {
      "id": "uuid",
      "job_title": "Senior Python Developer",
      "company": "TechCorp Inc",
      "location": "San Francisco, CA",
      "salary_min": 120000,
      "salary_max": 180000,
      "key_skills": ["Python", "Django", "PostgreSQL"],
      "similarity": 95.2,
      "distance": 0.048,
      ...
    }
  ]
}
```

#### List All Jobs
```http
GET /api/jobs/
```

#### Get Job by ID
```http
GET /api/jobs/{id}/
```

#### Create Job
```http
POST /api/jobs/
Content-Type: application/json

{
  "job_title": "Backend Engineer",
  "company": "CompanyName",
  "location": "Remote",
  "key_skills": ["Python", "Django"],
  ...
}
```

## 🔌 Using as a Pluggable App

See [PLUGGABLE_GUIDE.md](PLUGGABLE_GUIDE.md) for detailed instructions on integrating the `job_search` app into your existing Django projects.

**Quick steps:**
1. Copy the `job_search/` directory to your project
2. Add `'job_search'` to `INSTALLED_APPS`
3. Configure PostgreSQL with pgvector
4. Run migrations
5. Include URLs: `path('api/', include('job_search.urls'))`

## 🧪 Testing the Search

Try these example searches to see semantic matching in action:

- **"machine learning engineer"** → Matches ML, AI, Data Science roles
- **"frontend developer react"** → Matches React, JavaScript, UI roles
- **"cloud infrastructure"** → Matches DevOps, AWS, Kubernetes roles
- **"python backend"** → Matches Django, Flask, FastAPI roles

## 🛠️ Technology Stack

**Backend:**
- Django 5.0
- Django REST Framework
- PostgreSQL with pgvector
- sentence-transformers (all-MiniLM-L6-v2)
- BeautifulSoup4 (HTML cleaning)

**Frontend:**
- Angular 21
- TypeScript
- RxJS for reactive programming
- Modern CSS with animations

## 📊 How It Works

1. **Embedding Generation**: When a job is created/updated, the system:
   - Combines job title, skills, description into one text
   - Generates a 384-dimensional vector using `all-MiniLM-L6-v2`
   - Stores it in the `search_vector` field

2. **Semantic Search**: When a user searches:
   - Query text is converted to a vector
   - PostgreSQL's pgvector performs cosine similarity search using HNSW index
   - Results are ranked by similarity score

3. **Performance**: HNSW index enables fast approximate nearest neighbor search, even with millions of records

## 🎨 Frontend Features

- **Real-time Search**: Debounced search with 500ms delay
- **Similarity Scores**: Visual similarity percentage on each result
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Gradient backgrounds, smooth animations, card-based layout
- **Error Handling**: Graceful error messages and retry functionality

## 🤝 Contributing

Feel free to customize and extend this project for your needs!

## 📝 License

MIT License - Use this project however you like!

## 🐛 Troubleshooting

**Model download fails:**
- The sentence-transformers model (~80MB) downloads on first run
- Ensure internet connectivity during initial setup

**PostgreSQL connection error:**
- Verify PostgreSQL is running: `brew services list`
- Check credentials in `backend/.env`
- Ensure `vector` extension is installed: `psql job_search_db -c "CREATE EXTENSION IF NOT EXISTS vector;"`

**CORS errors:**
- Backend is configured for development (CORS_ALLOW_ALL_ORIGINS=True)
- For production, update `CORS_ALLOWED_ORIGINS` in settings.py

## 📧 Support

For issues or questions, please check the documentation files or create an issue in the repository.
