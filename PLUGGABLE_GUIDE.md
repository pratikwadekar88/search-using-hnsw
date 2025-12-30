# Making job_search a Pluggable Django App

This guide shows you how to integrate the `job_search` app into your existing Django projects.

## What is a Pluggable App?

The `job_search` app is designed to be **self-contained** and **reusable**. You can drop it into any Django project to add semantic job search functionality without modifying your existing code.

## Integration Steps

### 1. Copy the App

Copy the entire `job_search/` directory to your Django project:

```bash
cp -r /path/to/searchFeature/backend/job_search /path/to/your-project/
```

Your project structure should look like:

```
your-project/
├── your_app/
├── job_search/          # ← New app
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── migrations/
│   └── management/
├── your_project/
│   ├── settings.py
│   └── urls.py
└── manage.py
```

### 2. Install Dependencies

Add these to your `requirements.txt`:

```txt
djangorestframework==3.14.0
psycopg[binary]==3.2.13
pgvector==0.2.4
sentence-transformers==3.0.1
beautifulsoup4==4.12.3
django-cors-headers==4.3.1
```

Install them:

```bash
pip install -r requirements.txt
```

### 3. Update settings.py

Add the required apps to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... your existing apps ...
    
    # Required for job_search
    'rest_framework',
    'corsheaders',
    
    # The job search app
    'job_search',
]
```

Add CORS middleware (if using a separate frontend):

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Add this
    # ... rest of your middleware ...
]

# CORS Configuration (adjust for production)
CORS_ALLOW_ALL_ORIGINS = True  # Development only
CORS_ALLOW_CREDENTIALS = True
```

Configure PostgreSQL database (if not already using it):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. Update urls.py

Include the job_search URLs in your project's main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # ... your existing URLs ...
    
    # Add job search API endpoints
    path('api/jobs/', include('job_search.urls')),
]
```

### 5. Set Up Database

Ensure pgvector extension is installed in PostgreSQL:

```bash
psql your_database_name
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

Run migrations:

```bash
python manage.py makemigrations job_search
python manage.py migrate
```

### 6. Seed Data (Optional)

Load sample job data:

```bash
python manage.py seed_jobs
```

## Using the API

Once integrated, the job search API will be available at:

```
GET  /api/jobs/                  # List all jobs
GET  /api/jobs/search/?q=query   # Semantic search
GET  /api/jobs/{id}/             # Get specific job
POST /api/jobs/                  # Create new job
```

## Customization

### Extending the Job Model

If you need additional fields, edit `job_search/models.py`:

```python
class Job(models.Model):
    # ... existing fields ...
    
    # Add your custom fields
    remote_allowed = models.BooleanField(default=False)
    benefits = models.TextField(null=True, blank=True)
    
    # ... rest of the model ...
```

Then make and run migrations:

```bash
python manage.py makemigrations job_search
python manage.py migrate
```

### Changing the Embedding Model

Edit `job_search/models.py` to use a different sentence-transformers model:

```python
# Instead of "all-MiniLM-L6-v2", use:
EMBEDDING_MODEL = SentenceTransformer("all-mpnet-base-v2")  # Higher quality
# or
EMBEDDING_MODEL = SentenceTransformer("paraphrase-MiniLM-L3-v2")  # Faster
```

**Important**: If you change the model, update the `dimensions` in the `search_vector` field to match:

```python
search_vector = VectorField(dimensions=768)  # For all-mpnet-base-v2
```

### Adjusting Search Relevance

Modify the search threshold in your frontend or API calls:

- `threshold=0.5`: Very broad results
- `threshold=0.7`: Balanced (default)
- `threshold=0.9`: Very strict, high relevance only

### Adding Filters

Extend the `JobViewSet` in `job_search/views.py`:

```python
def get_queryset(self):
    queryset = super().get_queryset()
    
    # Add custom filters
    location = self.request.query_params.get('location')
    if location:
        queryset = queryset.filter(location__icontains=location)
    
    return queryset
```

## Admin Integration

Register the Job model in Django admin (`job_search/admin.py`):

```python
from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company', 'location', 'is_active', 'created_at']
    list_filter = ['job_type', 'is_active', 'created_at']
    search_fields = ['job_title', 'company', 'location']
    readonly_fields = ['id', 'created_at', 'updated_at']
```

## Production Considerations

1. **Environment Variables**: Store sensitive data in environment variables
   
   ```python
   import os
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.getenv('DB_NAME'),
           'USER': os.getenv('DB_USER'),
           'PASSWORD': os.getenv('DB_PASSWORD'),
           # ...
       }
   }
   ```

2. **CORS**: Restrict CORS to specific origins
   
   ```python
   CORS_ALLOWED_ORIGINS = [
       "https://yourfrontend.com",
   ]
   ```

3. **Caching**: Consider caching the embedding model to avoid reloading
   
4. **Async Processing**: For large-scale applications, generate embeddings asynchronously using Celery

## Troubleshooting

**Migrations conflict:**
- Check for conflicting migration files
- Use `--merge` flag: `python manage.py makemigrations --merge`

**Model not loading:**
- Ensure internet connectivity for first-time model download
- Check disk space (~80MB required)

**Search not working:**
- Verify pgvector extension: `psql -c "SELECT * FROM pg_extension WHERE extname = 'vector';"`
- Check if embeddings exist: `SELECT COUNT(*) FROM job_search_job WHERE search_vector IS NOT NULL;`

## Next Steps

- Customize the Job model for your domain
- Add authentication/permissions to API endpoints
- Integrate with your existing user management system
- Build a custom frontend or use the provided Angular app

## Support

For questions or issues, refer to the main [README.md](README.md) or check the Django and pgvector documentation.
