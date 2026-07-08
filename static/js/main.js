/**
 * ==========================================================================
 * PneumoAI - Core Production-Grade Application Engine
 * File: main.js
 * Version: 1.0.0
 * Description: Global application orchestration layer. Initializes core platform
 * behaviors, performance-optimized layout throttling, global event 
 * delegation maps, utility rendering, UI interactions, and high-contrast 
 * accessibility profiles for the PneumoAI system.
 * ==========================================================================
 */

'use strict';

/* ==========================================================================
   PART 1: GLOBAL CONFIGURATION MATRIX
   ========================================================================== */
const CONFIG = {
    ANIMATION: {
        DURATION_FAST: 150,
        DURATION_NORMAL: 300,
        DURATION_SLOW: 500,
        EASING_DEFAULT: 'cubic-bezier(0.16, 1, 0.3, 1)'
    },
    SCROLL: {
        NAVBAR_SHRINK_OFFSET: 40,
        NAVBAR_HIDE_THRESHOLD: 120,
        BACK_TO_TOP_OFFSET: 400,
        THROTTLE_DELAY: 16 // ~60fps rendering frame limit validation boundary
    },
    BREAKPOINTS: {
        SM: 576,
        MD: 768,
        LG: 992,
        XL: 1200
    },
    OBSERVER: {
        ROOT_MARGIN_REVEAL: '0px 0px -8% 0px',
        ROOT_MARGIN_LAZY: '200px 0px 200px 0px',
        THRESHOLD_REVEAL: 0.05,
        THRESHOLD_COUNTER: 0.1
    },
    TOAST: {
        AUTO_DISMISS_DELAY: 5000,
        MAX_QUEUE_SIZE: 5
    }
};

/* ==========================================================================
   PART 2: DOM CACHE MANAGEMENT (LAZY INITIALIZATION MAPS)
   ========================================================================== */
const DOM = {
    cache: {},
    initialize() {
        this.cache.html = document.documentElement;
        this.cache.body = document.body;
        this.cache.loadingScreen = document.querySelector('.js-loading-screen');
        this.cache.scrollProgress = document.querySelector('.js-scroll-progress');
        this.cache.backToTop = document.querySelector('.js-back-to-top');
        this.cache.navbar = document.querySelector('.js-navbar');
        this.cache.mobileMenuToggle = document.querySelector('.js-mobile-toggle');
        this.cache.mobileMenu = document.querySelector('.js-mobile-menu');
        this.cache.globalModal = document.querySelector('.js-global-modal');
        this.cache.toastContainer = document.querySelector('.js-toast-container');
        this.cache.mainContent = document.querySelector('.js-main-content');
        this.cache.flashContainer = document.querySelector('.js-flash-container');
    },
    get(elementKey) {
        return this.cache[elementKey] || null;
    }
};

/* ==========================================================================
   PART 3: ATOMIC PERFORMANCE & UTILITY HELPER FUNCTIONS
   ========================================================================== */
const select = (selector, context = document) => context.querySelector(selector);
const selectAll = (selector, context = document) => Array.from(context.querySelectorAll(selector));

const debounce = (callback, delay) => {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => callback.apply(this, args), delay);
    };
};

const throttle = (callback, limit) => {
    let waiting = false;
    return (...args) => {
        if (!waiting) {
            callback.apply(this, args);
            waiting = true;
            setTimeout(() => waiting = false, limit);
        }
    };
};

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

const isMobile = () => window.innerWidth < CONFIG.BREAKPOINTS.MD;
const isTablet = () => window.innerWidth >= CONFIG.BREAKPOINTS.MD && window.innerWidth < CONFIG.BREAKPOINTS.LG;
const isDesktop = () => window.innerWidth >= CONFIG.BREAKPOINTS.LG;

const scrollToElement = (element, offset = 0) => {
    if (!element) return;
    const elementPosition = element.getBoundingClientRect().top + window.scrollY;
    window.scrollTo({
        top: elementPosition - offset,
        behavior: 'smooth'
    });
};

const toggleClass = (element, className, force) => {
    element?.classList.toggle(className, force);
};

