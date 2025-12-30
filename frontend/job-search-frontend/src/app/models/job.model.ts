export interface Job {
    id: string;
    job_title: string;
    company: string;
    location: string;
    salary_min: number;
    salary_max: number;
    salary_currency: string;
    job_type: string;
    experience_required: string;
    key_skills: string[];
    description: string;
    requirements: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    distance?: number;
    similarity?: number;
}

export interface SearchResponse {
    query: string;
    page: number;
    page_size: number;
    total_results: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
    results: Job[];
}
