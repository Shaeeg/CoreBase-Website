document.addEventListener('DOMContentLoaded', () => {
    
    // --- Mobile Menu Toggle ---
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });

        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
            });
        });
    }

    // --- Navbar Scroll Effect ---
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const handleScroll = () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll(); // run on load
    }

    // --- Active Nav Link Highlighting ---
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname;
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            // Only mark exact matches or hash links on homepage
            if (href === currentPath) {
                link.classList.add('active');
            }
        }
    });


    // --- Scroll-Driven Animations (Intersection Observer) ---
    const animatedElements = document.querySelectorAll('.animate-on-scroll, .animate-slide-left, .animate-slide-right, .animate-scale-in');
    
    if (animatedElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -40px 0px'
        });

        animatedElements.forEach(el => observer.observe(el));
    }


    // --- Stats Counter Animation ---
    const statNumbers = document.querySelectorAll('.stat-number[data-target]');
    
    if (statNumbers.length > 0) {
        let statsAnimated = false;
        
        const animateCounters = () => {
            if (statsAnimated) return;
            statsAnimated = true;
            
            statNumbers.forEach(stat => {
                const target = parseInt(stat.dataset.target);
                const suffix = stat.dataset.suffix || '+';
                const duration = 2000;
                const startTime = performance.now();
                
                const updateCounter = (currentTime) => {
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    
                    // Ease out cubic
                    const eased = 1 - Math.pow(1 - progress, 3);
                    const current = Math.round(eased * target);
                    
                    stat.textContent = current.toLocaleString() + suffix;
                    
                    if (progress < 1) {
                        requestAnimationFrame(updateCounter);
                    }
                };
                
                requestAnimationFrame(updateCounter);
            });
        };

        const statsSection = document.getElementById('statsSection');
        if (statsSection) {
            const statsObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animateCounters();
                        statsObserver.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.3 });
            
            statsObserver.observe(statsSection);
        }
    }


    // --- Typed Text Effect ---
    const typedTextEl = document.getElementById('typedText');
    
    if (typedTextEl) {
        const words = ['Accounting', 'Inventory', 'Sales', 'HR & Payroll', 'CRM', 'eCommerce'];
        // Azerbaijani translations
        const wordsAz = ['Mühasibat', 'Anbar', 'Satış', 'İnsan Resursları', 'CRM', 'Elektron Ticarət'];
        let wordIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        let currentWords = words;
        
        const type = () => {
            const currentWord = currentWords[wordIndex];
            
            if (isDeleting) {
                charIndex--;
                typedTextEl.textContent = currentWord.substring(0, charIndex);
            } else {
                charIndex++;
                typedTextEl.textContent = currentWord.substring(0, charIndex);
            }
            
            let typeSpeed = isDeleting ? 40 : 80;
            
            if (!isDeleting && charIndex === currentWord.length) {
                typeSpeed = 2000; // pause at end
                isDeleting = true;
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                wordIndex = (wordIndex + 1) % currentWords.length;
                typeSpeed = 300; // pause before next word
            }
            
            setTimeout(type, typeSpeed);
        };
        
        // Start typing after hero animation
        setTimeout(type, 800);
        
        // Update words when language changes
        window.updateTypedWords = (lang) => {
            currentWords = lang === 'az' ? wordsAz : words;
            wordIndex = 0;
            charIndex = 0;
            isDeleting = false;
        };
    }


    // --- Hero Floating Particles ---
    const particlesContainer = document.getElementById('heroParticles');
    
    if (particlesContainer) {
        const particleCount = 30;
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.classList.add('hero-particle');
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = (60 + Math.random() * 40) + '%';
            particle.style.animationDuration = (6 + Math.random() * 8) + 's';
            particle.style.animationDelay = Math.random() * 6 + 's';
            particle.style.width = (2 + Math.random() * 4) + 'px';
            particle.style.height = particle.style.width;
            particlesContainer.appendChild(particle);
        }
    }


    // --- Localization (i18n) ---
    const langSwitcher = document.getElementById('langSwitcher');
    const langSwitcherMobile = document.getElementById('langSwitcherMobile');
    
    let currentLang = localStorage.getItem('appLang') || 'en';
    if (langSwitcher) langSwitcher.value = currentLang;
    if (langSwitcherMobile) langSwitcherMobile.value = currentLang;

    async function loadTranslations(lang) {
        try {
            // Use relative path for GitHub Pages compatibility
            const basePath = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/') + 1);
            const response = await fetch(`${basePath}static/translations/${lang}.json`);
            if (!response.ok) throw new Error('Network response was not ok');
            const translations = await response.json();
            
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (translations[key]) {
                    el.textContent = translations[key];
                }
            });

            document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
                const key = el.getAttribute('data-i18n-placeholder');
                if (translations[key]) {
                    el.setAttribute('placeholder', translations[key]);
                }
            });

            localStorage.setItem('appLang', lang);
            currentLang = lang;
            
            if (langSwitcher) langSwitcher.value = lang;
            if (langSwitcherMobile) langSwitcherMobile.value = lang;
            
            // Update typed text words
            if (window.updateTypedWords) {
                window.updateTypedWords(lang);
            }

        } catch (error) {
            console.error('Error loading translations:', error);
        }
    }

    loadTranslations(currentLang);

    const handleLangChange = (e) => {
        loadTranslations(e.target.value);
    };

    if (langSwitcher) langSwitcher.addEventListener('change', handleLangChange);
    if (langSwitcherMobile) langSwitcherMobile.addEventListener('change', handleLangChange);


    // --- Contact Form Submission ---
    const contactForm = document.getElementById('contactForm');
    const formSuccess = document.getElementById('formSuccess');

    if (contactForm && formSuccess) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalContent = submitBtn.innerHTML;
            
            // Loading state
            submitBtn.innerHTML = '<svg class="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg> Sending...';
            submitBtn.disabled = true;
            
            const formData = {
                name: document.getElementById('name').value,
                company: document.getElementById('company').value,
                phone: document.getElementById('phone').value
            };

            try {
                // IMPORTANT: Replace 'YOUR_FORM_ID' with your actual Formspree form ID
                const response = await fetch('https://formspree.io/f/YOUR_FORM_ID', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    formSuccess.classList.remove('hidden');
                    contactForm.reset();
                    
                    setTimeout(() => {
                        formSuccess.classList.add('hidden');
                    }, 5000);
                } else {
                    throw new Error('Form submission failed');
                }

            } catch (error) {
                console.error('Error submitting form:', error);
                alert('There was an error submitting the form. Please try again.');
            } finally {
                submitBtn.innerHTML = originalContent;
                submitBtn.disabled = false;
            }
        });
    }
});