const show = (element, displayStyle = 'block') => {
    if (!element) return;
    element.style.display = displayStyle;
    element.removeAttribute('aria-hidden');
};

const hide = (element) => {
    if (!element) return;
    element.style.display = 'none';
    element.setAttribute('aria-hidden', 'true');
};

const fadeIn = (element, duration = CONFIG.ANIMATION.DURATION_NORMAL) => {
    if (!element) return;
    element.style.opacity = 0;
    show(element);
    element.style.transition = `opacity ${duration}ms ${CONFIG.ANIMATION.EASING_DEFAULT}`;
    requestAnimationFrame(() => {
        element.style.opacity = 1;
    });
};

const fadeOut = (element, duration = CONFIG.ANIMATION.DURATION_NORMAL) => {
    if (!element) return;
    element.style.opacity = 1;
    element.style.transition = `opacity ${duration}ms ${CONFIG.ANIMATION.EASING_DEFAULT}`;
    requestAnimationFrame(() => {
        element.style.opacity = 0;
    });
    setTimeout(() => {
        hide(element);
    }, duration);
};

const createElement = (tagName, attributes = {}, ...children) => {
    const element = document.createElement(tagName);
    Object.entries(attributes).forEach(([key, val]) => {
        if (key === 'className') element.className = val;
        else if (key === 'dataset') {
            Object.entries(val).forEach(([dKey, dVal]) => element.dataset[dKey] = dVal);
        } else element.setAttribute(key, val);
    });
    children.forEach(child => {
        if (typeof child === 'string') element.appendChild(document.createTextNode(child));
        else if (child instanceof HTMLElement) element.appendChild(child);
    });
    return element;
};

/* ==========================================================================
   PART 4: PLATFORM ORCHESTRATION DRIVERS
   ========================================================================== */

/* --- Hardware Accelerated Boot Overlay Screen Loader --- */
const LoadingScreen = {
    init() {
        const screen = DOM.get('loadingScreen');
        if (!screen) return;
        
        window.addEventListener('load', () => {
            fadeOut(screen, CONFIG.ANIMATION.DURATION_SLOW);
            setTimeout(() => screen.remove(), CONFIG.ANIMATION.DURATION_SLOW + 50);
        });
    }
};

/* --- Top Boundary Render Throttled Scroll Progress Indicator --- */
const ScrollProgress = {
    init() {
        const progressBar = DOM.get('scrollProgress');
        if (!progressBar) return;

        const updateProgress = () => {
            const scrollHeight = DOM.get('html').scrollHeight - window.innerHeight;
            if (scrollHeight <= 0) {
                progressBar.style.width = '0%';
                return;
            }
            const progress = (window.scrollY / scrollHeight) * 100;
            progressBar.style.width = `${clamp(progress, 0, 100)}%`;
        };

        window.addEventListener('scroll', throttle(updateProgress, CONFIG.SCROLL.THROTTLE_DELAY), { passive: true });
    }
};

/* --- Global Functional Scroller Engine Node --- */
const BackToTop = {
    init() {
        const btn = DOM.get('backToTop');
        if (!btn) return;

        const toggleVisibility = () => {
            if (window.scrollY > CONFIG.SCROLL.BACK_TO_TOP_OFFSET) {
                if (btn.classList.contains('is-hidden')) {
                    btn.classList.remove('is-hidden');
                    fadeIn(btn, CONFIG.ANIMATION.DURATION_FAST);
                }
            } else {
                if (!btn.classList.contains('is-hidden')) {
                    btn.classList.add('is-hidden');
                    fadeOut(btn, CONFIG.ANIMATION.DURATION_FAST);
                }
            }
        };

        btn.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
            DOM.get('html').focus();
        });

        window.addEventListener('scroll', throttle(toggleVisibility, CONFIG.SCROLL.THROTTLE_DELAY), { passive: true });
    }
};

