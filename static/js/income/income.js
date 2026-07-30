const searchInput = document.getElementById('search');
const categoryInput = document.getElementById("category");
const sortInput = document.getElementById('sort');
const periodInput = document.getElementById('period');
const fromdateInput = document.getElementById('from_date');
const todateInput = document.getElementById('to_date');
const minamountInput = document.getElementById('min_amount');
const maxamountInput = document.getElementById('max_amount');
let currentPage = 1;
let timeout;

// Search input with debounce
searchInput.addEventListener('input', () => {
    currentPage = 1;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        searchIncome();
    }, 400);
});

// Filter change events
categoryInput.addEventListener('change', () => {
    currentPage = 1;
    searchIncome();
});

sortInput.addEventListener('change', () => {
    currentPage = 1;
    searchIncome();
});

periodInput.addEventListener('change', () => {
    currentPage = 1;
    searchIncome();
});

fromdateInput.addEventListener('change', () => {
    currentPage = 1;
    searchIncome();
});

todateInput.addEventListener('change', () => {
    currentPage = 1;
    searchIncome();
});

// Amount inputs with debounce
minamountInput.addEventListener('input', () => {
    currentPage = 1;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        searchIncome();
    }, 400);
});

maxamountInput.addEventListener('input', () => {
    currentPage = 1;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        searchIncome();
    }, 400);
});

/**
 * Binds pagination click events to all pagination links
 */
function bindPagination() {
    document.querySelectorAll(".pagination-buttons a").forEach(link => {
        // Remove old listeners to prevent duplicates
        link.removeEventListener("click", handlePaginationClick);
        link.addEventListener("click", handlePaginationClick);
    });
}

/**
 * Handles pagination link clicks
 */
async function handlePaginationClick(e) {
    e.preventDefault();
    const url = new URL(this.href);
    currentPage = parseInt(url.searchParams.get("page")) || 1;
    
    // Preserve all filter parameters
    const form = document.getElementById("filter-form");
    const params = new URLSearchParams(new FormData(form));
    params.set("page", currentPage);
    
    try {
        const response = await fetch(
            `${window.location.pathname}?${params.toString()}`,
            {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            }
        );
        const data = await response.json();
        document.getElementById("income-results").innerHTML = data.html;
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
 * Main search function that fetches filtered and paginated results
 */
async function searchIncome() {
    const form = document.getElementById("filter-form");
    const params = new URLSearchParams(new FormData(form));
    params.set("page", currentPage);
    
    
    
    try {
        const response = await fetch(
            `${window.location.pathname}?${params.toString()}`,
            {
                headers: {
                    'X-Requested-With': "XMLHttpRequest"
                }
            }
        );
        const data = await response.json();
        document.getElementById('income-results').innerHTML = data.html;
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
 * Binds delete events to all delete forms
 */
function bindDelete() {
    document.querySelectorAll(".inline-delete-form").forEach(form => {
        // Remove old listeners to prevent duplicates
        form.removeEventListener("submit", handleDeleteSubmit);
        form.addEventListener("submit", handleDeleteSubmit);
    });
}

/**
 * Handles delete form submissions
 */
async function handleDeleteSubmit(e) {
    e.preventDefault();

    if (!confirm("Are you sure you want to delete this income record?")) {
        return;
    }

    const form = this;
    
    // Get current filter parameters to pass to the delete view
    const filterForm = document.getElementById("filter-form");
    const params = new URLSearchParams(new FormData(filterForm));
    
    // Build the delete URL with filter parameters
    const deleteUrl = `${form.action}?${params.toString()}`;
    
    try {
        const response = await fetch(deleteUrl, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value
            }
        });

        const data = await response.json();

        if (data.success) {
            const totalItems = data.total_count || 0;
            const itemsPerPage = data.per_page || 10;
            const lastPage = Math.ceil(totalItems / itemsPerPage);
            
            
            
            // If we're on a page that no longer exists, go to the last valid page
            if (currentPage > lastPage) {
                currentPage = Math.max(1, lastPage);
            }
            
            // If current page is 0 or undefined, set to 1
            if (!currentPage || currentPage < 1) {
                currentPage = 1;
            }
            
            
            
            // Now search with the updated page number
            await searchIncome();
        } else {
            alert("Failed to delete the income record. Please try again.");
        }
    } catch (error) {
        console.error("Delete error:", error);
        alert("An error occurred while deleting the record. Please try again.");
    }
}

/**
 * Resets all filters to their default values
 */
const resetButton = document.getElementById("reset-filters");
if (resetButton) {
    resetButton.addEventListener("click", (e) => {
        e.preventDefault();
        const form = document.getElementById("filter-form");
        form.reset();
        currentPage = 1;
        searchIncome();
    });
}

// Initialize event listeners
bindDelete();
bindPagination();

