document.addEventListener('DOMContentLoaded', () => {
    
    // --- Mobile Menu Toggle ---
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
    });

    // Close mobile menu when a link is clicked
    const mobileLinks = mobileMenu.querySelectorAll('a');
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.add('hidden');
        });
    });


    // --- Localization (i18n) ---
    const langSwitcher = document.getElementById('langSwitcher');
    const langSwitcherMobile = document.getElementById('langSwitcherMobile');
    
    // Default language
    let currentLang = localStorage.getItem('appLang') || 'en';
    langSwitcher.value = currentLang;
    if(langSwitcherMobile) langSwitcherMobile.value = currentLang;

    // Fetch and apply translations
    async function loadTranslations(lang) {
        try {
            const response = await fetch(`/api/translations/${lang}`);
            if (!response.ok) throw new Error('Network response was not ok');
            const translations = await response.json();
            
            // Update all elements with data-i18n attribute
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (translations[key]) {
                    el.textContent = translations[key];
                }
            });

            // Update placeholders if needed (e.g., in forms)
            document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
                const key = el.getAttribute('data-i18n-placeholder');
                if (translations[key]) {
                    el.setAttribute('placeholder', translations[key]);
                }
            });

            // Save preference
            localStorage.setItem('appLang', lang);
            currentLang = lang;
            
            // Sync switchers
            langSwitcher.value = lang;
            if(langSwitcherMobile) langSwitcherMobile.value = lang;

        } catch (error) {
            console.error('Error loading translations:', error);
        }
    }

    // Initial load
    loadTranslations(currentLang);

    // Event listeners for language switchers
    const handleLangChange = (e) => {
        loadTranslations(e.target.value);
    };

    langSwitcher.addEventListener('change', handleLangChange);
    if(langSwitcherMobile) langSwitcherMobile.addEventListener('change', handleLangChange);


    // --- Contact Form Submission ---
    const contactForm = document.getElementById('contactForm');
    const formSuccess = document.getElementById('formSuccess');

    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Collect data
        const formData = {
            name: document.getElementById('name').value,
            company: document.getElementById('company').value,
            phone: document.getElementById('phone').value
        };

        // Submit via AJAX
        try {
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.status === 'success') {
                // Show success message
                formSuccess.classList.remove('hidden');
                // Clear form
                contactForm.reset();
                
                // Hide message after 5 seconds
                setTimeout(() => {
                    formSuccess.classList.add('hidden');
                }, 5000);
            }

        } catch (error) {
            console.error('Error submitting form:', error);
            alert('There was an error submitting the form. Please try again.');
        }
    });
});