/* --- Bi-Directional High Efficiency Menu Sub-systems --- */
const NavbarBehaviour = {
    lastScrollTop: 0,
    init() {
        const nav = DOM.get('navbar');
        if (!nav) return;

        const processScroll = () => {
            const currentScroll = window.scrollY;
            
            // Shrink Optimization State Controls
            toggleClass(nav, 'navbar--shrink', currentScroll > CONFIG.SCROLL.NAVBAR_SHRINK_OFFSET);
            toggleClass(nav, 'navbar--scrolled', currentScroll > 10);

            // Dynamic Visibility Vector Shifts (Hide on Downward Scroll, Present on Upward Scroll)
            if (currentScroll > CONFIG.SCROLL.NAVBAR_HIDE_THRESHOLD) {
                if (currentScroll > this.lastScrollTop && !nav.classList.contains('navbar--hidden')) {
                    nav.classList.add('navbar--hidden');
                } else if (currentScroll < this.lastScrollTop && nav.classList.contains('navbar--hidden')) {
                    nav.classList.remove('navbar--hidden');
                }
            } else {
                nav.classList.remove('navbar--hidden');
            }
            this.lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
        };

        window.addEventListener('scroll', throttle(processScroll, CONFIG.SCROLL.THROTTLE_DELAY), { passive: true });
    }
};

/* --- Accessible Focus Trapped Mobile Panel Drawer --- */
const MobileNavigation = {
    isOpen: false,
    focusedElementBeforeToggle: null,

    init() {
        const toggle = DOM.get('mobileMenuToggle');
        const menu = DOM.get('mobileMenu');
        if (!toggle || !menu) return;

        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            this.isOpen ? this.close() : this.open();
        });

        // Interactive Interface Event Closures Mapping
        document.addEventListener('click', (e) => {
            if (this.isOpen && !menu.contains(e.target) && !toggle.contains(e.target)) this.close();
        });

        menu.addEventListener('click', (e) => {
            if (e.target.closest('a')) this.close();
        });

        window.addEventListener('resize', debounce(() => {
            if (isDesktop() && this.isOpen) this.close();
        }, 100));
    },

    open() {
        this.isOpen = true;
        this.focusedElementBeforeToggle = document.activeElement;
        
        DOM.get('mobileMenuToggle').setAttribute('aria-expanded', 'true');
        DOM.get('mobileMenu').classList.add('is-active');
        DOM.get('body').style.overflow = 'hidden';
        
        this.trapFocus();
    },

    close() {
        this.isOpen = false;
        DOM.get('mobileMenuToggle').setAttribute('aria-expanded', 'false');
        DOM.get('mobileMenu').classList.remove('is-active');
        DOM.get('body').style.overflow = '';
        
        this.focusedElementBeforeToggle?.focus();
    },

    trapFocus() {
        const menu = DOM.get('mobileMenu');
        const focusables = selectAll('a, button, input, select, textarea, [tabindex="0"]', menu);
        if (focusables.length === 0) return;
        
        const first = focusables[0];
        const last = focusables[focusables.length - 1];

        menu.onkeydown = (e) => {
            if (e.key !== 'Tab') return;
            if (e.shiftKey && document.activeElement === first) {
                last.focus();
                e.preventDefault();
            } else if (!e.shiftKey && document.activeElement === last) {
                first.focus();
                e.preventDefault();
            }
        };
        setTimeout(() => first.focus(), 50);
    }
};

/* --- Storage Backed Modern Dark / Light Theme Manager Fallback --- */
const ThemeManager = {
    init() {
        const savedTheme = localStorage.getItem('pneumoai_theme') || 'light';
        DOM.get('html').setAttribute('data-theme', savedTheme);
        // Prepared implementation hook for execution components targeting subsequent iterations
    }
};

/* --- Fluid Global Router Link Context Navigation Adjustments --- */
const ActiveNavigation = {
    init() {
        const navLinks = selectAll('.js-nav-link');
        const currentPath = window.location.pathname;

        navLinks.forEach(link => {
            const linkPath = link.getAttribute('href');
            if (linkPath === currentPath || (linkPath !== '/' && currentPath.startsWith(linkPath))) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            } else {
                link.classList.remove('active');
                link.removeAttribute('aria-current');
            }
        });
    }
};

