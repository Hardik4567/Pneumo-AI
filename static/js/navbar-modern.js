/**
 * ==========================================================================
 * PNEUMOAI - Modern Navbar Controller
 * ========================================================================== */

(function() {
    'use strict';

    const navbar = document.querySelector('.med-navbar');
    const toggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileLinks = document.querySelectorAll('.med-navbar__mobile-link');

    // Initialize
    if (!navbar || !toggle || !mobileMenu) return;

    // Mobile menu toggle
    toggle.addEventListener('click', () => {
        toggle.classList.toggle('is-active');
        mobileMenu.classList.toggle('is-active');
    });

    // Close mobile menu when link is clicked
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            toggle.classList.remove('is-active');
            mobileMenu.classList.remove('is-active');
        });
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!navbar.contains(e.target)) {
            toggle.classList.remove('is-active');
            mobileMenu.classList.remove('is-active');
        }
    });

    // Add shadow on scroll
    const updateNavbarScroll = () => {
        if (window.scrollY > 10) {
            navbar.classList.add('is-scrolled');
        } else {
            navbar.classList.remove('is-scrolled');
        }
    };

    window.addEventListener('scroll', updateNavbarScroll);
    updateNavbarScroll();
})();
