import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { JobService } from './services/job.service';
import { Job } from './models/job.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent implements OnInit {
  title = 'Job Search with Semantic AI';
  searchQuery = '';
  jobs: Job[] = [];
  loading = false;
  error: string | null = null;
  searchMode = false;

  // Pagination state
  currentPage = 1;
  pageSize = 25;
  totalResults = 0;
  totalPages = 0;
  hasNext = false;
  hasPrevious = false;

  // Expose Math to template
  Math = Math;

  constructor(
    private jobService: JobService,
    private cdr: ChangeDetectorRef
  ) { }

  ngOnInit() {
    console.log('AppComponent initialized');
    // Load all jobs initially
    this.loadAllJobs();
  }

  loadAllJobs() {
    console.log('loadAllJobs called, page:', this.currentPage);
    this.loading = true;
    this.searchMode = false;

    this.jobService.getAllJobs(this.currentPage, this.pageSize).subscribe({
      next: (response) => {
        console.log('Received paginated jobs:', response);
        this.jobs = response.results;
        this.totalResults = response.total_results;
        this.totalPages = response.total_pages;
        this.hasNext = response.has_next;
        this.hasPrevious = response.has_previous;
        this.loading = false;
        console.log('Jobs loaded:', this.jobs.length, 'of', this.totalResults);
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.error = 'Failed to load jobs. Please ensure the backend server is running.';
        this.loading = false;
        console.error('Load jobs error:', err);
        this.cdr.detectChanges();
      }
    });
  }

  onSearchClick() {
    if (!this.searchQuery.trim()) {
      this.loadAllJobs();
      return;
    }

    this.currentPage = 1; // Reset to first page on new search
    this.performSearch();
  }

  performSearch() {
    console.log('Searching for:', this.searchQuery, 'Page:', this.currentPage);
    this.loading = true;
    this.searchMode = true;
    this.error = null;

    this.jobService.searchJobs(this.searchQuery, this.currentPage, this.pageSize).subscribe({
      next: (response) => {
        console.log('Search response:', response);
        this.jobs = response.results;
        this.totalResults = response.total_results;
        this.totalPages = response.total_pages;
        this.hasNext = response.has_next;
        this.hasPrevious = response.has_previous;
        this.loading = false;
        this.cdr.detectChanges();
        console.log('Jobs loaded:', this.jobs.length, 'Total:', this.totalResults);
      },
      error: (err) => {
        this.loading = false;
        this.error = 'Failed to fetch search results. Please try again.';
        console.error('Search error:', err);
        this.cdr.detectChanges();
      }
    });
  }

  goToPage(page: number) {
    if (page < 1 || page > this.totalPages) return;
    this.currentPage = page;

    if (this.searchMode && this.searchQuery.trim()) {
      this.performSearch();
    } else {
      // For "all jobs" view, we don't paginate on backend yet
      // This would require updating the getAllJobs API
      this.loadAllJobs();
    }
  }

  nextPage() {
    if (this.hasNext) {
      this.goToPage(this.currentPage + 1);
    }
  }

  previousPage() {
    if (this.hasPrevious) {
      this.goToPage(this.currentPage - 1);
    }
  }

  getPageNumbers(): number[] {
    const pages = [];
    const maxPagesToShow = 5;
    let startPage = Math.max(1, this.currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = Math.min(this.totalPages, startPage + maxPagesToShow - 1);

    if (endPage - startPage < maxPagesToShow - 1) {
      startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    return pages;
  }

  clearSearch() {
    this.searchQuery = '';
    this.searchMode = false;
    this.currentPage = 1;
    this.loadAllJobs();
  }

  stripHtml(html: string): string {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
  }
}
