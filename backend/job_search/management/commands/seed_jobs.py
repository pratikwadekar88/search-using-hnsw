from django.core.management.base import BaseCommand
from job_search.models import Job
import uuid


class Command(BaseCommand):
    help = 'Seeds the database with sample job listings'
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Seeding job data...'))
        
        # Sample job data
        jobs_data = [
            {
                'job_title': 'Senior Python Developer',
                'company': 'TechCorp Inc',
                'location': 'San Francisco, CA',
                'salary_min': 120000,
                'salary_max': 180000,
                'job_type': 'full_time',
                'experience_required': '5+ years',
                'key_skills': ['Python', 'Django', 'PostgreSQL', 'REST API', 'Docker'],
                'description': '<p>We are looking for an experienced Python developer to join our backend team. You will be working on building scalable web applications and APIs.</p>',
                'requirements': '<ul><li>5+ years of Python development</li><li>Strong knowledge of Django framework</li><li>Experience with PostgreSQL</li><li>Docker and Kubernetes knowledge</li></ul>',
            },
            {
                'job_title': 'Machine Learning Engineer',
                'company': 'AI Solutions Ltd',
                'location': 'New York, NY',
                'salary_min': 140000,
                'salary_max': 200000,
                'job_type': 'full_time',
                'experience_required': '3-5 years',
                'key_skills': ['Python', 'TensorFlow', 'PyTorch', 'Machine Learning', 'Deep Learning', 'NLP'],
                'description': '<p>Join our AI team to develop cutting-edge machine learning models for natural language processing and computer vision applications.</p>',
                'requirements': '<ul><li>Strong background in ML/DL</li><li>Experience with TensorFlow or PyTorch</li><li>Knowledge of NLP techniques</li><li>MS or PhD in Computer Science preferred</li></ul>',
            },
            {
                'job_title': 'Full Stack Developer',
                'company': 'StartupXYZ',
                'location': 'Austin, TX',
                'salary_min': 90000,
                'salary_max': 130000,
                'job_type': 'full_time',
                'experience_required': '2-4 years',
                'key_skills': ['JavaScript', 'React', 'Angular', 'Node.js', 'MongoDB', 'Express'],
                'description': '<p>We need a full-stack developer who can work on both frontend and backend. You will be building modern web applications using the latest technologies.</p>',
                'requirements': '<ul><li>Proficient in JavaScript/TypeScript</li><li>Experience with React or Angular</li><li>Node.js and Express knowledge</li><li>Database design skills</li></ul>',
            },
            {
                'job_title': 'Data Scientist',
                'company': 'DataCorp Analytics',
                'location': 'Seattle, WA',
                'salary_min': 110000,
                'salary_max': 160000,
                'job_type': 'full_time',
                'experience_required': '3+ years',
                'key_skills': ['Python', 'R', 'SQL', 'Machine Learning', 'Statistics', 'Data Visualization'],
                'description': '<p>Looking for a data scientist to analyze large datasets and build predictive models. You will work closely with product teams to drive data-driven decisions.</p>',
                'requirements': '<ul><li>Strong statistical knowledge</li><li>Experience with Python and R</li><li>SQL proficiency</li><li>Data visualization skills (Tableau, PowerBI)</li></ul>',
            },
            {
                'job_title': 'DevOps Engineer',
                'company': 'CloudTech Systems',
                'location': 'Boston, MA',
                'salary_min': 100000,
                'salary_max': 150000,
                'job_type': 'full_time',
                'experience_required': '4+ years',
                'key_skills': ['AWS', 'Docker', 'Kubernetes', 'CI/CD', 'Terraform', 'Python'],
                'description': '<p>We are seeking a DevOps engineer to manage our cloud infrastructure and implement CI/CD pipelines for our applications.</p>',
                'requirements': '<ul><li>Experience with AWS services</li><li>Kubernetes orchestration</li><li>Infrastructure as Code (Terraform)</li><li>CI/CD pipeline implementation</li></ul>',
            },
            {
                'job_title': 'Frontend Developer - React',
                'company': 'WebDev Studios',
                'location': 'Remote',
                'salary_min': 85000,
                'salary_max': 120000,
                'job_type': 'full_time',
                'experience_required': '2-3 years',
                'key_skills': ['React', 'JavaScript', 'TypeScript', 'CSS', 'HTML5', 'Redux'],
                'description': '<p>Remote position for a React developer to build beautiful and performant user interfaces for our web applications.</p>',
                'requirements': '<ul><li>Strong React knowledge</li><li>TypeScript proficiency</li><li>Responsive design skills</li><li>State management (Redux/Context API)</li></ul>',
            },
            {
                'job_title': 'Backend Engineer - Java',
                'company': 'Enterprise Solutions Inc',
                'location': 'Chicago, IL',
                'salary_min': 110000,
                'salary_max': 155000,
                'job_type': 'full_time',
                'experience_required': '5+ years',
                'key_skills': ['Java', 'Spring Boot', 'Microservices', 'MySQL', 'Kafka', 'Redis'],
                'description': '<p>Join our backend team to develop enterprise-grade microservices using Java and Spring Boot.</p>',
                'requirements': '<ul><li>Expert Java knowledge</li><li>Spring Boot framework</li><li>Microservices architecture</li><li>Message queuing (Kafka/RabbitMQ)</li></ul>',
            },
            {
                'job_title': 'AI Research Scientist',
                'company': 'Research Labs AI',
                'location': 'Cambridge, MA',
                'salary_min': 150000,
                'salary_max': 220000,
                'job_type': 'full_time',
                'experience_required': 'PhD preferred',
                'key_skills': ['Deep Learning', 'Computer Vision', 'NLP', 'PyTorch', 'Research', 'Publications'],
                'description': '<p>Research position focused on advancing the state-of-the-art in artificial intelligence, computer vision, and natural language understanding.</p>',
                'requirements': '<ul><li>PhD in CS, ML, or related field</li><li>Published papers in top conferences</li><li>Strong mathematical background</li><li>Experience with PyTorch/TensorFlow</li></ul>',
            },
            {
                'job_title': 'Mobile App Developer - iOS',
                'company': 'MobileFirst Inc',
                'location': 'Los Angeles, CA',
                'salary_min': 95000,
                'salary_max': 140000,
                'job_type': 'full_time',
                'experience_required': '3+ years',
                'key_skills': ['Swift', 'iOS', 'SwiftUI', 'Core Data', 'REST API', 'Git'],
                'description': '<p>We are looking for an iOS developer to build native mobile applications using Swift and SwiftUI.</p>',
                'requirements': '<ul><li>Swift programming</li><li>iOS SDK knowledge</li><li>SwiftUI framework</li><li>App Store deployment experience</li></ul>',
            },
            {
                'job_title': 'Database Administrator',
                'company': 'Data Management Co',
                'location': 'Denver, CO',
                'salary_min': 90000,
                'salary_max': 130000,
                'job_type': 'full_time',
                'experience_required': '4+ years',
                'key_skills': ['PostgreSQL', 'MySQL', 'Database Design', 'Performance Tuning', 'Backup & Recovery'],
                'description': '<p>Looking for a DBA to manage and optimize our database systems, ensure data integrity, and implement backup strategies.</p>',
                'requirements': '<ul><li>Expert PostgreSQL/MySQL knowledge</li><li>Performance optimization</li><li>Backup and disaster recovery</li><li>Database security</li></ul>',
            },
        ]
        
        created_count = 0
        for job_data in jobs_data:
            job, created = Job.objects.get_or_create(
                job_title=job_data['job_title'],
                company=job_data['company'],
                defaults=job_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.job_title} at {job.company}'))
            else:
                self.stdout.write(self.style.WARNING(f'- Exists: {job.job_title} at {job.company}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nCompleted! Created {created_count} new jobs.'))
        self.stdout.write(self.style.SUCCESS('Note: Embeddings are automatically generated on save.'))
