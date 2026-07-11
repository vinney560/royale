// To use this, u need this 👇👇
// <script src="{% static 'js/menu.js' %}" defer></script>
// at the head or remove the defer and place the script
// tag at the end of the body starting of the scripts.

(function() {

    // ===== POPUP MENU TOGGLE =====
    const menuOverlay = document.getElementById('menuOverlay');
    const menuToggle = document.getElementById('menuToggle');
    const popupCloseBtn = document.getElementById('popupCloseBtn');
    const menuItems = document.querySelectorAll('[data-menu-item]');

    if (menuOverlay && menuToggle) {

        function openMenu() {
            menuOverlay.classList.remove('closing');
            menuOverlay.classList.add('open');
            menuToggle.classList.add('open');
            document.body.style.overflow = 'hidden';
        }

        function closeMenu() {
            menuOverlay.classList.add('closing');
            menuOverlay.classList.remove('open');
            menuToggle.classList.remove('open');
            setTimeout(function() {
                menuOverlay.classList.remove('closing');
                document.body.style.overflow = '';
            }, 400);
        }

        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            if (menuOverlay.classList.contains('open')) {
                closeMenu();
            } else {
                openMenu();
            }
        });

        if (popupCloseBtn) {
            popupCloseBtn.addEventListener('click', closeMenu);
        }

        menuItems.forEach(function(item) {
            item.addEventListener('click', closeMenu);
        });

        menuOverlay.addEventListener('click', function(e) {
            if (e.target === this) {
                closeMenu();
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && menuOverlay.classList.contains('open')) {
                closeMenu();
            }
        });

    }

})();