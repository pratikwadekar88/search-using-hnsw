from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from pgvector.django import CosineDistance
from .models import Job, EMBEDDING_MODEL
from .serializers import JobSerializer, JobListSerializer


class JobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Job model with semantic search capabilities.
    """
    queryset = Job.objects.filter(is_deleted=False)
    serializer_class = JobSerializer
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == 'list':
            return JobListSerializer
        return JobSerializer
    
    def get_queryset(self):
        """Filter active jobs and add pagination support."""
        queryset = super().get_queryset()
        
        # Filter by is_active if specified
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-created_at')  # Newest first
    
    def list(self, request, *args, **kwargs):
        """Override list to add pagination metadata like search endpoint."""
        queryset = self.get_queryset()
        
        # Get pagination params
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 25))
        
        # Calculate pagination
        total_count = queryset.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        jobs = queryset[start_idx:end_idx]
        
        # Serialize
        serializer = self.get_serializer(jobs, many=True)
        
        return Response({
            'page': page,
            'page_size': page_size,
            'total_results': total_count,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Semantic search endpoint using pgvector's cosine distance.
        Now with pagination support (25 results per page).
        
        Query params:
        - q: search query (required)
        - page: page number (default: 1)
        - page_size: results per page (default: 25)
        - threshold: similarity threshold 0-1 (default: 0.85, lower = stricter)
        """
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({
                'error': 'Query parameter "q" is required'
            }, status=400)
        
        # Pagination parameters
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 25))
        threshold = float(request.query_params.get('threshold', 0.85))
        
        # Encode the user query into a vector
        query_vec = EMBEDDING_MODEL.encode(query)
        
        # Database Search - Get ALL job IDs sorted by relevance first
        # We need to do this in two steps because Django's queryset slicing
        # doesn't work properly with .alias() for vector operations
        all_job_ids = list(
            Job.objects.filter(is_active=True, is_deleted=False)
            .alias(distance=CosineDistance('search_vector', query_vec))
            .order_by('distance')
            .values_list('id', flat=True)
        )
        
        # Calculate pagination
        total_count = len(all_job_ids)
        total_pages = (total_count + page_size - 1) // page_size
        
        # Get IDs for this specific page
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_job_ids = all_job_ids[start_idx:end_idx]
        
        # Fetch the actual job objects for this page
        # Preserve the order from our distance-sorted ID list
        jobs = Job.objects.filter(id__in=page_job_ids)
        jobs = sorted(jobs, key=lambda x: page_job_ids.index(x.id))
        
        # Serialize results
        serializer = JobSerializer(jobs, many=True)
        
        return Response({
            'query': query,
            'page': page,
            'page_size': page_size,
            'total_results': total_count,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1,
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def hybrid_search(self, request):
        """
        Hybrid search combining semantic vectors + keyword matching.
        Uses Reciprocal Rank Fusion (RRF) to merge results.
        """
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, status=400)
        
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 25))
        
        # 1. Semantic Search (Vector)
        query_vec = EMBEDDING_MODEL.encode(query)
        semantic_ids = list(
            Job.objects.filter(is_active=True, is_deleted=False)
            .alias(distance=CosineDistance('search_vector', query_vec))
            .order_by('distance')
            .values_list('id', flat=True)[:100]
        )
        
        # 2. Keyword Search (Full-Text)
        try:
            keyword_jobs = Job.fulltext_search(query, limit=100)
            keyword_ids = [job.id for job in keyword_jobs]
        except Exception as e:
            print(f"Full-text search error: {e}")
            keyword_ids = []
        
        # 3. Merge using RRF
        merged_ids = self._reciprocal_rank_fusion(semantic_ids, keyword_ids, k=60)
        
        # 4. Paginate
        total_count = len(merged_ids)
        total_pages = (total_count + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        page_job_ids = merged_ids[start_idx:start_idx + page_size]
        
        # 5. Fetch jobs
        jobs = Job.objects.filter(id__in=page_job_ids)
        jobs = sorted(jobs, key=lambda x: page_job_ids.index(x.id))
        
        serializer = JobSerializer(jobs, many=True)
        
        return Response({
            'query': query,
            'mode': 'hybrid',
            'semantic_results': len(semantic_ids),
            'keyword_results': len(keyword_ids),
            'page': page,
            'page_size': page_size,
            'total_results': total_count,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1,
            'results': serializer.data
        })
    
    def _reciprocal_rank_fusion(self, list1, list2, k=60):
        """Merge two ranked lists using Reciprocal Rank Fusion."""
        scores = {}
        for rank, item_id in enumerate(list1, start=1):
            scores[item_id] = scores.get(item_id, 0) + 1 / (k + rank)
        for rank, item_id in enumerate(list2, start=1):
            scores[item_id] = scores.get(item_id, 0) + 1 / (k + rank)
        return [item_id for item_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)]
