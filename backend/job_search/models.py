import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField, HnswIndex, CosineDistance
from django.contrib.postgres.search import SearchQuery, SearchRank
from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup

# Load model ONCE at module level (prevents reloading on every request)
try:
    EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"Warning: Could not load embedding model. {e}")
    EMBEDDING_MODEL = None


class Job(models.Model):
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Job Information
    job_title = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    
    # Salary Information
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default='USD')
    
    # Job Details
    job_type = models.CharField(
        max_length=50,
        choices=[
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('contract', 'Contract'),
            ('internship', 'Internship'),
            ('freelance', 'Freelance'),
        ],
        default='full_time'
    )
    experience_required = models.CharField(max_length=100, null=True, blank=True)
    key_skills = models.JSONField(null=True, blank=True, default=list)
    description = models.TextField(null=True, blank=True)
    requirements = models.TextField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # VECTOR SEARCH FIELD (384 dimensions for 'all-MiniLM-L6-v2')
    search_vector = VectorField(
        dimensions=384,
        null=True,
        blank=True,
        help_text="Semantic Search Vector"
    )
    
    class Meta:
        indexes = [
            # HNSW Index for fast approximate nearest neighbor search
            HnswIndex(
                name='job_search_idx',
                fields=['search_vector'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops']
            )
        ]
        ordering = ['-created_at']
    
    def clean_html(self, html_content):
        """Convert HTML to clean plain text."""
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    
    def generate_embedding_text(self):
        """
        Constructs a single 'rich' string for the AI to read.
        We repeat important fields to give them 'weight' in the embedding.
        """
        title = self.job_title or ""
        company_name = self.company or ""
        location_name = self.location or ""
        
        # Handle key_skills (it's a JSON list, so join it)
        if isinstance(self.key_skills, list):
            skills = ", ".join(self.key_skills)
        else:
            skills = str(self.key_skills) if self.key_skills else ""
        
        clean_desc = self.clean_html(self.description)
        clean_reqs = self.clean_html(self.requirements)
        
        # PRO TIP: The structure helps the model understand context.
        # We repeat Title and Skills to prioritize them over long descriptions.
        combined_text = (
            f"Job Title: {title}. "
            f"Company: {company_name}. "
            f"Location: {location_name}. "
            f"Required Skills: {skills}. "
            f"Description: {clean_desc}. "
            f"Requirements: {clean_reqs}"
        )
        return combined_text
    
    def save(self, *args, **kwargs):
        """Override save to automatically generate embeddings."""
        # Only update vector if model is available
        if EMBEDDING_MODEL:
            text_to_embed = self.generate_embedding_text()
            if text_to_embed.strip():
                # Encode and store directly
                self.search_vector = EMBEDDING_MODEL.encode(text_to_embed)
        
        super().save(*args, **kwargs)
    
    @classmethod
    def fulltext_search(cls, query, limit=100):
        """
        Keyword-based full-text search using PostgreSQL.
        Returns jobs ranked by text relevance using the search_text tsvector column.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results to return
            
        Returns:
            QuerySet: Jobs ordered by relevance (highest first)
        """
        from django.contrib.postgres.search import SearchQuery, SearchRank
        
        # Use websearch syntax for better query parsing
        # Example: "python developer" OR "machine learning"
        search_query = SearchQuery(query, search_type='websearch')
        
        return cls.objects.filter(
            is_active=True, 
            is_deleted=False
        ).annotate(
            rank=SearchRank('search_text', search_query)
        ).filter(
            rank__gt=0.01  # Minimum relevance threshold
        ).order_by('-rank')[:limit]
    
    def __str__(self):
        return self.job_title or f"Job {self.id}"
