(function() {

    // ============================================================
    // WAIT FOR DOM TO BE READY
    // ============================================================

    function domReady(fn) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fn);
        } else {
            fn();
        }
    }

    domReady(function() {

        // ============================================================
        // CREATE LOADER OVERLAY
        // ============================================================

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
                <div class="loader-text" id="loaderText">Loading...</div>
                <div class="loader-subtext" id="loaderSubtext">Preparing your experience</div>
                <div class="loader-progress">
                    <div class="loader-progress-bar"></div>
                </div>
                <button class="loader-close-btn" id="loaderCloseBtn">
                    <i class="fas fa-times"></i> Close
                </button>
            </div>
        `;

        overlay.style.cssText = [
            'position: fixed',
            'top: 0',
            'left: 0',
            'width: 100%',
            'height: 100%',
            'background: rgba(7, 10, 12, 0.88)',
            'backdrop-filter: blur(16px)',
            '-webkit-backdrop-filter: blur(16px)',
            'z-index: 99999',
            'display: none',
            'align-items: center',
            'justify-content: center',
            'flex-direction: column',
            'transition: opacity 0.5s ease',
            'opacity: 0'
        ].join(';');

        if (document.body) {
            document.body.appendChild(overlay);
        } else {
            document.addEventListener('DOMContentLoaded', function() {
                document.body.appendChild(overlay);
            });
        }

        // ============================================================
        // CREATE SAME-PAGE FLASH INDICATOR
        // ============================================================

        var flash = document.createElement('div');
        flash.id = 'page-flash';
        flash.style.cssText = [
            'position: fixed',
            'top: 0',
            'left: 0',
            'width: 100%',
            'height: 100%',
            'background: rgba(7, 10, 12, 0.3)',
            'backdrop-filter: blur(4px)',
            '-webkit-backdrop-filter: blur(4px)',
            'z-index: 99998',
            'display: none',
            'align-items: center',
            'justify-content: center',
            'transition: opacity 0.3s ease',
            'opacity: 0',
            'pointer-events: none'
        ].join(';');
        flash.innerHTML = `
            <div style="display:flex;flex-direction:column;align-items:center;gap:0.5rem;">
                <div style="width:40px;height:40px;border:2px solid rgba(95,208,186,0.2);border-top-color:#5fd0ba;border-radius:50%;animation:loaderSpin 0.8s linear infinite;"></div>
                <div style="color:#9bb0bb;font-size:0.8rem;letter-spacing:0.1em;">Scrolling...</div>
            </div>
        `;
        if (document.body) {
            document.body.appendChild(flash);
        } else {
            document.addEventListener('DOMContentLoaded', function() {
                document.body.appendChild(flash);
            });
        }

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
            #page-flash.show {
                display: flex !important;
                opacity: 1 !important;
            }
            #page-flash.hide {
                opacity: 0 !important;
                display: none !important;
            }
            .loader-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 1rem;
                padding: 2rem;
                position: relative;
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
                color: #e4edf2;
                font-size: 1.1rem;
                font-weight: 500;
                letter-spacing: 0.1em;
                margin-top: 0.5rem;
                animation: loaderTextPulse 1.5s ease-in-out infinite;
            }
            .loader-subtext {
                color: #7a9aa8;
                font-size: 0.8rem;
                font-weight: 300;
                letter-spacing: 0.05em;
                opacity: 0.7;
                transition: opacity 0.3s ease;
            }
            .loader-progress {
                width: 200px;
                height: 2px;
                background: rgba(255, 255, 255, 0.06);
                border-radius: 2px;
                overflow: hidden;
                margin-top: 0.5rem;
            }
            .loader-progress-bar {
                height: 100%;
                width: 0%;
                background: linear-gradient(90deg, #5fd0ba, #3ab0a0);
                border-radius: 2px;
                transition: width 0.5s ease;
                animation: loaderProgress 3s ease-in-out infinite;
            }
            .loader-close-btn {
                display: none;
                align-items: center;
                gap: 0.5rem;
                margin-top: 1.5rem;
                padding: 0.5rem 1.5rem;
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 2rem;
                color: #9bb0bb;
                font-size: 0.8rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                font-family: inherit;
                letter-spacing: 0.05em;
            }
            .loader-close-btn.visible {
                display: inline-flex;
            }
            .loader-close-btn:hover {
                background: rgba(255, 255, 255, 0.12);
                border-color: rgba(255, 255, 255, 0.15);
                color: #e4edf2;
                transform: scale(1.02);
            }
            .loader-close-btn i {
                font-size: 0.7rem;
                color: #5fd0ba;
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
                0%, 100% { opacity: 0.6; }
                50% { opacity: 1; }
            }
            @keyframes loaderProgress {
                0% { width: 0%; }
                50% { width: 70%; }
                100% { width: 100%; }
            }
            @media (max-width: 480px) {
                .loader-text { font-size: 0.95rem; }
                .loader-subtext { font-size: 0.7rem; }
                .loader-progress { width: 150px; }
                .loader-close-btn { padding: 0.4rem 1.2rem; font-size: 0.75rem; }
            }
        `;

        if (document.head) {
            document.head.appendChild(style);
        } else {
            document.addEventListener('DOMContentLoaded', function() {
                document.head.appendChild(style);
            });
        }

        // ============================================================
        // LOADER CONTROLS
        // ============================================================

        var isShowing = false;
        var hideTimeout = null;
        var messageTimeout = null;
        var closeBtnTimeout = null;
        var flashTimeout = null;
        var loaderText = document.getElementById('loaderText');
        var loaderSubtext = document.getElementById('loaderSubtext');
        var closeBtn = document.getElementById('loaderCloseBtn');

        var messages = [
            { text: 'Loading...', sub: 'Preparing your experience' },
            { text: 'Almost there...', sub: 'Loading your content' },
            { text: 'Just a moment...', sub: 'Getting things ready' },
            { text: 'Finalizing...', sub: 'Almost done' }
        ];

        var messageIndex = 0;

        function rotateMessage() {
            if (!isShowing) return;
            var msg = messages[messageIndex % messages.length];
            if (loaderText) loaderText.textContent = msg.text;
            if (loaderSubtext) loaderSubtext.textContent = msg.sub;
            messageIndex++;
            if (messageTimeout) clearTimeout(messageTimeout);
            messageTimeout = setTimeout(rotateMessage, 2500);
        }

        function showCloseButton() {
            if (isShowing && closeBtn) {
                closeBtn.classList.add('visible');
            }
        }

        function showLoader() {
            if (isShowing) return;
            isShowing = true;

            if (hideTimeout) {
                clearTimeout(hideTimeout);
                hideTimeout = null;
            }

            if (closeBtn) {
                closeBtn.classList.remove('visible');
            }

            messageIndex = 0;

            overlay.classList.remove('hide');
            overlay.classList.add('show');
            overlay.style.display = 'flex';

            rotateMessage();

            if (closeBtnTimeout) {
                clearTimeout(closeBtnTimeout);
            }
            closeBtnTimeout = setTimeout(showCloseButton, 5000);
        }

        function hideLoader() {
            if (!isShowing) return;
            isShowing = false;

            if (messageTimeout) {
                clearTimeout(messageTimeout);
                messageTimeout = null;
            }

            if (closeBtn) {
                closeBtn.classList.remove('visible');
            }

            if (closeBtnTimeout) {
                clearTimeout(closeBtnTimeout);
                closeBtnTimeout = null;
            }

            overlay.classList.remove('show');
            overlay.classList.add('hide');

            if (hideTimeout) {
                clearTimeout(hideTimeout);
            }
            hideTimeout = setTimeout(function() {
                overlay.style.display = 'none';
                overlay.classList.remove('hide');
                hideTimeout = null;
            }, 500);
        }

        // ===== SAME-PAGE FLASH INDICATOR =====
        function showFlash() {
            if (flashTimeout) {
                clearTimeout(flashTimeout);
            }
            flash.classList.remove('hide');
            flash.classList.add('show');

            flashTimeout = setTimeout(function() {
                flash.classList.remove('show');
                flash.classList.add('hide');
                flashTimeout = null;
            }, 1500);
        }

        // ===== CLOSE BUTTON EVENT =====
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                hideLoader();
            });
        }

        // ============================================================
        // EXPOSE GLOBALLY
        // ============================================================

        window.PageLoader = {
            show: showLoader,
            hide: hideLoader,
            isShowing: function() { return isShowing; },
            setMessage: function(text, sub) {
                if (loaderText) loaderText.textContent = text;
                if (loaderSubtext) loaderSubtext.textContent = sub || '';
            },
            showCloseButton: showCloseButton,
            showFlash: showFlash
        };

        // ============================================================
        // AUTO-DETECT NAVIGATION EVENTS
        // ============================================================

        // 1. Link clicks - works on desktop AND mobile
        document.addEventListener('click', function(e) {
            var target = e.target.closest('a');
            if (!target) return;

            var href = target.getAttribute('href');
            if (!href) return;
            if (href.startsWith('javascript:')) return;
            if (target.target === '_blank') return;
            if (e.ctrlKey || e.metaKey || e.shiftKey) return;

            // Same-page anchor link (starts with # only)
            if (href.startsWith('#')) {
                e.preventDefault();
                var targetId = href.substring(1);
                var targetElement = document.getElementById(targetId);
                if (targetElement) {
                    showFlash();
                    targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                } else {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
                return;
            }

            // Full URL with hash (e.g., /products/#section)
            if (href.includes('#')) {
                showLoader();
                return;
            }

            // Regular navigation (no hash)
            showLoader();
        }, true);

        // 2. Form submissions
        document.addEventListener('submit', function(e) {
            showLoader();
        }, true);

        // 3. Page refresh / reload / close
        window.addEventListener('beforeunload', function() {
            showLoader();
        });

        // 4. Page unload
        window.addEventListener('pagehide', function() {
            showLoader();
        });

        // 5. Back/Forward navigation
        window.addEventListener('popstate', function() {
            showLoader();
        });

        // 6. Hide loader when page is ready
        function hideOnReady() {
            setTimeout(hideLoader, 400);
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', hideOnReady);
        } else {
            hideOnReady();
        }

        // 7. Full page load
        window.addEventListener('load', function() {
            setTimeout(hideLoader, 500);
        });

        // 8. Fallback: force hide after 10 seconds max
        var fallbackTimer = setTimeout(function() {
            if (isShowing) {
                console.warn('[PageLoader] Force hiding after 10s timeout');
                hideLoader();
            }
        }, 10000);

        window.addEventListener('load', function() {
            clearTimeout(fallbackTimer);
        });

        // ============================================================
        // INTERCEPT HISTORY API
        // ============================================================

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
        // HTMX / TURBO / ALPINE SUPPORT
        // ============================================================

        document.addEventListener('htmx:beforeRequest', showLoader);
        document.addEventListener('htmx:afterRequest', hideLoader);
        document.addEventListener('htmx:afterSwap', hideLoader);

        document.addEventListener('turbo:before-fetch', showLoader);
        document.addEventListener('turbo:render', hideLoader);

        document.addEventListener('alpine:init', hideLoader);

        document.addEventListener('page:loading', showLoader);
        document.addEventListener('page:loaded', hideLoader);

        console.log('[PageLoader] Active ✓');

    }); // end domReady

})();