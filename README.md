# CoreBase Website

A professional, multi-language B2B website built for **CoreBase**, a certified Odoo Learning Partner in Azerbaijan. This project uses a Flask backend and a clean HTML/Tailwind CSS frontend with a dynamic client-side translation system.

## 🚀 Features

- **Dynamic Localization**: Instantly switch between English (EN) and Azerbaijani (AZ) without page reloads using Vanilla JavaScript and JSON dictionaries.
- **Modern UI**: Styled with Tailwind CSS, featuring an enterprise-tech aesthetic with custom "Odoo Purple" and "Deep Navy" branding.
- **Fully Responsive**: Optimized for desktop, tablet, and mobile viewing.
- **Lead Generation Form**: A functional AJAX-powered contact form with immediate user feedback.

## 🛠️ Technology Stack

- **Backend**: Python (Flask)
- **Frontend**: HTML5, Vanilla JavaScript, CSS3
- **Styling**: Tailwind CSS (via CDN)
- **Translations**: JSON Dictionaries (`en.json`, `az.json`)

## 💻 Getting Started

### Prerequisites
Make sure you have Python 3 installed on your machine.

### Installation & Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/Shaeeg/CoreBase-Website.git
   cd CoreBase-Website
   ```

2. **Create and activate a virtual environment** (Recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask application**:
   ```bash
   python3 app.py
   ```

5. **View the website**:
   Open your browser and navigate to `http://127.0.0.1:5000`

## 📁 Project Structure

```text
CoreBase-Website/
├── app.py                  # Main Flask application and API routes
├── requirements.txt        # Python dependencies
├── .gitignore              # Ignored files for git
├── translations/           # Localization dictionaries
│   ├── az.json             # Azerbaijani translations
│   └── en.json             # English translations
├── templates/              # HTML templates
│   ├── base.html           # Master layout containing Navbar and Footer
│   └── index.html          # Homepage content
└── static/                 # Static assets
    ├── css/
    │   └── style.css       # Custom animations and styles
    └── js/
        └── main.js         # Logic for translation switcher and form submission
```
