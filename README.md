# DermaAura - E-Commerce Platform

A Nykaa-style skincare & haircare e-commerce platform built with Flask, featuring AI-powered recommendations, user authentication, shopping cart, and admin product management.

## Features

- ✨ Responsive Bootstrap UI with pastel pink & fresh green theme
- 🛍️ Complete product catalog with skincare & haircare categories
- 🛒 Session-based shopping cart system
- 👤 User registration & login with password hashing
- 💳 Checkout flow with tax & shipping calculation
- 🔐 Admin dashboard for product CRUD operations
- 📱 Fully responsive design (mobile, tablet, desktop)
- 🎯 Product search functionality
- ⭐ Product ratings system
- ❤️ Wishlist support for logged‑in users
- 👁️ Quick‑view modal on product listing (AJAX powered)
- 🧠 Simple AI-based skin analysis & recommendations
- 💳 Payment handling with simulation and optional Stripe integration (see below)

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite
- **Frontend**: Bootstrap 5, Jinja2 templates, Font Awesome
- **Authentication**: Session-based with password hashing (Werkzeug)

## Project Structure

```
DermaAura/
├── app/
│   ├── __init__.py           # App factory
│   ├── routes.py             # All routes (public & admin)
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Custom styles
│   │   ├── images/           # Product images
│   │   └── js/               # JavaScript
│   └── templates/
│       ├── base.html         # Base layout (navbar, footer, auth modal)
│       ├── home.html         # Homepage with featured products
│       ├── shop.html         # Shop page with filters
│       ├── product_detail.html # Individual product page
│       ├── cart.html         # Shopping cart
│       ├── checkout.html     # Checkout
│       ├── login.html        # Login form
│       ├── register.html     # Registration form
│       ├── profile.html      # User profile page
│       └── admin/
│           ├── dashboard.html # Admin dashboard
│           ├── products.html  # Manage products
│           └── product_form.html # Add/Edit product form
├── models.py                 # Database models (Product, User)
├── database.py              # Database initialization & seeding
├── app.py                   # Application entry point
├── make_admin.py            # Utility to promote user to admin
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation & Setup

### 1. Prerequisites
- Python 3.11 or 3.12 recommended
- pip (Python package manager)

Important setup note:
- This project is expected to install and run most cleanly on a fresh Python 3.11/3.12 environment.
- Older Python versions, especially Python 3.9, may fail on some machines because native dependency builds can be required.

### 2. Clone/Setup Project
```bash
cd DermaAura
```

### 3. Create Virtual Environment (Recommended)
```bash
python -m venv .venv
```

**Activate virtual environment:**
- **Windows (PowerShell/CMD):**
  ```bash
  .venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

Recommended clean setup on another machine:
```bash
python --version
# prefer Python 3.11.x or 3.12.x

python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS/Linux

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 5. Initialize Database & Seed Products
For a fresh development database run:
```bash
python seed_dev.py
```

The script will create an admin user (`admin@test.com` / `testpass123`) and a handful of sample products. You can also use `database.py` to populate twenty placeholder products or fetch real images with `fetch_images.py`.

### 6. (Optional) Fetch Photographic Product Images
By default sample products use generated coloured SVG placeholders.
To replace them with real photos you can run the `fetch_images.py` script
using either an Unsplash or Pexels API key (environment variable
`UNSPLASH_ACCESS_KEY` or `PEXELS_API_KEY`).

```bash
# set key in your shell first
export UNSPLASH_ACCESS_KEY=your_key_here
# then run
python fetch_images.py
```

The script saves photos into `app/static/images` and updates each
`Product.image` field accordingly. If no key is provided the app will
continue using placeholders.

### 6b. Hybrid AI Skin Scanner Dataset
The upgraded scanner uses a hybrid approach:
- image model for oily/acne/dry/normal base cues
- webcam-friendly face-region analysis
- quiz fusion for the final app result (`Oily & Acne-Prone`, `Dry & Sensitive`, `Combination`, `Normal`)

Dataset layout and labeling guidance live in:
`data/skin_types/README.md`

Training examples:
```bash
python train_skin_ai.py --architecture efficientnet_v2_s --epochs 12
python train_skin_ai.py --architecture mobilenet_v3_large --epochs 12
```

Public data bootstrap:
```bash
python prepare_public_skin_dataset.py --download-images --limit 300
```

Import a local oily/dry/normal dataset archive or folder:
```bash
python import_skin_type_dataset.py --source path/to/skin-type-dataset.zip
```

Webcam collection:
```bash
python collect_webcam_skin_dataset.py --subject person01
```

### 7. Stripe (Optional)
For a more realistic checkout experience you can plug in Stripe API keys. In test mode set the following environment variables before starting the app:

```bash
export STRIPE_SECRET_KEY=sk_test_xxx   # your test secret key
export STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

The app will then create real Checkout sessions and redirect users using `stripe.js`. A minimal `/payment/success` and `/payment/cancel` callback exist but no webhook logic is implemented – orders are still created via the normal checkout form. If no keys are provided the example uses the simulated flow.

### 8. Run the Application
```bash
python app.py
```

The app will start at `http://localhost:5000`