/* --------------------------------------------------------------------------
   PART 5: GLOBAL SYSTEM COMPONENT DIALOGS & OVERLAY INFRASTRUCTURE
   -------------------------------------------------------------------------- */

/* --- Reusable Modal Form Interface Driver --- */
const GlobalModal = {
    activeModal: null,
    previousActiveElement: null,

    init() {
        this.activeModal = DOM.get('globalModal');
        if (!this.activeModal) return;

        // Dynamic Event Intercept Assignment
        this.activeModal.addEventListener('click', (e) => {
            if (e.target.classList.contains('js-modal-close') || e.target === this.activeModal) {
                this.close();
            }
        });
    },

    open(titleText, contentDomNode, onOpenCallback = null) {
        if (!this.activeModal) return;
        this.previousActiveElement = document.activeElement;

        const title = select('.js-modal-title', this.activeModal);
        const body = select('.js-modal-body', this.activeModal);

        if (title) title.textContent = titleText;
        if (body) {
            body.innerHTML = '';
            if (typeof contentDomNode === 'string') body.innerHTML = contentDomNode;
            else if (contentDomNode instanceof HTMLElement) body.appendChild(contentDomNode);
        }

        show(this.activeModal, 'flex');
        setTimeout(() => this.activeModal.classList.add('modal--open'), 10);
        DOM.get('body').style.overflow = 'hidden';
        
        this.trapFocus();
        if (onOpenCallback) onOpenCallback(this.activeModal);
    },

    close() {
        if (!this.activeModal || !this.activeModal.classList.contains('modal--open')) return;
        this.activeModal.classList.remove('modal--open');
        
        setTimeout(() => {
            hide(this.activeModal);
            DOM.get('body').style.overflow = '';
            this.previousActiveElement?.focus();
        }, CONFIG.ANIMATION.DURATION_NORMAL);
    },

    trapFocus() {
        const focusables = selectAll('a, button, input, select, textarea, [tabindex="0"]', this.activeModal);
        if (focusables.length === 0) return;
        const first = focusables[0];
        const last = focusables[focusables.length - 1];

        this.activeModal.onkeydown = (e) => {
            if (e.key === 'Escape') this.close();
            if (e.key !== 'Tab') return;
            if (e.shiftKey && document.activeElement === first) {
                last.focus();
                e.preventDefault();
            } else if (!e.shiftKey && document.activeElement === last) {
                first.focus();
                e.preventDefault();
            }
        };
        setTimeout(() => first.focus(), CONFIG.ANIMATION.DURATION_FAST);
    }
};

/* --- Memory Leaking Insulated Live Operational Notification System --- */
const ToastNotification = {
    init() {
        if (!DOM.get('toastContainer')) {
            const container = createElement('div', { className: 'toast-container js-toast-container', 'aria-live': 'polite' });
            DOM.get('body').appendChild(container);
            DOM.cache.toastContainer = container;
        }
    },

    create(message, type = 'info', duration = CONFIG.TOAST.AUTO_DISMISS_DELAY) {
        const container = DOM.get('toastContainer');
        if (!container) return;

        // Regulate queue scaling ceiling limits to avoid system processing saturation
        if (container.children.length >= CONFIG.TOAST.MAX_QUEUE_SIZE) {
            container.firstElementChild?.remove();
        }

        const iconMap = { success: 'fa-check-circle', error: 'fa-exclamation-triangle', warning: 'fa-exclamation-circle', info: 'fa-info-circle' };
        const toast = createElement('div', { className: `toast toast--${type} js-toast`, role: 'alert' },
            createElement('i', { className: `fas ${iconMap[type] || iconMap.info} toast__icon` }),
            createElement('div', { className: 'toast__content' }, message),
            createElement('button', { className: 'toast__close js-toast-close', 'aria-label': 'Dismiss alert' }, '×')
        );

        container.appendChild(toast);
        
        // Execute operational life cycles
        requestAnimationFrame(() => toast.classList.add('toast--visible'));

        let dismissTimer = setTimeout(() => this.dismiss(toast), duration);

        toast.addEventListener('mouseenter', () => clearTimeout(dismissTimer));
        toast.addEventListener('mouseleave', () => dismissTimer = setTimeout(() => this.dismiss(toast), duration));
    },

    dismiss(toast) {
        if (!toast || !toast.parentNode) return;
        toast.classList.remove('toast--visible');
        toast.classList.add('toast--exit');
        setTimeout(() => toast.remove(), CONFIG.ANIMATION.DURATION_NORMAL);
    }
};

