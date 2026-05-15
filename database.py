import os
import re
import requests

from app import db
from models import Product, User
import sys

# if you have an Unsplash API access key, set it via environment variable
UNSPLASH_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

def download_unsplash_image(query: str) -> str | None:
    """Search Unsplash for *query* and save the first result locally.
    Returns the filename (relative to static/images) or None if the search fails."""
    if not UNSPLASH_KEY:
        return None
    params = {'query': query, 'per_page': 1}
    headers = {'Authorization': f'Client-ID {UNSPLASH_KEY}'}
    try:
        resp = requests.get('https://api.unsplash.com/search/photos',
                            params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        results = data.get('results') or []
        if not results:
            return None
        url = results[0]['urls']['regular']
        # create safe filename from query
        fname = re.sub(r"[^\w]+", '_', query.lower()).strip('_') + '.jpg'
        outdir = os.path.join(os.path.dirname(__file__), 'app', 'static', 'images')
        os.makedirs(outdir, exist_ok=True)
        outpath = os.path.join(outdir, fname)
        image_resp = requests.get(url, timeout=10)
        image_resp.raise_for_status()
        with open(outpath, 'wb') as f:
            f.write(image_resp.content)
        return fname
    except Exception:
        return None


def init_db(app):
    """Create tables and seed the database with sample products."""
    with app.app_context():
        # Recreate tables
        db.drop_all()
        db.create_all()

        items = [
            # SKINCARE (30 products)
            {"name":"Lakme Vitamin C Serum","category":"skin","skin_type":"Normal","price":799.0,"description":"Brightening vitamin C serum with antioxidants","image":"https://via.placeholder.com/300x300?text=Lakme+VitC","rating":4.4},
            {"name":"Mamaearth Salicylic Acid Cleanser","category":"skin","skin_type":"Oily","price":499.0,"description":"Gentle salicylic acid cleanser for acne-prone skin","image":"https://via.placeholder.com/300x300?text=Mamaearth+Salicylic","rating":4.5},
            {"name":"Loreal SPF 50 Sunscreen","category":"skin","skin_type":"All","price":599.0,"description":"Broad spectrum SPF 50 sunscreen protection","image":"https://via.placeholder.com/300x300?text=Loreal+SPF50","rating":4.6},
            {"name":"Neutrogena Hydro Boost Gel","category":"skin","skin_type":"Dry","price":1099.0,"description":"Hydrating gel-cream with hyaluronic acid","image":"https://via.placeholder.com/300x300?text=Neutrogena+Hydro","rating":4.7},
            {"name":"The Face Shop Rice Water Toner","category":"skin","skin_type":"All","price":450.0,"description":"Brightening rice water toner for all skin types","image":"https://via.placeholder.com/300x300?text=Face+Shop+Rice","rating":4.2},
            {"name":"Kiehls Midnight Recovery Oil","category":"skin","skin_type":"Dry","price":3200.0,"description":"Night facial oil for skin repair and regeneration","image":"https://via.placeholder.com/300x300?text=Kiehls+Midnight","rating":4.8},
            {"name":"Biotique Bio Cucumber Lotion","category":"skin","skin_type":"Normal","price":350.0,"description":"Soothing cucumber lotion for hydration","image":"https://via.placeholder.com/300x300?text=Biotique+Cucumber","rating":4.1},
            {"name":"Cetaphil Daily Facial Cleanser","category":"skin","skin_type":"Sensitive","price":650.0,"description":"Gentle daily cleanser for sensitive skin","image":"https://via.placeholder.com/300x300?text=Cetaphil+Cleanser","rating":4.6},
            {"name":"Simple Kind To Skin Moisturizer","category":"skin","skin_type":"All","price":299.0,"description":"Lightweight everyday moisturizer for all skin types","image":"https://via.placeholder.com/300x300?text=Simple+Moisturizer","rating":4.0},
            {"name":"Olay Regenerist Cream","category":"skin","skin_type":"Mature","price":1499.0,"description":"Anti-ageing cream with peptides and amino acids","image":"https://via.placeholder.com/300x300?text=Olay+Regenerist","rating":4.3},
            {"name":"Neem Face Wash","category":"skin","skin_type":"Oily","price":299.0,"description":"Neem and turmeric face wash for acne control","image":"https://via.placeholder.com/300x300?text=Neem+FaceWash","rating":4.4},
            {"name":"Himalaya Herbals Moisturizing Cream","category":"skin","skin_type":"Dry","price":225.0,"description":"Herbal moisturizer with natural oils","image":"https://via.placeholder.com/300x300?text=Himalaya+Cream","rating":4.2},
            {"name":"Vicco Turmeric Cream","category":"skin","skin_type":"All","price":85.0,"description":"Traditional turmeric cream for skin brightening","image":"https://via.placeholder.com/300x300?text=Vicco+Turmeric","rating":4.0},
            {"name":"Azelaic Acid Treatment","category":"skin","skin_type":"Oily","price":1899.0,"description":"Advanced azelaic acid for rosacea and acne","image":"https://via.placeholder.com/300x300?text=Azelaic+Acid","rating":4.5},
            {"name":"Rose Water Toner","category":"skin","skin_type":"Sensitive","price":199.0,"description":"Pure rose water toner for sensitive skin","image":"https://via.placeholder.com/300x300?text=Rose+Water","rating":4.1},
            {"name":"Aloe Vera Gel","category":"skin","skin_type":"All","price":149.0,"description":"Pure aloe vera gel for soothing and hydration","image":"https://via.placeholder.com/300x300?text=Aloe+Vera+Gel","rating":4.3},
            {"name":"Retinol Night Cream","category":"skin","skin_type":"Mature","price":1299.0,"description":"Retinol-rich night cream for anti-ageing","image":"https://via.placeholder.com/300x300?text=Retinol+Cream","rating":4.6},
            {"name":"Hyaluronic Acid Serum","category":"skin","skin_type":"Dry","price":899.0,"description":"Deep hydrating hyaluronic acid serum","image":"https://via.placeholder.com/300x300?text=Hyaluronic+Acid","rating":4.7},
            {"name":"Vitamin E Oil","category":"skin","skin_type":"All","price":399.0,"description":"Pure vitamin E oil for skin nourishment","image":"https://via.placeholder.com/300x300?text=Vitamine+E","rating":4.4},
            {"name":"Glycolic Acid Exfoliant","category":"skin","skin_type":"Oily","price":699.0,"description":"Chemical exfoliant with glycolic acid","image":"https://via.placeholder.com/300x300?text=Glycolic+Acid","rating":4.5},
            {"name":"Charcoal Face Mask","category":"skin","skin_type":"Oily","price":349.0,"description":"Detoxifying charcoal mask for deep cleansing","image":"https://via.placeholder.com/300x300?text=Charcoal+Mask","rating":4.2},
            {"name":"Peptide Eye Cream","category":"skin","skin_type":"All","price":1199.0,"description":"Eye cream with peptides for fine lines","image":"https://via.placeholder.com/300x300?text=Peptide+Eye","rating":4.6},
            {"name":"Salicylic Acid Toner","category":"skin","skin_type":"Oily","price":499.0,"description":"Weekly toner with salicylic acid for pores","image":"https://via.placeholder.com/300x300?text=Salicylic+Toner","rating":4.3},
            {"name":"Kojic Acid Soap","category":"skin","skin_type":"All","price":199.0,"description":"Kojic acid soap for brightening skin","image":"https://via.placeholder.com/300x300?text=Kojic+Acid","rating":4.1},
            {"name":"Tea Tree Oil Spot Treatment","category":"skin","skin_type":"Oily","price":299.0,"description":"Concentrated tea tree oil for acne spots","image":"https://via.placeholder.com/300x300?text=Tea+Tree","rating":4.4},
            {"name":"Snail Mucin Essence","category":"skin","skin_type":"All","price":799.0,"description":"K-beauty snail mucin essence for hydration","image":"https://via.placeholder.com/300x300?text=Snail+Mucin","rating":4.5},
            {"name":"Vitamin C Brightening Mask","category":"skin","skin_type":"Normal","price":549.0,"description":"Peel-off mask with vitamin C for brightening","image":"https://via.placeholder.com/300x300?text=VitC+Mask","rating":4.3},
            {"name":"Sulfur Acne Soap","category":"skin","skin_type":"Oily","price":175.0,"description":"Traditional sulfur soap for acne control","image":"https://via.placeholder.com/300x300?text=Sulfur+Soap","rating":4.0},
            {"name":"Lactic Acid Toner","category":"skin","skin_type":"Dry","price":649.0,"description":"Gentle lactic acid for sensitive skin exfoliation","image":"https://via.placeholder.com/300x300?text=Lactic+Acid","rating":4.4},
            {"name":"Micellar Water","category":"skin","skin_type":"All","price":349.0,"description":"Gentle micellar water makeup remover","image":"https://via.placeholder.com/300x300?text=Micellar+Water","rating":4.2},
            # HAIRCARE (25 products)
            {"name":"Head & Shoulders Anti-Dandruff Shampoo","category":"hair","hair_type":"Dandruff","price":199.0,"description":"Clinically proven anti-dandruff shampoo","image":"https://via.placeholder.com/300x300?text=Head+Shoulders","rating":4.2},
            {"name":"Khadi Onion Hair Oil","category":"hair","hair_type":"Hair fall","price":249.0,"description":"Organic onion oil to reduce hair fall","image":"https://via.placeholder.com/300x300?text=Khadi+Onion","rating":4.0},
            {"name":"Dove Argan Oil Conditioner","category":"hair","hair_type":"Dry","price":299.0,"description":"Argan oil infused conditioner for smooth hair","image":"https://via.placeholder.com/300x300?text=Dove+Argan","rating":4.3},
            {"name":"Loreal Total Repair 5 Shampoo","category":"hair","hair_type":"Damaged","price":399.0,"description":"Repairing shampoo for severely damaged hair","image":"https://via.placeholder.com/300x300?text=Loreal+Repair","rating":4.4},
            {"name":"St. Botanica Moroccan Argan Oil","category":"hair","hair_type":"Dry","price":599.0,"description":"Pure argan oil for deep nourishment","image":"https://via.placeholder.com/300x300?text=Argan+Oil","rating":4.5},
            {"name":"WOW Onion Shampoo","category":"hair","hair_type":"Hair fall","price":449.0,"description":"Onion enriched shampoo to reduce hair fall","image":"https://via.placeholder.com/300x300?text=WOW+Onion","rating":4.1},
            {"name":"Biotique Bhringraj Shampoo","category":"hair","hair_type":"Hair fall","price":275.0,"description":"Ayurvedic bhringraj shampoo for hair growth","image":"https://via.placeholder.com/300x300?text=Bhringraj","rating":4.0},
            {"name":"Pantene Pro-V Conditioner","category":"hair","hair_type":"All","price":325.0,"description":"Smooth & shiny conditioner for all hair types","image":"https://via.placeholder.com/300x300?text=Pantene+ProV","rating":4.1},
            {"name":"Forest Essentials Hair Serum","category":"hair","hair_type":"Dry","price":1299.0,"description":"Luxury hair serum for shine and smoothness","image":"https://via.placeholder.com/300x300?text=Forest+Serum","rating":4.7},
            {"name":"Mamaearth Onion Hair Mask","category":"hair","hair_type":"Hair fall","price":349.0,"description":"Repair mask with onion and keratin","image":"https://via.placeholder.com/300x300?text=Mamaearth+Mask","rating":4.2},
            {"name":"Coconut Hair Oil","category":"hair","hair_type":"Dry","price":229.0,"description":"Pure virgin coconut oil for hair nourishment","image":"https://via.placeholder.com/300x300?text=Coconut+Oil","rating":4.3},
            {"name":"Neem Hair Oil","category":"hair","hair_type":"Dandruff","price":199.0,"description":"Neem oil for scalp health and dandruff control","image":"https://via.placeholder.com/300x300?text=Neem+Oil","rating":4.1},
            {"name":"Keratin Smoothing Shampoo","category":"hair","hair_type":"Frizzy","price":599.0,"description":"Keratin infused shampoo for smooth frizz-free hair","image":"https://via.placeholder.com/300x300?text=Keratin+Shampoo","rating":4.4},
            {"name":"Apple Cider Vinegar Hair Rinse","category":"hair","hair_type":"Oily","price":299.0,"description":"Natural clarifying hair rinse with apple cider vinegar","image":"https://via.placeholder.com/300x300?text=ACV+Rinse","rating":4.0},
            {"name":"Tea Tree Oil Scalp Treatment","category":"hair","hair_type":"Dandruff","price":449.0,"description":"Tea tree oil for scalp itching and dandruff","image":"https://via.placeholder.com/300x300?text=Tea+Tree+Oil","rating":4.3},
            {"name":"Rice Bran Hair Mask","category":"hair","hair_type":"Dry","price":399.0,"description":"Rice bran mask for deep conditioning","image":"https://via.placeholder.com/300x300?text=Rice+Bran+Mask","rating":4.2},
            {"name":"Rosemary Hair Growth Oil","category":"hair","hair_type":"Hair fall","price":349.0,"description":"Rosemary oil to stimulate hair growth","image":"https://via.placeholder.com/300x300?text=Rosemary+Oil","rating":4.4},
            {"name":"Almond Oil Hair Serum","category":"hair","hair_type":"All","price":329.0,"description":"Almond oil serum for shine and strength","image":"https://via.placeholder.com/300x300?text=Almond+Serum","rating":4.1},
            {"name":"Amla Hair Powder","category":"hair","hair_type":"Hair fall","price":149.0,"description":"Dried amla powder for hair strength","image":"https://via.placeholder.com/300x300?text=Amla+Powder","rating":4.0},
            {"name":"Castor Oil","category":"hair","hair_type":"Hair fall","price":249.0,"description":"Pure castor oil for hair growth","image":"https://via.placeholder.com/300x300?text=Castor+Oil","rating":4.2},
            {"name":"Henna Hair Color","category":"hair","hair_type":"All","price":199.0,"description":"Natural henna for hair color and conditioning","image":"https://via.placeholder.com/300x300?text=Henna+Color","rating":4.3},
            {"name":"Shikakai Natural Shampoo","category":"hair","hair_type":"All","price":199.0,"description":"Herbal shikakai shampoo for natural cleansing","image":"https://via.placeholder.com/300x300?text=Shikakai","rating":4.1},
            {"name":"Hibiscus Hair Pack","category":"hair","hair_type":"Dry","price":279.0,"description":"Hibiscus and fenugreek hair conditioning pack","image":"https://via.placeholder.com/300x300?text=Hibiscus+Pack","rating":4.2},
            {"name":"Argan & Coconut Hair Spray","category":"hair","hair_type":"Frizzy","price":399.0,"description":"Leave-in spray with argan and coconut oil","image":"https://via.placeholder.com/300x300?text=Argan+Spray","rating":4.4},
            {"name":"Biotin Hair Growth Tablets","category":"hair","hair_type":"All","price":899.0,"description":"Biotin supplement for stronger hair growth","image":"https://via.placeholder.com/300x300?text=Biotin+Tablets","rating":4.5},
        ]

        for data in items:
            # attempt to fetch a real photo from Unsplash if we have a key
            filename = data.get('image')
            if UNSPLASH_KEY:
                downloaded = download_unsplash_image(data['name'])
                if downloaded:
                    filename = downloaded

            prod = Product(
                name=data.get('name'),
                category=data.get('category'),
                skin_type=data.get('skin_type'),
                hair_type=data.get('hair_type'),
                price=data.get('price'),
                description=data.get('description'),
                image=filename,
                rating=data.get('rating', 4.5)
            )
            db.session.add(prod)

        db.session.commit()
        print(f"Database initialized with {len(items)} sample products with images!")

        # Create a default admin user so admin UI is reachable after reseed.
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'secret123')
        admin_name = os.getenv('ADMIN_NAME', 'Site Admin')

        try:
            existing = User.query.filter_by(email=admin_email).first()
            if existing:
                existing.is_admin = True
                existing.set_password(admin_pass)
                db.session.commit()
                print(f"Promoted existing user '{existing.email}' to admin.")
            else:
                u = User(full_name=admin_name, email=admin_email)
                u.set_password(admin_pass)
                u.is_admin = True
                db.session.add(u)
                db.session.commit()
                print(f"Created default admin {admin_email}")
        except Exception as e:
            print('Failed to create default admin:', e, file=sys.stderr)


if __name__ == '__main__':
    # Allow running this file directly to initialize DB
    from app import create_app

    app = create_app()
    init_db(app)
