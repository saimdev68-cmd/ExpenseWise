document.addEventListener("DOMContentLoaded", () => {
    
    const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("sidebarToggle");
    const mainContent = document.getElementById("mainContent");

    // --- 1. HIGHLIGHT ACTIVE NAV ITEM ---
    const currentUrl = window.location.href;
    const navLinks = document.querySelectorAll("nav ul li a");

    navLinks.forEach(link => {
        // If current window path matches link href attributes, mark it active
        if (currentUrl === link.href || currentUrl.startsWith(link.href + '?')) {
            link.classList.add("active");
        }
    });

    // --- 2. COLLAPSIBLE PERSISTENT SIDEBAR DOCK ---
    if (toggleBtn && sidebar && mainContent) {
        toggleBtn.addEventListener("click", () => {
            const willCollapse = !sidebar.classList.contains("collapsed");
            
            if (willCollapse) {
                sidebar.classList.add("collapsed");
                mainContent.classList.add("expanded");
            } else {
                sidebar.classList.remove("collapsed");
                mainContent.classList.remove("expanded");
            }
            
            // Save state to local storage so navigation won't break configuration
            localStorage.setItem("sidebarCollapsed", willCollapse);
        });
    }

    // --- 3. TOAST AUTO-DISMISS & MANUAL CLOSE ---
    const toasts = document.querySelectorAll(".toast");

    toasts.forEach((toast) => {
        const dismissToast = () => {
            toast.style.opacity = "0";
            setTimeout(() => {
                toast.remove();
            }, 300);
        };

        const closeBtn = toast.querySelector(".toast-close");
        if (closeBtn) {
            closeBtn.addEventListener("click", dismissToast);
        }

        // Auto-close after 10 seconds
        setTimeout(dismissToast, 10000);
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const toggles = document.querySelectorAll('.password-toggle-hook');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target-id');
            const passwordField = document.getElementById(targetId);
            
            // Define the SVG icon strings
            const eyeOpenIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;

            const eyeSlashIcon = `
                <svg xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round">
                    <!-- The eye -->
                    <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0" />
                    <!-- The circle pupil -->
                    <circle cx="12" cy="12" r="3" />
                    <!-- The diagonal slash (Left-Top to Right-Bottom) -->
                    <path d="m2.5 2.5 19 19" />
                </svg>
                `;

            if (passwordField) {
                if (passwordField.type === "password") {
                    passwordField.type = "text";
                    this.innerHTML = eyeSlashIcon; // Shows the line through the eye
                } else {
                    passwordField.type = "password";
                    this.innerHTML = eyeOpenIcon;  // Shows the open eye
                }
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    // Intercept clicks on links designated for smooth SPA-like transitions
    document.body.addEventListener("click", function (e) {
        const link = e.target.closest("a");
        
        // Check if it's an internal link and has a data-spa attribute (or apply to all internal links)
        if (link && link.hasAttribute("data-spa") && link.href.startsWith(window.location.origin)) {
            e.preventDefault();
            
            const targetUrl = link.href;

            fetch(targetUrl, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.text())
            .then(html => {
                // Parse the incoming HTML response
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, "text/html");
                
                // Extract the new content container (e.g., .auth-card or a wrapper element)
                const newContent = doc.querySelector(".auth-container");
                const currentContent = document.querySelector(".auth-container");

                if (newContent && currentContent) {
                    // Swap the content seamlessly
                    currentContent.innerHTML = newContent.innerHTML;
                    
                    // Update browser history URL without reloading
                    history.pushState({ path: targetUrl }, "", targetUrl);
                    
                    // Optional: Update document title if provided in the fetched page
                    const newTitle = doc.querySelector("title");
                    if (newTitle) document.title = newTitle.textContent;
                } else {
                    // Fallback to normal navigation if container layout doesn't match
                    window.location.href = targetUrl;
                }
            })
            .catch(error => {
                console.error("Navigation error:", error);
                window.location.href = targetUrl; // Fallback on error
            });
        }
    });

    // Handle browser back/forward buttons smoothly
    window.addEventListener("popstate", function () {
        window.location.reload(); // Simple fallback for history back/forward state changes
    });
});