/* --- Flask Direct Output Architecture Server Validation Bridge Hooks --- */
const FlashMessageHandler = {
    init() {
        const alerts = selectAll('.js-flash-alert');
        alerts.forEach(alert => {
            const closeBtn = select('.js-flash-close', alert);
            let timer = setTimeout(() => this.dismiss(alert), 6000);

            alert.addEventListener('mouseenter', () => clearTimeout(timer));
            alert.addEventListener('mouseleave', () => timer = setTimeout(() => this.dismiss(alert), 4000));
            
            closeBtn?.addEventListener('click', () => {
                clearTimeout(timer);
                this.dismiss(alert);
            });
        });
    },

    dismiss(alert) {
        if (!alert) return;
        alert.style.transition = `all ${CONFIG.ANIMATION.DURATION_NORMAL}ms ${CONFIG.ANIMATION.EASING_DEFAULT}`;
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), CONFIG.ANIMATION.DURATION_NORMAL);
    }
};

/* --------------------------------------------------------------------------
   PART 6: INTERSECTION OBSERVER PERFORMANCE IMPLEMENTATIONS
   -------------------------------------------------------------------------- */

/* --- Lazy Loading Engine Nodes Map --- */
const LazyLoader = {
    init() {
        const lazyElements = selectAll('[data-src], [data-background]');
        if (lazyElements.length === 0) return;

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                const el = entry.target;
                
                if (el.dataset.src) {
                    el.src = el.dataset.src;
                    el.removeAttribute('data-src');
                }
                if (el.dataset.background) {
                    el.style.backgroundImage = `url('${el.dataset.background}')`;
                    el.removeAttribute('data-background');
                }
                
                el.classList.add('lazy-loaded');
                obs.unobserve(el);
            });
        }, { rootMargin: CONFIG.OBSERVER.ROOT_MARGIN_LAZY });

        lazyElements.forEach(el => observer.observe(el));
    }
};

/* --- Structural Interface Smooth Motion Framework Reveal Mapping --- */
const ScrollReveal = {
    init() {
        const reveals = selectAll('.reveal');
        if (reveals.length === 0) return;

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                const el = entry.target;
                
                // Address nested delay sequencing structural directives
                if (el.dataset.stagger) {
                    const children = selectAll(el.dataset.staggerChildren || '> *', el);
                    children.forEach((child, idx) => {
                        child.style.animationDelay = `${idx * parseInt(el.dataset.stagger, 10)}ms`;
                    });
                }
                
                el.classList.add('active');
                obs.unobserve(el);
            });
        }, {
            rootMargin: CONFIG.OBSERVER.ROOT_MARGIN_REVEAL,
            threshold: CONFIG.OBSERVER.THRESHOLD_REVEAL
        });

        reveals.forEach(el => observer.observe(el));
    }
};

/* --- Numerical Variable Linear Interpolation Run Execution Node --- */
const CounterAnimation = {
    init() {
        const counters = selectAll('.js-counter');
        if (counters.length === 0) return;

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                this.animate(entry.target);
                obs.unobserve(entry.target);
            });
        }, { threshold: CONFIG.OBSERVER.THRESHOLD_COUNTER });

        counters.forEach(c => observer.observe(c));
    },

    animate(element) {
        const target = parseFloat(element.dataset.target) || 0;
        const duration = parseInt(element.dataset.duration, 10) || 2000;
        const suffix = element.dataset.suffix || '';
        const prefix = element.dataset.prefix || '';
        const decimals = parseInt(element.dataset.decimals, 10) || 0;
        
        let startTime = null;

        const step = (timestamp) => {
            if (!startTime) startTime = timestamp;
            const progress = timestamp - startTime;
            const percentage = Math.min(progress / duration, 1);
            
            // Cubic out easing translation layer optimization parameters
            const easeProgress = 1 - Math.pow(1 - percentage, 3);
            const current = easeProgress * target;
            
            element.textContent = `${prefix}${current.toFixed(decimals)}${suffix}`;

            if (percentage < 1) {
                requestAnimationFrame(step);
            } else {
                element.textContent = `${prefix}${target.toFixed(decimals)}${suffix}`;
            }
        };

        requestAnimationFrame(step);
    }
};

