# PR Royale

A modern Django-powered web application showcasing a suite of professional digital tools and services. PR Royale provides users with powerful utilities including media downloaders, website monitoring tools, and custom software development services.

## ✨ Features

### 🎬 Media Downloaders
- **YouTube Downloader**: Download videos, playlists, and audio in high quality (4K, 60fps support)
- **Facebook Downloader**: Save videos and reels in HD quality without watermarks

### 🖥️ System Tools
- **Uptime & Pinger**: 24/7 website monitoring with instant downtime alerts
- **Custom Scripts**: Tailored automation, web scrapers, and API integrations

### 🎨 Modern Web Features
- Responsive design with particle animations
- Interactive product filtering and search
- Contact form for customer inquiries
- Admin dashboard for content management
- Static file optimization with Whitenoise

## 🛠️ Technologies Used

- **Framework**: Django 5.x
- **Server**: Gunicorn
- **Database**: SQLite (development), PostgreSQL (production)
- **Environment Management**: python-decouple
- **Static Files**: Whitenoise
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Vercel-ready configuration

## 📋 Prerequisites

- Python 3.12+
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pr_royale
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   Create a `.env` file in the root directory:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///db.sqlite3
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (admin access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   Visit `http://localhost:8000` to view the application.

## 📁 Project Structure

```
pr_royale/
├── app_royale/                 # Main application
│   ├── u_views/               # User-facing views
│   │   ├── main.py           # Main page views
│   │   ├── products.py       # Products API and views
│   │   └── contact.py        # Contact page views
│   ├── templates/            # HTML templates
│   │   ├── main_page.html
│   │   ├── products.html
│   │   └── contact.html
│   ├── migrations/           # Database migrations
│   ├── models.py             # Database models
│   ├── admin.py              # Admin configuration
│   └── apps.py               # App configuration
├── pr_royale/                 # Project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py               # URL routing
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
├── static/                    # Static assets
│   ├── css/
│   ├── js/
│   └── uploads/
├── staticfiles/              # Collected static files
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── gunicorn.conf.py          # Gunicorn configuration
├── vercel.json               # Vercel deployment config
└── db.sqlite3                # Development database
```

## 🌐 Available URLs

| URL | Description |
|-----|-------------|
| `/` | Main landing page |
| `/products/` | Products showcase page |
| `/api/products` | JSON API for product data (supports pagination & search) |
| `/contact/` | Contact page |
| `/admin/` | Django admin dashboard |

### API Features

The products API supports:
- **Pagination**: `?page=1&limit=4`
- **Search**: `?search=youtube`
- Returns detailed product information including descriptions, tags, and statistics

## 🚢 Deployment

### Vercel
The project includes a `vercel.json` configuration file for easy deployment to Vercel.

### Production Server
1. Set `DEBUG=False` in production
2. Configure PostgreSQL database
3. Collect static files:
   ```bash
   python manage.py collectstatic
   ```
4. Run with Gunicorn:
   ```bash
   gunicorn pr_royale.wsgi
   ```

## 🎯 Features in Detail

### Products Page
- Dynamic product loading with AJAX
- Search functionality across all products
- Featured products highlighting
- Tag-based categorization
- Responsive grid layout

### Interactive Elements
- Particle background animation
- Smooth loading transitions
- Mobile-responsive navigation
- Hover effects on product cards

## 🔧 Development

### Adding New Products
Edit `app_royale/u_views/products.py` and add new items to the `all_products` list with the following structure:
```python
{
    'id': <unique_id>,
    'name': 'Product Name',
    'description': 'Detailed description',
    'icon': 'font-awesome-icon-class',
    'iconColor': 'tailwind-color-class',
    'tags': ['tag1', 'tag2'],
    'link': 'product-url',
    'featured': false,
    'stats': {'downloads': '1K+', 'rating': '4.8'}
}
```

### Adding New Pages
1. Create a new view in `app_royale/u_views/`
2. Add a template in `app_royale/templates/`
3. Update the URL patterns in `pr_royale/urls.py`

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For support and inquiries, use the contact form on the website or reach out through the admin dashboard.

---

**PR Royale** - Empowering your digital journey with professional tools and services.