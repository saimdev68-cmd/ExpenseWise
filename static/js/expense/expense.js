const searchInput = document.getElementById('search');
const categoryInput = document.getElementById('category');
const paymentInput = document.getElementById('payment_method');
const periodInput = document.getElementById('period');
const fromdateInput = document.getElementById('start_date');
const todateInput = document.getElementById('end_date');
const minamountInput = document.getElementById('min_amount');
const maxamountInput = document.getElementById('max_amount');
const sortInput = document.getElementById('sort');
const resetButton = document.getElementById("reset-filters");
let currentPage = 1;
let timeout;

// Search input with debounce
searchInput.addEventListener('input', () => {
    currentPage = 1;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        searchExpense();
    }, 400);
});

// Amount inputs with debounce
minamountInput.addEventListener('input', () => {
    currentPage = 1;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        searchExpense();
    }, 400);
});

maxamountInput.addEventListener('input', () => {
    currentPage = 1;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        searchExpense();
    }, 400);
});

// Filter change events
categoryInput.addEventListener('change', () => {
    currentPage = 1;
    searchExpense();
});

paymentInput.addEventListener('change', () => {
    currentPage = 1;
    searchExpense();
});

periodInput.addEventListener('change', () => {
    currentPage = 1;
    searchExpense();
});

fromdateInput.addEventListener('change', () => {
    currentPage = 1;
    searchExpense();
});

todateInput.addEventListener('change', () => {
    currentPage = 1;
    searchExpense();
});

sortInput.addEventListener('change', () => {
    currentPage = 1;
    searchExpense();
});

/**
 * Main search function that fetches filtered and paginated results
 */
async function searchExpense() {
    const form = document.getElementById('filter-form');
    const params = new URLSearchParams(new FormData(form));
    params.set('page', currentPage);
    
    console.log("Searching with params:", params.toString()); // Debug log
    
    try {
        const response = await fetch(
            `${window.location.pathname}?${params.toString()}`,
            {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }
        );
        const data = await response.json();
        document.getElementById('expense-results').innerHTML = data.html;
        if (window.lucide) {
            lucide.createIcons();
        }
        bindPagination();
        bindDelete();
    } catch (error) {
        console.error("Search error:", error);
    }
}

/**
 * Binds pagination click events to all pagination links
 */
function bindPagination() {
    document.querySelectorAll(".pagination-buttons a").forEach(link => {
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
    currentPage = parseInt(url.searchParams.get('page')) || 1;
    
    // Preserve all filter parameters
    const form = document.getElementById('filter-form');
    const params = new URLSearchParams(new FormData(form));
    params.set('page', currentPage);
    
    try {
        const response = await fetch(
            `${window.location.pathname}?${params.toString()}`,
            {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }
        );
        const data = await response.json();
        document.getElementById('expense-results').innerHTML = data.html;
        if (window.lucide) {
            lucide.createIcons();
        }
        bindPagination();
        bindDelete();
    } catch (error) {
        console.error("Pagination error:", error);
    }
}

/**
 * Binds delete events to all delete forms
 */
function bindDelete() {
    document.querySelectorAll(".inline-delete-form").forEach(form => {
        // Remove old listeners to prevent duplicates
        form.removeEventListener('submit', handleDeleteSubmit);
        form.addEventListener('submit', handleDeleteSubmit);
    });
}

/**
 * Handles delete form submissions
 */
async function handleDeleteSubmit(e) {
    e.preventDefault();
    
    if (!confirm("Are you sure you want to delete this expense record?")) {
        return;
    }
    
    const form = this;
    
    // Get current filter parameters to pass to the delete view
    const filterForm = document.getElementById('filter-form');
    const params = new URLSearchParams(new FormData(filterForm));
    
    // Build the delete URL with filter parameters
    const deleteUrl = `${form.action}?${params.toString()}`;
    
    try {
        const response = await fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': form.querySelector("[name=csrfmiddlewaretoken]").value
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
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
            
            // Now search with the updated page number
            await searchExpense();
        } else {
            alert("Failed to delete the expense record. Please try again.");
        }
    } catch (error) {
        console.error("Delete error:", error);
        alert("An error occurred while deleting the record. Please try again.");
    }
}

// Reset filters
resetButton.addEventListener('click', (e) => {
    e.preventDefault();
    const form = document.getElementById('filter-form');
    form.reset();
    currentPage = 1;
    searchExpense();
});

// Initialize event listeners
bindDelete();
bindPagination();

// Log that the script has loaded
console.log("Expense.js loaded successfully");