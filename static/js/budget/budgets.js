// ============================================
// BUDGET MANAGEMENT - Complete JavaScript
// ============================================

(function() {
    'use strict';

    // DOM Elements
    const categoryInput = document.getElementById('category');
    const monthInput = document.getElementById('month');
    const yearInput = document.getElementById('year');
    const sortInput = document.getElementById('sort');
    const resetButton = document.getElementById('reset-filters');
    const budgetResultContainer = document.getElementById('budget-result');
    
    // State
    let currentPage = 1;
    let isDeleting = false;
    let timeout;

    // ============================================
    // Event Listeners
    // ============================================
    
    // Filter change events
    if (categoryInput) {
        categoryInput.addEventListener('change', () => {
            currentPage = 1;
            searchBudget();
        });
    }
    
    if (monthInput) {
        monthInput.addEventListener('change', () => {
            currentPage = 1;
            searchBudget();
        });
    }
    
    if (yearInput) {
        yearInput.addEventListener('change', () => {
            currentPage = 1;
            searchBudget();
        });
    }
    
    if (sortInput) {
        sortInput.addEventListener('change', () => {
            currentPage = 1;
            searchBudget();
        });
    }
    
    // Reset filters
    if (resetButton) {
        resetButton.addEventListener('click', (e) => {
            e.preventDefault();
            const form = document.getElementById('filter-form');
            if (form) {
                form.reset();
            }
            currentPage = 1;
            searchBudget();
        });
    }

    // ============================================
    // Core Functions
    // ============================================
    
    /**
     * Search/Filter budgets with current parameters
     */
    async function searchBudget() {
        try {
            const form = document.getElementById('filter-form');
            if (!form) return;
            
            const params = new URLSearchParams(new FormData(form));
            params.set('page', currentPage);
            
            console.log("Searching with params:", params.toString()); // Debug log
            
            const response = await fetch(
                `${window.location.pathname}?${params.toString()}`,
                {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                }
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Update the DOM
            if (budgetResultContainer) {
                budgetResultContainer.innerHTML = data.html;
            }
            
            // Re-initialize components
            reinitializeComponents();
            
        } catch (error) {
            console.error('Error searching budgets:', error);
        }
    }

    /**
     * Handle pagination clicks
     */
    function bindPagination() {
        document.querySelectorAll('.pagination-buttons a').forEach(link => {
            // Remove old listeners to prevent duplicates
            link.removeEventListener('click', handlePaginationClick);
            link.addEventListener('click', handlePaginationClick);
        });
    }

    /**
     * Handles pagination link clicks
     */
    async function handlePaginationClick(e) {
        e.preventDefault();
        
        const url = new URL(this.href);
        const page = url.searchParams.get('page');
        
        if (page) {
            currentPage = parseInt(page);
            await searchBudget();
        }
    }

    /**
     * Handle delete functionality with page redirection
     */
    function bindDelete() {
        document.querySelectorAll('.inline-delete-form').forEach(form => {
            // Remove existing listeners to prevent duplicates
            form.removeEventListener('submit', handleDelete);
            form.addEventListener('submit', handleDelete);
        });
    }

    /**
     * Delete handler function with proper page handling
     */
    async function handleDelete(e) {
        e.preventDefault();
        
        // Prevent multiple simultaneous deletions
        if (isDeleting) return;
        
        if (!confirm('Are you sure you want to delete this budget record?')) {
            return;
        }
        
        const form = this;
        isDeleting = true;
        
        try {
            // Get current filter parameters to pass to the delete view
            const filterForm = document.getElementById('filter-form');
            const params = new URLSearchParams(new FormData(filterForm));
            
            // Add current page to params
            params.set('page', currentPage);
            
            // Build the delete URL with filter parameters
            const deleteUrl = `${form.action}?${params.toString()}`;
            
            const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]");
            if (!csrfToken) {
                throw new Error('CSRF token not found');
            }
            
            const response = await fetch(deleteUrl, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken.value
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Get the total count and items per page from the response
                const totalItems = data.total_count || 0;
                const itemsPerPage = data.per_page || 10;
                const lastPage = Math.ceil(totalItems / itemsPerPage);
                
                console.log("Before update - Current page:", currentPage, "Last page:", lastPage);
                
                // If we're on a page that no longer exists, go to the last valid page
                if (currentPage > lastPage) {
                    currentPage = Math.max(1, lastPage);
                }
                
                // If current page is 0 or undefined, set to 1
                if (!currentPage || currentPage < 1) {
                    currentPage = 1;
                }
                
                console.log("After update - Current page:", currentPage);
                
                // Refresh the budget list
                await searchBudget();
                
            } else {
                console.error('Delete failed:', data.message || 'Unknown error');
                alert('Failed to delete the budget record. Please try again.');
            }
            
        } catch (error) {
            console.error('Error deleting budget:', error);
            alert('An error occurred while deleting the record. Please try again.');
        } finally {
            isDeleting = false;
        }
    }

    /**
     * Reinitialize all dynamic components after DOM update
     */
    function reinitializeComponents() {
        // Recreate Lucide icons
        if (window.lucide) {
            lucide.createIcons();
        }
        
        // Re-bind event listeners
        bindDelete();
        bindPagination();
        
        // Re-bind any other dynamic elements
        bindDynamicElements();
    }

    /**
     * Bind other dynamic elements (if any)
     */
    function bindDynamicElements() {
        // Add any additional dynamic element bindings here
        // Example: tooltips, modals, etc.
    }

    /**
     * Get current page information
     */
    function getCurrentPageInfo() {
        const paginationInfo = document.querySelector('.pagination-info');
        if (!paginationInfo) {
            return { current: 1, total: 1 };
        }
        
        const match = paginationInfo.textContent.match(/Page\s+(\d+)\s+of\s+(\d+)/);
        if (match) {
            return {
                current: parseInt(match[1]),
                total: parseInt(match[2])
            };
        }
        
        return { current: 1, total: 1 };
    }

    // ============================================
    // Keyboard Shortcuts
    // ============================================
    
    document.addEventListener('keydown', (e) => {
        // Ctrl+Shift+R to reset filters
        if (e.ctrlKey && e.shiftKey && (e.key === 'r' || e.key === 'R')) {
            e.preventDefault();
            if (resetButton) {
                resetButton.click();
            }
        }
        
        // Escape to cancel any operation
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                const closeBtn = modal.querySelector('.btn-close');
                if (closeBtn) closeBtn.click();
            });
        }
    });

    // ============================================
    // Initialization
    // ============================================
    
    /**
     * Initialize the budget management system
     */
    function init() {
        // Initial bindings
        reinitializeComponents();
        
        console.log('Budget Management System initialized');
    }

    // ============================================
    // Expose functions globally if needed
    // ============================================
    
    window.BudgetManager = {
        searchBudget,
        bindDelete,
        bindPagination,
        reinitializeComponents,
        getCurrentPageInfo
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();