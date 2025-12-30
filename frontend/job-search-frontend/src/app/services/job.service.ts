import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Job, SearchResponse } from '../models/job.model';

@Injectable({
    providedIn: 'root'
})
export class JobService {
    private apiUrl = 'http://localhost:8000/api/jobs';

    constructor(private http: HttpClient) { }

    /**
     * Search for jobs using semantic search with pagination
     * @param query Search query string
     * @param page Page number (default: 1)
     * @param pageSize Results per page (default: 25)
     * @param threshold Similarity threshold (0-1)
     */
    searchJobs(query: string, page: number = 1, pageSize: number = 25, threshold: number = 0.85): Observable<SearchResponse> {
        const params = new HttpParams()
            .set('q', query)
            .set('page', page.toString())
            .set('page_size', pageSize.toString())
            .set('threshold', threshold.toString());

        return this.http.get<SearchResponse>(`${this.apiUrl}/search/`, { params });
    }

    /**
     * Get all jobs with pagination
     * @param page Page number (default: 1)
     * @param pageSize Results per page (default: 25)
     */
    getAllJobs(page: number = 1, pageSize: number = 25): Observable<SearchResponse> {
        const params = new HttpParams()
            .set('page', page.toString())
            .set('page_size', pageSize.toString());
        return this.http.get<SearchResponse>(this.apiUrl + '/', { params });
    }

    /**
     * Get a single job by ID
     * @param id Job UUID
     */
    getJob(id: string): Observable<Job> {
        return this.http.get<Job>(`${this.apiUrl}/${id}/`);
    }

    /**
     * Create a new job
     * @param job Job data
     */
    createJob(job: Partial<Job>): Observable<Job> {
        return this.http.post<Job>(`${this.apiUrl}/`, job);
    }
}
