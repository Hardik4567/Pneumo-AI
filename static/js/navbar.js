/**
 * ==========================================================================
 * PneumoAI - Premium Navbar Component Controller
 * File: navbar.js
 * Version: 1.0.0
 * Description: Dedicated navigation architecture orchestration logic.
 * Handles advanced responsive menus, accordion dropdown toggles,
 * IntersectionObserver-backed scroll spying, and focus traps.
 * ==========================================================================
 */

'use strict';

(function () {
    /* ==========================================================================
       1. NAVBAR CONFIGURATION MATRIX
       ========================================================================== */
    const CONFIG = {
        HEIGHT: {
            DEFAULT: 80,
            SHRINK: 60
        },
        SCROLL: {
            SHRINK_THRESHOLD: 80,
            HIDE_THRESHOLD: 150,
            TOLERANCE: 8,
            THROTTLE_DELAY: 16 // Optimized frame-rate limits (~60fps)
        },
        BREAKPOINTS: {
            DESKTOP: 992 // Matching CSS lg breakpoint
        },
        TIMING: {
            HOVER_DELAY: 150,
            TRANSITION: 300
        },
        OBSERVER: {
            ROOT_MARGIN: '-20% 0px -60% 0px', // Precise middle-viewport tracking zone
            THRESHOLD: 0
        }
    };

    /* ==========================================================================
       2. DOM ELEMENTS CACHE
       ========================================================================== */
    const DOM = {};
    
    const cacheElements = () => {
        DOM.navbar = document.querySelector('.navbar');
        if (!DOM.navbar) return false;

        DOM.container      = DOM.navbar.querySelector('.navbar__container');
        DOM.brand          = DOM.navbar.querySelector('.navbar__brand');
        DOM.logo           = DOM.navbar.querySelector('.navbar__logo');
        DOM.toggle         = DOM.navbar.querySelector('.navbar__toggle');
        DOM.menu           = DOM.navbar.querySelector('.navbar__menu');
        DOM.overlay        = DOM.navbar.querySelector('.navbar__overlay') || createOverlayFallback();
        DOM.links          = Array.from(DOM.navbar.querySelectorAll('.navbar__link'));
        DOM.dropdowns      = Array.from(DOM.navbar.querySelectorAll('.navbar__dropdown'));
        DOM.searchButton   = DOM.navbar.querySelector('.navbar__search-btn');
        DOM.searchPanel    = DOM.navbar.querySelector('.navbar__search-panel');
        
        return true;
    };

    const createOverlayFallback = () => {
        if (!DOM.menu) return null;
        const overlay = document.createElement('div');
        overlay.className = 'navbar__overlay';
        DOM.navbar.appendChild(overlay);
        return overlay;
    };

    /* ==========================================================================
       3. SYSTEM RUNTIME VARIABLE STATE
       ========================================================================== */
    const STATE = {
        isMenuOpen: false,
        isNavbarHidden: false,
        isSearchOpen: false,
        lastScroll: 0,
        currentSection: null,
        isMobile: false,
        isAnimating: false,
        focusedElementBeforeOpen: null,
        dropdownTimers: new Map()
    };

    /* ==========================================================================
       4. CONTEXTUAL UTILITY SHORTCUTS (BOUNDED LOCALLY)
       ========================================================================== */
    const throttle = (callback, limit) => {
        let wait = false;
        return (...args) => {
            if (!wait) {
                callback.apply(this, args);
                wait = true;
                setTimeout(() => wait = false, limit);
            }
        };
    };

    const debounce = (callback, delay) => {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => callback.apply(this, args), delay);
        };
    };

    /* ==========================================================================
       5. CORE STRUCTURAL LAYOUT MODIFIERS (SCROLL MECHANICS)
       ========================================================================== */
    const handleScrollMetrics = () => {
        if (STATE.isMenuOpen || STATE.isAnimating) return;

        const currentScroll = Math.max(0, window.scrollY);
        const scrollDelta = currentScroll - STATE.lastScroll;

        // Sticky & Shrink Vector States Processing
        if (currentScroll > CONFIG.SCROLL.SHRINK_THRESHOLD) {
            DOM.navbar.classList.add('navbar--sticky', 'navbar--shrink');
        } else {
            DOM.navbar.classList.remove('navbar--sticky', 'navbar--shrink');
        }

        // Auto Hide/Show Structural Translation Engine Layer (Desktop Exclusive)
        if (!STATE.isMobile) {
            if (Math.abs(scrollDelta) > CONFIG.SCROLL.TOLERANCE) {
                if (currentScroll > CONFIG.SCROLL.HIDE_THRESHOLD && scrollDelta > 0) {
                    // Scrolling Downwards - Evacuate Navbar Node
                    if (!STATE.isNavbarHidden) {
                        DOM.navbar.classList.add('navbar--hidden');
                        STATE.isNavbarHidden = true;
                        if (STATE.isSearchOpen) closeSearch();
                    }
                } else if (scrollDelta < 0 || currentScroll <= CONFIG.SCROLL.HIDE_THRESHOLD) {
                    // Scrolling Upwards - Reposition Navbar Node
                    if (STATE.isNavbarHidden) {
                        DOM.navbar.classList.remove('navbar--hidden');
                        STATE.isNavbarHidden = false;
                    }
                }
            }
        } else {
            // Guard safety clear for fluid breakpoint transformations
            DOM.navbar.classList.remove('navbar--hidden');
            STATE.isNavbarHidden = false;
        }

        STATE.lastScroll = currentScroll;
    };

    /* ==========================================================================
       6. MOBILE DRAWER INTERFACE MANAGEMENT (DRAWER MANAGEMENT)
       ========================================================================== */
    const openMenu = () => {
        if (STATE.isMenuOpen || STATE.isAnimating) return;

        STATE.isAnimating = true;
        STATE.focusedElementBeforeOpen = document.activeElement;

        DOM.navbar.classList.add('navbar--menu-open');
        DOM.toggle?.setAttribute('aria-expanded', 'true');
        DOM.toggle?.classList.remove('collapsed');
        
        document.body.style.overflow = 'hidden';

        setTimeout(() => {
            STATE.isMenuOpen = true;
            STATE.isAnimating = false;
            trapFocus(DOM.menu);
        }, CONFIG.TIMING.TRANSITION);
    };

    const closeMenu = () => {
        if (!STATE.isMenuOpen || STATE.isAnimating) return;

        STATE.isAnimating = true;
        DOM.navbar.classList.remove('navbar--menu-open');
        DOM.toggle?.setAttribute('aria-expanded', 'false');
        DOM.toggle?.classList.add('collapsed');
        
        closeAllDropdowns();
        document.body.style.overflow = '';

        setTimeout(() => {
            STATE.isMenuOpen = false;
            STATE.isAnimating = false;
            DOM.menu.onkeydown = null;
            STATE.focusedElementBeforeOpen?.focus();
        }, CONFIG.TIMING.TRANSITION);
    };

    const toggleMenu = () => {
        STATE.isMenuOpen ? closeMenu() : openMenu();
    };

    const trapFocus = (containerElement) => {
        if (!containerElement) return;
        const focusables = Array.from(containerElement.querySelectorAll('a, button, input, [tabindex="0"]'));
        if (focusables.length === 0) return;

        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        
        first.focus();

        containerElement.onkeydown = (e) => {
            if (e.key !== 'Tab') return;
            if (e.shiftKey && document.activeElement === first) {
                last.focus();
                e.preventDefault();
            } else if (!e.shiftKey && document.activeElement === last) {
                first.focus();
                e.preventDefault();
            }
        };
    };

    /* ==========================================================================
       7. DROPDOWN ACCORDION ENGINE (BI-MODAL PATTERNS)
       ========================================================================== */
    const initDropdownArchitecture = () => {
        DOM.dropdowns.forEach(dropdown => {
            const btn = dropdown.querySelector('.navbar__dropdown-btn');
            const menu = dropdown.querySelector('.navbar__dropdown-menu');
            if (!btn || !menu) return;

            // Desktop Interaction Profiles Initialization Layer (Hover Strategies)
            dropdown.addEventListener('mouseenter', () => {
                if (STATE.isMobile) return;
                clearTimeout(STATE.dropdownTimers.get(dropdown));
                openDropdown(dropdown, btn, menu);
            });

            dropdown.addEventListener('mouseleave', () => {
                if (STATE.isMobile) return;
                const timer = setTimeout(() => {
                    closeDropdown(dropdown, btn, menu);
                }, CONFIG.TIMING.HOVER_DELAY);
                STATE.dropdownTimers.set(dropdown, timer);
            });

            // Universal Mobile Trigger Point and Accessibility Binding Mapping
            btn.addEventListener('click', (e) => {
                if (!STATE.isMobile) return;
                e.preventDefault();
                e.stopPropagation();
                toggleMobileDropdown(dropdown, btn, menu);
            });

            // Keyboard Keyboard Map Support System Layer
            btn.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleDropdownState(dropdown, btn, menu);
                }
                if (e.key === 'ArrowDown' && !STATE.isMobile) {
                    e.preventDefault();
                    openDropdown(dropdown, btn, menu);
                    menu.querySelector('a')?.focus();
                }
            });
        });
    };

    const openDropdown = (dropdown, btn, menu) => {
        dropdown.classList.add('show');
        btn.setAttribute('aria-expanded', 'true');
        menu.classList.add('show');
    };

    const closeDropdown = (dropdown, btn, menu) => {
        dropdown.classList.remove('show');
        btn.setAttribute('aria-expanded', 'false');
        menu.classList.remove('show');
    };

    const toggleDropdownState = (dropdown, btn, menu) => {
        const isOpen = dropdown.classList.contains('show');
        isOpen ? closeDropdown(dropdown, btn, menu) : openDropdown(dropdown, btn, menu);
    };

    const toggleMobileDropdown = (dropdown, btn, menu) => {
        const isOpen = dropdown.classList.contains('show');
        
        // Enforce structural accordion rules (Only a single drawer remains deployed)
        DOM.dropdowns.forEach(item => {
            if (item !== dropdown) {
                const iBtn = item.querySelector('.navbar__dropdown-btn');
                const iMenu = item.querySelector('.navbar__dropdown-menu');
                if (iBtn && iMenu) closeDropdown(item, iBtn, iMenu);
            }
        });

        isOpen ? closeDropdown(dropdown, btn, menu) : openDropdown(dropdown, btn, menu);
    };

    const closeAllDropdowns = () => {
        DOM.dropdowns.forEach(dropdown => {
            const btn = dropdown.querySelector('.navbar__dropdown-btn');
            const menu = dropdown.querySelector('.navbar__dropdown-menu');
            if (btn && menu) closeDropdown(dropdown, btn, menu);
        });
    };

    /* ==========================================================================
       8. RUNTIME URL EVALUATION & ROUTE DETECTOR LAYER
       ========================================================================== */
    const updateActiveLink = () => {
        const currentPath = window.location.pathname;
        const currentHash = window.location.hash;

        DOM.links.forEach(link => {
            const href = link.getAttribute('href');
            if (!href) return;

            // Strict Evaluation Filters Targeting Clean Interface Highlights
            const isMatch = href.startsWith('#') 
                ? (currentHash === href) 
                : (currentPath === href || (href !== '/' && currentPath.startsWith(href)));

            link.classList.toggle('active', isMatch);
            if (isMatch) link.setAttribute('aria-current', 'page');
            else link.removeAttribute('aria-current');
        });
    };

    /* ==========================================================================
       9. ASYNCHRONOUS SCROLL SPY INFRASTRUCTURE (IntersectionObserver Core)
       ========================================================================== */
    const initScrollSpyEngine = () => {
        const hashLinks = DOM.links.filter(link => link.getAttribute('href')?.startsWith('#'));
        if (hashLinks.length === 0) return;

        const targetSections = new Map();
        hashLinks.forEach(link => {
            const id = link.getAttribute('href');
            const section = document.querySelector(id);
            if (section) targetSections.set(id, section);
        });

        if (targetSections.size === 0) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = `#${entry.target.id}`;
                    highlightSpyLink(id);
                }
            });
        }, {
            rootMargin: CONFIG.OBSERVER.ROOT_MARGIN,
            threshold: CONFIG.OBSERVER.THRESHOLD
        });

        targetSections.forEach(section => observer.observe(section));
    };

    const highlightSpyLink = (id) => {
        DOM.links.forEach(link => {
            const href = link.getAttribute('href');
            if (href === id) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'location');
            } else if (href?.startsWith('#')) {
                link.classList.remove('active');
                link.removeAttribute('aria-current');
            }
        });
    };

    /* ==========================================================================
       10. FLUID SCROLL ANCHOR CORRECTION MECHANICS
       ========================================================================== */
    const scrollToSection = (targetSelector) => {
        const targetElement = document.querySelector(targetSelector);
        if (!targetElement) return;

        if (STATE.isMenuOpen) closeMenu();

        // Calculate dynamic offset footprint adjustments on layout fly boundaries
        const finalNavbarHeight = DOM.navbar.classList.contains('navbar--shrink') 
            ? CONFIG.HEIGHT.SHRINK 
            : CONFIG.HEIGHT.DEFAULT;

        const elementPosition = targetElement.getBoundingClientRect().top + window.scrollY;
        const offsetPosition = elementPosition - finalNavbarHeight - 16;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });

        // Graceful window structural hash updates
        if (history.pushState) {
            history.pushState(null, null, targetSelector);
        } else {
            window.location.hash = targetSelector;
        }
    };

    /* ==========================================================================
       11. SECTOR SEARCH INTERFACE SYSTEM HOOKS (FUTURE READY DRIVER)
       ========================================================================== */
    const toggleSearch = () => {
        STATE.isSearchOpen ? closeSearch() : openSearch();
    };

    const openSearch = () => {
        if (!DOM.searchPanel || STATE.isSearchOpen) return;
        DOM.searchPanel.classList.add('show');
        DOM.searchButton?.setAttribute('aria-expanded', 'true');
        STATE.isSearchOpen = true;
        
        const input = DOM.searchPanel.querySelector('input');
        if (input) setTimeout(() => input.focus(), 50);
    };

    const closeSearch = () => {
        if (!DOM.searchPanel || !STATE.isSearchOpen) return;
        DOM.searchPanel.classList.remove('show');
        DOM.searchButton?.setAttribute('aria-expanded', 'false');
        STATE.isSearchOpen = false;
    };

    /* ==========================================================================
       12. INTERACTION EVENT SUBSCRIBERS MATRIX (CENTRAL FLOW REGULATORY ENGINE)
       ========================================================================== */
    const initEventBridges = () => {
        // Throttled Scroll Core Loop Drivers Implementation
        window.addEventListener('scroll', throttle(handleScrollMetrics, CONFIG.SCROLL.THROTTLE_DELAY), { passive: true });

        // Debounced Window Structuring Resizing Pipeline Transformations
        window.addEventListener('resize', debounce(() => {
            const currentMobileState = window.innerWidth < CONFIG.BREAKPOINTS.DESKTOP;
            STATE.isMobile = currentMobileState;

            if (!currentMobileState && STATE.isMenuOpen) {
                closeMenu();
            }
            if (!currentMobileState) {
                closeAllDropdowns();
            }
        }, 100));

        // Hamburger Control Mechanism Processing Action Interception
        DOM.toggle?.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleMenu();
        });

        // Overlay Escape Route Capture Vector Points Placement
        DOM.overlay?.addEventListener('click', () => {
            if (STATE.isMenuOpen) closeMenu();
        });

        // Outside Click Target Identification Boundary Interceptors Mapping
        document.addEventListener('click', (e) => {
            const target = e.target;
            
            if (STATE.isMenuOpen && !DOM.navbar.contains(target)) {
                closeMenu();
            }
            if (!STATE.isMobile && !DOM.navbar.contains(target)) {
                closeAllDropdowns();
            }
            if (STATE.isSearchOpen && DOM.searchPanel && !DOM.searchPanel.contains(target) && !DOM.searchButton.contains(target)) {
                closeSearch();
            }
        });

        // Structural Event Intercept Map Delegation Pattern (Anchor Vectoring Rules Execution)
        DOM.navbar.addEventListener('click', (e) => {
            const linkNode = e.target.closest('.navbar__link');
            if (!linkNode) return;

            const href = linkNode.getAttribute('href');
            if (href?.startsWith('#')) {
                e.preventDefault();
                scrollToSection(href);
            }
        });

        // Optional Search Controller Structural Activation Map
        DOM.searchButton?.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleSearch();
        });

        // Accessible Keypress Sequence Router Matrix Evaluation Block
        DOM.navbar.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (STATE.isMenuOpen) closeMenu();
                if (STATE.isSearchOpen) closeSearch();
                if (!STATE.isMobile) closeAllDropdowns();
            }
        });
    };

    /* ==========================================================================
       13. INTERFACE PUBLIC DISTRIBUTION ENGINE LAYER (PneumoAI PUBLIC REGISTER)
       ========================================================================== */
    window.Navbar = {
        openMenu: () => openMenu(),
        closeMenu: () => closeMenu(),
        toggleMenu: () => toggleMenu(),
        scrollToSection: (selector) => scrollToSection(selector),
        updateActiveLink: () => updateActiveLink(),
        toggleSearch: () => toggleSearch()
    };

    /* ==========================================================================
       14. CORE SYNCHRONOUS BOOT EXECUTION POINT INITIALIZATION
       ========================================================================== */
    const initNavbar = () => {
        if (!cacheElements()) return; // Early structural escape boundary check safe processing loop guard

        STATE.isMobile = window.innerWidth < CONFIG.BREAKPOINTS.DESKTOP;
        STATE.lastScroll = window.scrollY;

        initDropdownArchitecture();
        updateActiveLink();
        initScrollSpyEngine();
        initEventBridges();
        
        // Execute bootstrap layout configuration baseline processing sync
        handleScrollMetrics();
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNavbar);
    } else {
        initNavbar();
    }
})();