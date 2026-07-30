// ============================================
// NOTIFICATION MANAGEMENT - Complete JavaScript
// ============================================

(function() {
    'use strict';

    // DOM Elements
    const resultContainer = document.getElementById('notification-results');
    const markAllReadBtn = document.getElementById('markAllReadBtn');
    
    // State
    let isDeleting = false;
    let isMarkingAll = false;

    // ============================================
    // Core Functions
    // ============================================
    
    /**
     * Handle delete functionality
     */
    function bindDelete() {
        document.querySelectorAll('.inline-delete-form').forEach(form => {
            // Remove existing listeners to prevent duplicates
            form.removeEventListener('submit', handleDelete);
            form.addEventListener('submit', handleDelete);
        });
    }

    /**
     * Delete handler function
     */
    async function handleDelete(e) {
        e.preventDefault();
        
        // Prevent multiple simultaneous deletions
        if (isDeleting) return;
        
        if (!confirm('Are you sure you want to delete this notification?')) {
            return;
        }
        
        const form = this;
        isDeleting = true;
        
        // Show loading state on the delete button
        const button = form.querySelector('button');
        const originalText = button.innerHTML;
        button.innerHTML = '...';
        button.disabled = true;
        
        try {
            const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]");
            if (!csrfToken) {
                throw new Error('CSRF token not found');
            }
            
            const response = await fetch(form.action, {
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
                // Check if there are any notifications left
                if (data.has_notifications === false) {
                    // No notifications left, refresh the entire list to show empty state
                    await refreshNotifications();
                } else {
                    // Remove the notification item from the DOM with animation
                    const notificationItem = form.closest('.notification-item');
                    if (notificationItem) {
                        // Add fade out animation
                        notificationItem.style.transition = 'all 0.3s ease';
                        notificationItem.style.opacity = '0';
                        notificationItem.style.transform = 'translateX(-20px)';
                        
                        // Remove after animation
                        setTimeout(() => {
                            notificationItem.remove();
                            
                            // Update the "Mark All As Read" button if no notifications left
                            updateMarkAllButton();
                        }, 300);
                    }
                }
                
                console.log('Notification deleted successfully');
                
            } else {
                console.error('Delete failed:', data.message || 'Unknown error');
                alert('Failed to delete the notification. Please try again.');
                // Restore button
                button.innerHTML = originalText;
                button.disabled = false;
            }
            
        } catch (error) {
            console.error('Error deleting notification:', error);
            alert('An error occurred while deleting the notification. Please try again.');
            // Restore button
            button.innerHTML = originalText;
            button.disabled = false;
        } finally {
            isDeleting = false;
        }
    }

    /**
     * Handle "Mark All As Read" functionality
     */
    async function handleMarkAllRead() {
        // Prevent multiple simultaneous requests
        if (isMarkingAll) return;
        
        // Check if there are any unread notifications
        const unreadItems = document.querySelectorAll('.notification-item:not([data-read="true"])');
        if (unreadItems.length === 0) {
            alert('All notifications are already read.');
            return;
        }
        
        if (!confirm(`Mark all ${unreadItems.length} unread notifications as read?`)) {
            return;
        }
        
        isMarkingAll = true;
        
        // Show loading state on the button
        if (markAllReadBtn) {
            const originalText = markAllReadBtn.innerHTML;
            markAllReadBtn.innerHTML = '<i data-lucide="loader" class="icon-sm" style="animation: spin 1s linear infinite;"></i> Marking...';
            markAllReadBtn.disabled = true;
            
            // Recreate the loading icon
            if (window.lucide) {
                lucide.createIcons();
            }
        }
        
        try {
            const response = await fetch('/notifications/read-all/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Update the DOM with the new HTML
                if (resultContainer) {
                    resultContainer.innerHTML = data.html;
                }
                
                // Re-initialize components
                reinitializeComponents();
                
                // Show success message
                console.log(`${data.updated_count} notifications marked as read`);
                
                // Update the mark all button
                updateMarkAllButton();
                
            } else {
                console.error('Mark all read failed:', data.message || 'Unknown error');
                alert('Failed to mark all notifications as read. Please try again.');
            }
            
        } catch (error) {
            console.error('Error marking all as read:', error);
            alert('An error occurred while marking all notifications as read. Please try again.');
        } finally {
            isMarkingAll = false;
            
            // Restore button state
            if (markAllReadBtn) {
                const hasUnread = document.querySelectorAll('.notification-item:not([data-read="true"])').length > 0;
                if (hasUnread) {
                    markAllReadBtn.innerHTML = '<i data-lucide="check" class="icon-sm"></i> Mark All As Read';
                    markAllReadBtn.disabled = false;
                } else {
                    markAllReadBtn.style.display = 'none';
                }
                
                // Recreate icons
                if (window.lucide) {
                    lucide.createIcons();
                }
            }
        }
    }

    /**
     * Refresh notifications (for when all are deleted)
     */
    async function refreshNotifications() {
        try {
            const response = await fetch(
                window.location.pathname,
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
            if (resultContainer) {
                resultContainer.innerHTML = data.html;
            }
            
            // Re-initialize components
            reinitializeComponents();
            
        } catch (error) {
            console.error('Error refreshing notifications:', error);
            // Fallback: reload the page
            window.location.reload();
        }
    }

    /**
     * Update the "Mark All As Read" button visibility
     */
    function updateMarkAllButton() {
        const remainingItems = document.querySelectorAll('.notification-item').length;
        const unreadItems = document.querySelectorAll('.notification-item:not([data-read="true"])').length;
        const markAllButton = document.getElementById('markAllReadBtn');
        
        if (markAllButton) {
            if (remainingItems === 0 || unreadItems === 0) {
                markAllButton.style.display = 'none';
            } else {
                markAllButton.style.display = 'inline-flex';
                // Update button text with count
                markAllButton.innerHTML = `<i data-lucide="check" class="icon-sm"></i> Mark All As Read (${unreadItems})`;
                
                // Recreate icons
                if (window.lucide) {
                    lucide.createIcons();
                }
            }
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
        
        // Re-bind mark all read button
        if (markAllReadBtn) {
            markAllReadBtn.removeEventListener('click', handleMarkAllRead);
            markAllReadBtn.addEventListener('click', handleMarkAllRead);
        }
        
        // Update mark all button state
        updateMarkAllButton();
    }

    // ============================================
    // CSS Animation for loading spinner
    // ============================================
    
    // Add spin animation if not already present
    if (!document.getElementById('notification-spin-style')) {
        const style = document.createElement('style');
        style.id = 'notification-spin-style';
        style.textContent = `
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    // ============================================
    // Initialization
    // ============================================
    
    /**
     * Initialize the notification management system
     */
    function init() {
        // Initial bindings
        reinitializeComponents();
        
        console.log('Notification Management System initialized');
    }

    // ============================================
    // Expose functions globally if needed
    // ============================================
    
    window.NotificationManager = {
        bindDelete,
        refreshNotifications,
        reinitializeComponents,
        handleMarkAllRead,
        updateMarkAllButton
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();