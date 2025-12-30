# PostgreSQL + pgvector Setup Guide (macOS)

This guide walks you through setting up PostgreSQL with the pgvector extension for semantic search.

## Prerequisites

- macOS (Intel or Apple Silicon)
- Homebrew package manager

## Installation Steps

### 1. Install PostgreSQL

```bash
# Install PostgreSQL 16 (or latest)
brew install postgresql@16

# Start PostgreSQL service
brew services start postgresql@16

# Verify installation
psql --version
```

### 2. Create Database and User

```bash
# Connect to PostgreSQL as superuser
psql postgres

# In the psql shell:
# Create database
CREATE DATABASE job_search_db;

# Create user (if needed)
CREATE USER postgres WITH PASSWORD 'postgres';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE job_search_db TO postgres;
ALTER DATABASE job_search_db OWNER TO postgres;

# Exit psql
\q
```

### 3. Install pgvector Extension

```bash
# Connect to your database
psql job_search_db

# Install the vector extension
CREATE EXTENSION vector;

# Verify installation
\dx

# You should see 'vector' in the list of extensions
# Exit
\q
```

### 4. Update Database Credentials

Edit `backend/.env` with your actual database credentials:

```env
DB_NAME=job_search_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

## Verification

Test the connection:

```bash
cd backend
source ../venv/bin/activate
python manage.py check --database default
```

If successful, you'll see: `System check identified no issues (0 silenced).`

## Common Issues

### PostgreSQL not starting

```bash
# Check status
brew services list

# If not running, try:
brew services restart postgresql@16
```

### Role "postgres" does not exist

Create the postgres role:

```bash
psql postgres
CREATE ROLE postgres WITH LOGIN PASSWORD 'postgres';
ALTER ROLE postgres CREATEDB;
\q
```

### Permission denied

Grant necessary privileges:

```bash
psql postgres
GRANT ALL PRIVILEGES ON DATABASE job_search_db TO postgres;
ALTER DATABASE job_search_db OWNER TO postgres;
\c job_search_db
GRANT ALL ON SCHEMA public TO postgres;
\q
```

### pgvector extension not available

Install pgvector using Homebrew:

```bash
brew install pgvector

# Then connect to your database and run:
psql job_search_db
CREATE EXTENSION vector;
\q
```

## Running Migrations

Once PostgreSQL is set up:

```bash
cd backend
source ../venv/bin/activate

# Run migrations
python manage.py migrate

# You should see: 
# - Running migration 0001_initial (creates vector extension)
# - Running migration 0002_initial (creates Job table with vector field)
```

## Testing pgvector

Test vector operations directly in PostgreSQL:

```sql
psql job_search_db

-- Create a test table
CREATE TABLE items (id SERIAL PRIMARY KEY, embedding vector(3));

-- Insert test vectors
INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');

-- Query using cosine distance
SELECT * FROM items ORDER BY embedding <=> '[3,1,2]' LIMIT 5;

-- Clean up
DROP TABLE items;
\q
```

## Next Steps

After completing this setup:

1. Run database migrations: `python manage.py migrate`
2. Seed sample data: `python manage.py seed_jobs`
3. Start the Django server: `python manage.py runserver`

The first time you run the application, the sentence-transformers model (~80MB) will be downloaded automatically.
