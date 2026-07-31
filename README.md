# CoreBase Website

A professional, multi-language B2B website built for **CoreBase**, a team of dedicated Odoo specialists in Azerbaijan. This is a static HTML/Tailwind CSS site with a dynamic client-side translation system — no backend or build step required.

## 🚀 Features

- **Dynamic Localization**: Instantly switch between English (EN) and Azerbaijani (AZ) without page reloads using Vanilla JavaScript and JSON dictionaries.
- **Modern UI**: Styled with Tailwind CSS, featuring an enterprise-tech aesthetic with custom "Odoo Purple" and "Deep Navy" branding.
- **Fully Responsive**: Optimized for desktop, tablet, and mobile viewing.
- **Lead Generation Form**: An AJAX-powered contact form (backend submission handler in progress).

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla JavaScript, CSS3
- **Styling**: Tailwind CSS (via CDN)
- **Translations**: JSON Dictionaries (`static/translations/en.json`, `az.json`)
- **Hosting**: Static hosting (GitHub Pages, via `CNAME` → corebase.az)

## 💻 Getting Started

### Prerequisites
Any local static file server works. No Python or Node dependencies are required to view the site.

### Running locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Shaeeg/CoreBase-Website.git
   cd CoreBase-Website
   ```

2. **Serve the files** with any static server, for example:
   ```bash
   python3 -m http.server 8000
   ```

3. **View the website**:
   Open your browser and navigate to `http://127.0.0.1:8000`

## 📁 Project Structure

```text
CoreBase-Website/
├── index.html              # Homepage
├── about.html              # About Us page
├── services.html           # Services / Solutions page
├── CNAME                   # Custom domain for GitHub Pages (corebase.az)
├── robots.txt              # Search engine crawl rules
├── sitemap.xml             # Sitemap for search engines
└── static/
    ├── css/
    │   └── style.css       # Custom animations and styles
    ├── js/
    │   └── main.js         # Translation switcher, scroll animations, form handling
    ├── images/
    │   └── favicon.svg
    └── translations/
        ├── en.json         # English translations
        └── az.json         # Azerbaijani translations
```
