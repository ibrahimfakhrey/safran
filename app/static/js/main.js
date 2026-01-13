/**
 * Main JavaScript for Apartment Sharing Platform
 * Handles animations, interactions, dynamic content, and theme switching
 */

// ============= Theme Switcher (Light/Dark Mode) =============
(function() {
    // Get theme from localStorage or default to 'dark'
    const getTheme = () => localStorage.getItem('theme') || 'dark';
    
    // Set theme on document
    const setTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    };
    
    // Initialize theme on page load
    const initTheme = () => {
        const theme = getTheme();
        setTheme(theme);
    };
    
    // Toggle theme
    const toggleTheme = () => {
        const currentTheme = getTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        
        // Add animation effect
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    };
    
    // Initialize on load
    initTheme();
    
    // Add event listener when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', toggleTheme);
        }
    });
})();

// ============= Counter Animation =============
function animateCounters() {
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const increment = target / (duration / 16); // 60fps
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.textContent = Math.floor(current).toLocaleString('ar-EG');
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target.toLocaleString('ar-EG');
            }
        };
        
        // Start animation when element is in viewport
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(counter.closest('.stat-card'));
    });
}

// ============= Scroll Animations =============
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in, .slide-in-up');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    animatedElements.forEach(el => observer.observe(el));
}

// ============= Smooth Scroll =============
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ============= Alert Auto-dismiss =============
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}

// ============= Form Validation =============
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('error');
                
                // Remove error class on input
                field.addEventListener('input', function() {
                    this.classList.remove('error');
                }, { once: true });
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            alert('يرجى ملء جميع الحقول المطلوبة');
        }
    });
}

// ============= Number Formatting =============
function formatCurrency(amount) {
    return new Intl.NumberFormat('ar-EG', {
        style: 'currency',
        currency: 'EGP',
        minimumFractionDigits: 0
    }).format(amount);
}

function formatNumber(num) {
    return new Intl.NumberFormat('ar-EG').format(num);
}

// ============= Share Purchase Calculator =============
function initShareCalculator() {
    const sharesInput = document.getElementById('num_shares');
    const sharePrice = document.getElementById('share_price');
    const totalCost = document.getElementById('total_cost');
    const userBalance = document.getElementById('user_balance');
    const remainingBalance = document.getElementById('remaining_balance');
    
    if (!sharesInput || !sharePrice) return;
    
    sharesInput.addEventListener('input', function() {
        const numShares = parseInt(this.value) || 0;
        const pricePerShare = parseFloat(sharePrice.textContent.replace(/[^\d.]/g, ''));
        const total = numShares * pricePerShare;
        
        if (totalCost) {
            totalCost.textContent = formatNumber(total);
        }
        
        if (userBalance && remainingBalance) {
            const balance = parseFloat(userBalance.textContent.replace(/[^\d.]/g, ''));
            const remaining = balance - total;
            remainingBalance.textContent = formatNumber(remaining);
            
            // Update color based on remaining balance
            if (remaining < 0) {
                remainingBalance.style.color = 'var(--error)';
            } else {
                remainingBalance.style.color = 'var(--success)';
            }
        }
    });
}

// ============= Filter & Sort =============
function initMarketFilters() {
    const statusFilter = document.getElementById('status_filter');
    const locationFilter = document.getElementById('location_filter');
    const sortFilter = document.getElementById('sort_filter');
    
    function updateFilters() {
        const params = new URLSearchParams();
        
        if (statusFilter && statusFilter.value !== 'all') {
            params.append('status', statusFilter.value);
        }
        
        if (locationFilter && locationFilter.value) {
            params.append('location', locationFilter.value);
        }
        
        if (sortFilter && sortFilter.value !== 'newest') {
            params.append('sort', sortFilter.value);
        }
        
        window.location.search = params.toString();
    }
    
    [statusFilter, locationFilter, sortFilter].forEach(filter => {
        if (filter) {
            filter.addEventListener('change', updateFilters);
        }
    });
}

// ============= Progress Bar Animation =============
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const percentage = bar.getAttribute('data-percentage');
                setTimeout(() => {
                    bar.style.width = percentage + '%';
                }, 100);
                observer.unobserve(bar);
            }
        });
    }, { threshold: 0.5 });
    
    progressBars.forEach(bar => observer.observe(bar));
}

// ============= Mobile Menu Toggle =============
function initMobileMenu() {
    const menuToggle = document.getElementById('mobile-menu-toggle');
    const navMenu = document.querySelector('.navbar-menu');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }
}

// ============= Confirm Delete =============
function confirmDelete(message) {
    return confirm(message || 'هل أنت متأكد من عملية الحذف؟');
}

// ============= Image Preview =============
function initImagePreview() {
    const imageInput = document.getElementById('image');
    const preview = document.getElementById('image-preview');
    
    if (imageInput && preview) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
}

// ============= Gallery Lightbox =============
function initGallery() {
    const thumbs = document.querySelectorAll('.gallery-thumb');
    if (!thumbs || thumbs.length === 0) return;

    const modal = document.getElementById('gallery-modal');
    const currentImg = document.getElementById('gallery-current');
    const closeBtn = document.getElementById('gallery-close');
    const prevBtn = document.getElementById('gallery-prev');
    const nextBtn = document.getElementById('gallery-next');

    const sources = Array.from(thumbs).map(t => t.getAttribute('data-src'));
    let index = 0;

    function openAt(i) {
        index = (i + sources.length) % sources.length;
        currentImg.src = sources[index];
        modal.style.display = 'flex';
    }

    function close() {
        modal.style.display = 'none';
        currentImg.src = '';
    }

    thumbs.forEach((thumb, i) => thumb.addEventListener('click', () => openAt(i)));
    closeBtn && closeBtn.addEventListener('click', close);
    prevBtn && prevBtn.addEventListener('click', () => openAt(index - 1));
    nextBtn && nextBtn.addEventListener('click', () => openAt(index + 1));

    // keyboard
    document.addEventListener('keydown', (e) => {
        if (!modal || modal.style.display !== 'flex') return;
        if (e.key === 'Escape') close();
        if (e.key === 'ArrowLeft') openAt(index - 1);
        if (e.key === 'ArrowRight') openAt(index + 1);
    });

    // click outside to close
    modal && modal.addEventListener('click', (e) => {
        if (e.target === modal) close();
    });
}

// ============= Tooltip =============
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
            tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) tooltip.remove();
        });
    });
}

// ============= Loading State =============
function showLoading(button) {
    if (!button) return;
    button.disabled = true;
    button.innerHTML = '<span class="spinner"></span> جاري التحميل...';
}

function hideLoading(button, originalText) {
    if (!button) return;
    button.disabled = false;
    button.innerHTML = originalText;
}

// ============= Initialize All =============
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all features
    animateCounters();
    initScrollAnimations();
    initSmoothScroll();
    initAlerts();
    initShareCalculator();
    initMarketFilters();
    animateProgressBars();
    initMobileMenu();
    initImagePreview();
    initTooltips();
    initGallery();
    
    // Add floating animation to hero section
    const heroElements = document.querySelectorAll('.hero .floating');
    heroElements.forEach((el, index) => {
        el.style.animationDelay = (index * 0.2) + 's';
    });
    
    console.log('🏢 Apartment Sharing Platform initialized');
});

// ============= Export Functions =============
window.apartmentPlatform = {
    formatCurrency,
    formatNumber,
    confirmDelete,
    showLoading,
    hideLoading
};
