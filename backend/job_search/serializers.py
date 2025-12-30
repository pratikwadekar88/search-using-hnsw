from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model."""
    distance = serializers.FloatField(read_only=True, required=False)
    similarity = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'job_title', 'company', 'location',
            'salary_min', 'salary_max', 'salary_currency',
            'job_type', 'experience_required', 'key_skills',
            'description', 'requirements', 'is_active',
            'created_at', 'updated_at', 'distance', 'similarity'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_similarity(self, obj):
        """Convert distance to similarity score (1 - distance)."""
        if hasattr(obj, 'distance') and obj.distance is not None:
            # Convert cosine distance to similarity percentage
            similarity = (1 - obj.distance) * 100
            return round(similarity, 2)
        return None


class JobListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing jobs."""
    
    class Meta:
        model = Job
        fields = [
            'id', 'job_title', 'company', 'location',
            'salary_min', 'salary_max', 'salary_currency',
            'job_type', 'created_at'
        ]
