from django.core.management.base import BaseCommand
from job_search.models import Job
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Regenerate embeddings for all jobs with new weighting (Title 5x, Skills 2x)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Regenerating embeddings with new weights...'))
        self.stdout.write('Title: 5x | Skills: 2x | Description: 1x')
        
        jobs = Job.objects.filter(is_deleted=False)
        total = jobs.count()
        
        self.stdout.write(f'Found {total} jobs to update')
        
        updated = 0
        for job in tqdm(jobs, desc="Updating embeddings"):
            try:
                # Calling save() triggers embedding regeneration with new weights
                job.save()
                updated += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating job {job.id}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated}/{total} jobs'))
        self.stdout.write(self.style.SUCCESS('All embeddings now use hierarchical weighting!'))