/* --------------------------------------------------------------------------
   PART 7: CENTRAL REGULATED COMPONENT EVENT DELEGATION MATRIX
   -------------------------------------------------------------------------- */
const GlobalEventDelegator = {
    init() {
        // Core Single Point of Subscription Interception Engine mapping lower computational structures
        document.addEventListener('click', (e) => {
            const target = e.target;

            // Direct Intercept Handler Node: Smooth Internal Anchor Scroller
            const anchor = target.closest('a[href^="#"]');
            if (anchor) {
                const targetId = anchor.getAttribute('href');
                if (targetId && targetId !== '#') {
                    e.preventDefault();
                    const dest = select(targetId);
                    if (dest) {
                        const navHeight = DOM.get('navbar')?.offsetHeight || 0;
                        scrollToElement(dest, navHeight + 20);
                    }
                }
                return;
            }

            // Direct Intercept Handler Node: Toast Manual Immediate Dismissions
            if (target.closest('.js-toast-close')) {
                const toast = target.closest('.js-toast');
                if (toast) ToastNotification.dismiss(toast);
                return;
            }

            // Direct Intercept Handler Node: Bootstrap Native Adaptive Declarative Overlays Fallbacks
            const dropdownToggle = target.closest('.js-dropdown-toggle');
            if (dropdownToggle) {
                e.stopPropagation();
                dropdownToggle.parentElement.classList.toggle('dropdown--open');
            }
        });

        // Close global responsive submenus across context boundaries
        document.addEventListener('click', () => {
            selectAll('.dropdown--open').forEach(d => d.classList.remove('dropdown--open'));
        });

        // Keydown Management Systems Router Pipeline Mapping
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (MobileNavigation.isOpen) MobileNavigation.close();
                if (GlobalModal.activeModal?.classList.contains('modal--open')) GlobalModal.close();
            }
        });
    }
};

/* --------------------------------------------------------------------------
   PART 8: PUBLIC INTERFACE APPLICATION WRAPPER (PneumoAI CONTROL INTERACTION MATRIX)
   -------------------------------------------------------------------------- */
window.PneumoAI = {
    showToast: (message, type, duration) => ToastNotification.create(message, type, duration),
    openModal: (title, content, callback) => GlobalModal.open(title, content, callback),
    closeModal: () => GlobalModal.close(),
    scrollToElement: (el, offset) => scrollToElement(el, offset),
    debounce: (cb, delay) => debounce(cb, delay),
    throttle: (cb, limit) => throttle(cb, limit),
    fadeIn: (el, dur) => fadeIn(el, dur),
    fadeOut: (el, dur) => fadeOut(el, dur),
    show: (el, display) => show(el, display),
    hide: (el) => hide(el)
};

/* --------------------------------------------------------------------------
   PART 9: SYSTEM PIPELINE SYNCHRONOUS BOOT INITIALIZER
   -------------------------------------------------------------------------- */
const init = () => {
    DOM.initialize();
    
    // Core Engine Sequence Directives Execution Map
    GlobalEventDelegator.init();
    LoadingScreen.init();
    ScrollProgress.init();
    BackToTop.init();
    NavbarBehaviour.init();
    MobileNavigation.init();
    ThemeManager.init();
    ActiveNavigation.init();
    GlobalModal.init();
    ToastNotification.init();
    FlashMessageHandler.init();
    
    // Performance Intersection Sub-systems Driving Engine Networks
    LazyLoader.init();
    ScrollReveal.init();
    CounterAnimation.init();
};

// Safe Context Application Guarded Initializing Framework Handlers
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}