## Key Routes
### AJAX/JSON Endpoints
- `/product/<id>?json=1` - Return basic product info (used by quick‑view modal)

### Public Routes
- `/` - Homepage
- `/shop` - All products (filterable by category)
- `/product/<id>` - Product detail page
- `/cart` - Shopping cart
- `/checkout` - Checkout (login required)
- `/register` - User registration
- `/login` - User login
- `/logout` - Logout

### Admin Routes (login required + admin user)
- `/admin/dashboard` - Admin dashboard
- `/admin/products` - Manage products list
- `/admin/products/new` - Add new product
- `/admin/products/<id>/edit` - Edit product
- `/admin/products/<id>/delete` - Delete product
- `/admin/orders` - View all orders, change status and inspect payments

## User Management

### Creating Your First Admin User

After registering a regular user account:

```bash
python make_admin.py your-email@example.com
```

Example:
```bash
python make_admin.py john@example.com
```

After promotion, log in again and you'll see the **Admin** link in the navbar.

## Database Models

### Product
- `id` - Primary key
- `name` - Product name
- `category` - 'skin' or 'hair'
- `skin_type` - Oily, Dry, Normal, Combination (optional)
- `hair_type` - Hair concern (optional)
- `price` - Product price
- `description` - Product description
- `rating` - 1-5 rating
- `created_at` - Timestamp
- `image`/`image_url` - Image filename (stored under `static/images/`) or external URL (default: 'default.jpg')

  **Branded products & images:**
  - The development seed script (`reset_seed.py`) now populates the database with brand‑name items (Cetaphil, Minimalist, Pantene, etc.) using placeholder URLs labeled with the brand.
  - When you add or edit a product in the **Admin → Products** interface you may either type a filename/URL or use the **Upload Image** field at the bottom of the form.  Uploaded files are validated (JPG/PNG/GIF/WEBP, max 5 MB, minimum 100×100px) and saved into `app/static/images/` with a random UUID name.
  - To use your own photos outside the web form, simply place them in `app/static/images/` and either:
    * enter the filename (e.g. `cetaphil.jpg`) in the text box, or
    * update the `image_url` column directly (via seed script or database tool).
  - External URLs are also supported (e.g. `https://example.com/cetaphil.jpg`). Ensure the links are reachable and licensed for your use.

### User
- `id` - Primary key
- `username` - Display name
- `email` - Unique email
- `phone` - Phone number (optional)
- `password_hash` - Hashed password
- `skin_type` - Optional skin type preference
- `role` - 'user' or 'admin'
- `created_at` - Account creation timestamp

## API Endpoints (JSON)

The application includes a few simple AJAX endpoints used by the UI. All
`POST` requests require a CSRF token which is automatically injected into
`window.__CSRF_TOKEN` by the base template.


### Shopping Cart
- `POST /add-to-cart` - Add product to cart
  ```json
  {"product_id": 1, "qty": 1}
  ```

- `POST /update-cart` - Update product quantity
  ```json
  {"product_id": 1, "qty": 2}
  ```

- `POST /clear-cart` - Clear entire cart
  ```json
  {}
  ```

### Search
- `GET /api/search?q=neem` - Search products

## Customization

### Theme Colors
Edit `app/static/css/style.css` to change:
- `--pink: #F8C8DC` (Primary pink)
- `--green: #90EE90` (Secondary green)

### Sample Products
Edit `database.py` to modify the 20 seeded products or add more.

### Assigning Your Own Photos
If you've placed real product images in `app/static/images` you can run
`assign_images.py` to automatically update the database records. The
script will try to match filenames by product name slug or id. You can also
provide an explicit CSV mapping (`product_id,filename`). Example:

```bash
python assign_images.py              # auto-match
python assign_images.py --dir path/to/photos
python assign_images.py --map mapping.csv
```

This is useful when you download brand photos and want the app to serve
them instead of placeholders.

## Security Notes

⚠️ **Development Only** - The following are for development use only:

- `app.secret_key = 'dev-secret-change-me'` - Must be changed for production
- No CSRF protection (add Flask-WTF for production)
- No rate limiting on auth endpoints
- Plain session storage (use Redis for production)
- No email verification

For production, implement:
- Environment variable for SECRET_KEY
- CSRF tokens
- Rate limiting
- Secure password policies
- Email verification
- HTTPS only

## Running Locally

Complete quick start:

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Initialize database
python database.py

# 3. Start server
python app.py

# 4. Visit http://localhost:5000

# 5. Register a test account & make it admin:
# python make_admin.py test@example.com
```

Then log in and visit `/admin/dashboard` to manage products.

## Future Enhancements

- 🤖 AI-powered skin/hair analysis (CNN model)
- 💰 Real payment gateway integration (Stripe/Razorpay)
- 📧 Email notifications & order tracking
- ⭐ Customer reviews & ratings
- 🎁 Wishlist functionality
- 📊 Analytics dashboard
- 🔍 Advanced search & filters
- 📦 Order management system

## Contributing

Feel free to fork, modify, and improve this project!

## License

MIT License - Feel free to use for personal/commercial projects.

---

**Built with ❤️ for skincare & haircare enthusiasts**
