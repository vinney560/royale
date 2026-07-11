(function() {

    // ============================================================
    // LOADING OVERLAY
    // ============================================================

    // Create overlay elements
    var overlay = document.createElement('div');
    overlay.id = 'page-loader-overlay';
    overlay.innerHTML = `
        <div class="loader-container">
            <div class="loader-spinner">
                <div class="loader-ring"></div>
                <div class="loader-ring"></div>
                <div class="loader-ring"></div>
                <div class="loader-logo">R</div>
            </div>
            <div class="loader-text">Loading...</div>
        </div>
    `;
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(7, 10, 12, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        z-index: 9999;
        display: none;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        transition: opacity 0.4s ease;
        opacity: 0;
    `;
    document.body.appendChild(overlay);

    // ===== LOADER STYLES =====
    var style = document.createElement('style');
    style.textContent = `
        #page-loader-overlay.show {
            display: flex !important;
            opacity: 1 !important;
        }

        #page-loader-overlay.hide {
            opacity: 0 !important;
            pointer-events: none !important;
        }

        .loader-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 1.5rem;
        }

        .loader-spinner {
            position: relative;
            width: 80px;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .loader-ring {
            position: absolute;
            border: 2px solid transparent;
            border-radius: 50%;
            animation: loaderSpin 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
        }

        .loader-ring:nth-child(1) {
            width: 80px;
            height: 80px;
            border-top-color: #5fd0ba;
            border-right-color: #5fd0ba;
            animation-delay: 0s;
        }

        .loader-ring:nth-child(2) {
            width: 60px;
            height: 60px;
            border-top-color: #3ab0a0;
            border-left-color: #3ab0a0;
            animation-delay: 0.2s;
        }

        .loader-ring:nth-child(3) {
            width: 40px;
            height: 40px;
            border-bottom-color: #2d8f7a;
            border-right-color: #2d8f7a;
            animation-delay: 0.4s;
        }

        .loader-logo {
            position: absolute;
            font-family: 'Playfair Display', serif;
            font-weight: 900;
            font-style: italic;
            font-size: 1.8rem;
            color: #5fd0ba;
            text-shadow: 0 0 30px rgba(95, 208, 186, 0.2);
            animation: loaderPulse 1.5s ease-in-out infinite;
        }

        .loader-text {
            color: #9bb0bb;
            font-size: 0.9rem;
            font-weight: 400;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            animation: loaderTextPulse 1.5s ease-in-out infinite;
        }

        @keyframes loaderSpin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @keyframes loaderPulse {
            0%, 100% { transform: scale(1); opacity: 0.6; }
            50% { transform: scale(1.1); opacity: 1; }
        }

        @keyframes loaderTextPulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
    `;
    document.head.appendChild(style);

    // ===== LOADER STATE =====
    var isShowing = false;
    var hideTimeout = null;

    function showLoader() {
        if (isShowing) return;
        isShowing = true;

        // Clear any pending hide
        if (hideTimeout) {
            clearTimeout(hideTimeout);
            hideTimeout = null;
        }

        overlay.classList.remove('hide');
        overlay.classList.add('show');
    }

    function hideLoader() {
        if (!isShowing) return;
        isShowing = false;

        overlay.classList.remove('show');
        overlay.classList.add('hide');

        // Remove from display after transition
        if (hideTimeout) {
            clearTimeout(hideTimeout);
        }
        hideTimeout = setTimeout(function() {
            overlay.style.display = 'none';
            overlay.classList.remove('hide');
            hideTimeout = null;
        }, 400);
    }

    // ============================================================
    // DETECT NAVIGATION EVENTS
    // ============================================================

    // 1. Link clicks (including same-page and external)
    document.addEventListener('click', function(e) {
        var target = e.target.closest('a');
        if (!target) return;

        var href = target.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;
        if (target.target === '_blank') return;
        if (e.ctrlKey || e.metaKey || e.shiftKey) return;

        showLoader();
    });

    // 2. Form submissions
    document.addEventListener('submit', function(e) {
        var form = e.target;
        if (form) {
            showLoader();
        }
    });

    // 3. Beforeunload (page refresh, close, navigate away)
    window.addEventListener('beforeunload', function() {
        showLoader();
    });

    // 4. Page unload
    window.addEventListener('pagehide', function() {
        showLoader();
    });

    // 5. Popstate (back/forward navigation)
    window.addEventListener('popstate', function() {
        showLoader();
    });

    // 6. DOM content loaded - hide loader when page is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            hideLoader();
        });
    } else {
        hideLoader();
    }

    // 7. Full page load (images, styles, etc.)
    window.addEventListener('load', function() {
        setTimeout(hideLoader, 300);
    });

    // 8. Hide loader after a maximum time (fallback - 5 seconds)
    var maxLoadTimeout = setTimeout(function() {
        hideLoader();
    }, 5000);

    // Clear max timeout when page loads
    window.addEventListener('load', function() {
        clearTimeout(maxLoadTimeout);
    });

    // ============================================================
    // EXPOSE METHODS (for manual control)
    // ============================================================

    window.PageLoader = {
        show: showLoader,
        hide: hideLoader,
        isShowing: function() { return isShowing; }
    };

    // ============================================================
    // TURBO / HTMX / HOTWIRE SUPPORT
    // ============================================================

    // Turbo (Rails) / Hotwire
    document.addEventListener('turbo:before-fetch', showLoader);
    document.addEventListener('turbo:render', hideLoader);
    document.addEventListener('turbo:before-cache', showLoader);

    // HTMX
    document.addEventListener('htmx:beforeRequest', showLoader);
    document.addEventListener('htmx:afterRequest', hideLoader);
    document.addEventListener('htmx:afterSwap', hideLoader);

    // Alpine.js
    document.addEventListener('alpine:init', function() {
        hideLoader();
    });

    // ============================================================
    // UNLOAD PROTECTION
    // ============================================================

    // Ensure loader shows on any navigation
    var originalPushState = history.pushState;
    var originalReplaceState = history.replaceState;

    history.pushState = function() {
        showLoader();
        return originalPushState.apply(this, arguments);
    };

    history.replaceState = function() {
        showLoader();
        return originalReplaceState.apply(this, arguments);
    };

    // ============================================================
    // CUSTOM EVENT TRIGGERS
    // ============================================================

    // Listen for custom events from your app
    document.addEventListener('page:loading', showLoader);
    document.addEventListener('page:loaded', hideLoader);

    console.log('[PageLoader] Initialized ✓');

})();