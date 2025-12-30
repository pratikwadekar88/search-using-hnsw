import uuid
import random
from faker import Faker
from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer
from job_search.models import Job

# --- CONFIGURATION ---
BATCH_SIZE = 1000
TOTAL_RECORDS = 10000

# Realistic Tech Data Pools
TITLES = [
    "Python Backend Developer", "Frontend React Engineer", "DevOps Specialist", 
    "Full Stack Developer (MERN)", "Data Scientist", "Machine Learning Engineer",
    "Java Spring Boot Developer", "Cloud Architect (AWS)", "QA Automation Engineer",
    "Product Manager", "UI/UX Designer", "Cyber Security Analyst",
    "Golang Developer", "Rust Systems Engineer", "Technical Lead",
    "Node.js Developer", "Angular Developer", "Vue.js Developer",
    "iOS Developer (Swift)", "Android Developer (Kotlin)", "Flutter Developer",
    "Database Administrator", "Site Reliability Engineer", "Platform Engineer",
    "AI Research Scientist", "Data Engineer", "Business Intelligence Analyst"
]

SKILLS_POOL = [
    "Python", "Django", "FastAPI", "React", "Next.js", "Vue.js", "Angular",
    "AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "Jenkins",
    "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Kafka",
    "Java", "Spring Boot", "Microservices", "Go", "Rust", "C++",
    "Machine Learning", "PyTorch", "TensorFlow", "NLP", "Computer Vision",
    "Node.js", "Express", "GraphQL", "REST API", "TypeScript",
    "Swift", "Kotlin", "Flutter", "React Native", "iOS", "Android",
    "Git", "Linux", "Agile", "Scrum", "JIRA", "SQL"
]

LOCATIONS = [
    "Bangalore, India", "Pune, India", "Hyderabad, India", "Mumbai, India", 
    "Delhi NCR, India", "Chennai, India", "Remote", "San Francisco, CA",
    "New York, NY", "Seattle, WA", "London, UK", "Berlin, Germany",
    "Singapore", "Toronto, Canada", "Austin, TX", "Boston, MA"
]

JOB_TYPES = ["Full-time", "Part-time", "Contract", "Freelance"]

COMPANIES = [
    "TechCorp Solutions", "InnovateTech Inc", "DataDriven Systems",
    "CloudScale Technologies", "AI Innovations Ltd", "DevOps Masters",
    "CodeCraft Studios", "Digital Transformations", "AgileWorks",
    "FutureTech Enterprises", "SmartSolutions Co", "ByteBuilders",
    "NexGen Software", "Quantum Computing Labs", "CyberSafe Systems"
]

class Command(BaseCommand):
    help = 'Generates 10,000 synthetic jobs with pre-calculated embeddings for performance testing'

    def handle(self, *args, **kwargs):
        faker = Faker('en_IN')  # Indian locale for realistic data
        
        self.stdout.write(self.style.WARNING("1. Loading AI Model (all-MiniLM-L6-v2)..."))
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        self.stdout.write(self.style.SUCCESS(f"2. Starting generation of {TOTAL_RECORDS} jobs..."))
        
        jobs_buffer = []
        total_created = 0

        for i in range(TOTAL_RECORDS):
            # --- A. Generate Random Data ---
            title = random.choice(TITLES)
            company = random.choice(COMPANIES)
            skills = random.sample(SKILLS_POOL, k=random.randint(3, 7))
            location = random.choice(LOCATIONS)
            job_type = random.choice(JOB_TYPES)
            
            # Generate realistic description
            desc_sentences = []
            desc_sentences.append(f"We are looking for a talented {title} to join our dynamic team at {company}.")
            desc_sentences.append(faker.paragraph(nb_sentences=2))
            desc_sentences.append("Key responsibilities include: " + faker.paragraph(nb_sentences=2))
            desc_sentences.append("Requirements: " + faker.paragraph(nb_sentences=2))
            desc_text = " ".join(desc_sentences)
            
            # --- B. Pre-Calculate Embedding ---
            combined_text = f"{title}. {', '.join(skills)}. {desc_text}"
            embedding_vector = model.encode(combined_text)

            # --- C. Create Job Object in Memory ---
            job = Job(
                id=uuid.uuid4(),
                job_title=title,
                company=company,
                location=location,
                job_type=job_type,
                
                salary_min=random.randint(50000, 150000),
                salary_max=random.randint(160000, 300000),
                
                key_skills=skills,
                description=f"<p>{desc_text}</p>",
                requirements=f"<ul><li>{faker.sentence()}</li><li>{faker.sentence()}</li><li>{faker.sentence()}</li></ul>",
                
                is_active=True,
                is_deleted=False,
                
                # THE VECTOR (pre-calculated embedding)
                search_vector=embedding_vector
            )
            
            jobs_buffer.append(job)

            # --- D. Batch Insert to DB ---
            if len(jobs_buffer) >= BATCH_SIZE:
                Job.objects.bulk_create(jobs_buffer, ignore_conflicts=True)
                total_created += len(jobs_buffer)
                jobs_buffer = []
                self.stdout.write(self.style.SUCCESS(f"   ✓ Inserted {total_created}/{TOTAL_RECORDS} jobs"))

        # Insert any remaining items
        if jobs_buffer:
            Job.objects.bulk_create(jobs_buffer, ignore_conflicts=True)
            total_created += len(jobs_buffer)

        self.stdout.write(self.style.SUCCESS(f"\n🎉 DONE! Successfully generated {total_created} jobs with searchable embeddings."))
        self.stdout.write(self.style.WARNING(f"\nYou can now test semantic search at scale!"))
        self.stdout.write(self.style.WARNING(f"Try: python manage.py test_search 'machine learning engineer'"))
