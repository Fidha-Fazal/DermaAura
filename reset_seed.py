from app import create_app, db
from models import User, Product
import os

def reset_and_seed():
    """Reset all data and reseed with fresh products"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Dropping all tables...")
        db.drop_all()
        
        print("🔄 Recreating tables...")
        db.create_all()
        
        # Create admin
        admin = User(
            email='admin@test.com',
            username='Admin User',
            phone='9876543210',
            role='admin'
        )
        admin.set_password('testpass123')
        db.session.add(admin)
        print("✓ Admin user created: admin@test.com / testpass123")
        
        # SKINCARE PRODUCTS (branded with local placeholder images)
        skincare_specs = [
            {
                'name': 'Cetaphil Moisturizing Lotion',
                'price': 699,
                'skin_type': 'Dry & Sensitive',
                'description': 'Lightweight moisturizer trusted by dermatologists',
                'rating': 4.6,
                'brand': 'cetaphil',
                'image_url': 'https://via.placeholder.com/300?text=Cetaphil+Moisturizing+Lotion'
            },
            {
                'name': 'Cetaphil Gentle Skin Cleanser',
                'price': 549,
                'skin_type': 'All Skin Types',
                'description': 'Iconic gentle cleanser for sensitive skin',
                'rating': 4.5,
                'brand': 'cetaphil',
                'image_url': 'https://via.placeholder.com/300?text=Cetaphil+Cleanser'
            },
            {
                'name': 'Minimalist 10% Vitamin C Serum',
                'price': 749,
                'skin_type': 'All Skin Types',
                'description': 'Stable Vitamin C serum for brightening and glow',
                'rating': 4.7,
                'brand': 'minimalist',
                'image_url': 'https://via.placeholder.com/300?text=Minimalist+Vitamin+C'
            },
            {
                'name': 'Minimalist 12% Niacinamide Serum',
                'price': 699,
                'skin_type': 'Oily & Acne Prone',
                'description': 'Helps reduce pores and regulate sebum',
                'rating': 4.6,
                'brand': 'minimalist',
                'image_url': 'https://via.placeholder.com/300?text=Minimalist+Niacinamide'
            },
            {
                'name': 'Beauty of Joseon Glow Serum',
                'price': 849,
                'skin_type': 'All Skin Types',
                'description': 'Korean serum for radiant skin and clarity',
                'rating': 4.7,
                'brand': 'beauty_of_joseon',
                'image_url': 'https://via.placeholder.com/300?text=Beauty+of+Joseon+Glow+Serum'
            },
            {
                'name': 'Beauty of Joseon Radiance Cleansing Balm',
                'price': 999,
                'skin_type': 'All Skin Types',
                'description': 'Oil-to-milk cleanser for gentle makeup removal',
                'rating': 4.8,
                'brand': 'beauty_of_joseon',
                'image_url': 'https://via.placeholder.com/300?text=BoJ+Cleansing+Balm'
            },
            {
                'name': 'The Ordinary Niacinamide 10% + Zinc 1%',
                'price': 399,
                'skin_type': 'Oily & Acne Prone',
                'description': 'High-strength vitamin and mineral blemish formula',
                'rating': 4.5,
                'brand': 'the_ordinary',
                'image_url': 'https://via.placeholder.com/300?text=The+Ordinary+Niacinamide'
            },
            {
                'name': 'La Roche-Posay Toleriane Double Repair Face Moisturizer',
                'price': 1299,
                'skin_type': 'All Skin Types',
                'description': 'Prebiotic thermal water to restore skin barrier',
                'rating': 4.8,
                'brand': 'la_roche_posay',
                'image_url': 'https://via.placeholder.com/300?text=La+Roche+Posay'
            },
            {
                'name': 'Neutrogena Hydro Boost Water Gel',
                'price': 849,
                'skin_type': 'Oily & Combination',
                'description': 'Hydrating gel-cream with hyaluronic acid',
                'rating': 4.7,
                'brand': 'neutrogena',
                'image_url': 'https://via.placeholder.com/300?text=Neutrogena+Hydro+Boost'
            },
            {
                'name': 'Lakme 9 to 5 Vitamin C Gel Creme',
                'price': 599,
                'skin_type': 'All Skin Types',
                'description': 'Daily moisturizer with antioxidant power',
                'rating': 4.3,
                'brand': 'lakme',
                'image_url': 'https://via.placeholder.com/300?text=Lakme+Vitamin+C'
            },
            {
                'name': 'Plum Green Tea Clear Face Wash',
                'price': 249,
                'skin_type': 'Oily & Acne Prone',
                'description': 'Salicylic acid infused face wash to prevent breakouts',
                'rating': 4.4,
                'brand': 'plum',
                'image_url': 'https://via.placeholder.com/300?text=Plum+Green+Tea'
            },
            {
                'name': 'Biotique Morning Nectar Flawless Skin Lotion',
                'price': 299,
                'skin_type': 'All Skin Types',
                'description': 'Natural ingredient-rich daily moisturizer',
                'rating': 4.2,
                'brand': 'biotique',
                'image_url': 'https://via.placeholder.com/300?text=Biotique+Lotion'
            },
            {
                'name': 'COSRX Advanced Snail 96 Mucin Power Essence',
                'price': 1099,
                'skin_type': 'Dry & Sensitive',
                'description': 'Snail mucin for hydration and repair',
                'rating': 4.8,
                'brand': 'cosrx',
                'image_url': 'https://via.placeholder.com/300?text=COSRX+Snail+Essence'
            },
            {
                'name': 'Olay Regenerist Micro-Sculpting Cream',
                'price': 1599,
                'skin_type': 'Mature & Fine Lines',
                'description': 'Anti-aging cream with hyaluronic acid',
                'rating': 4.6,
                'brand': 'olay',
                'image_url': 'https://via.placeholder.com/300?text=Olay+Regenerist'
            },
            {
                'name': 'Keep It Simple Vitamin E Face Oil',
                'price': 399,
                'skin_type': 'Dry Skin',
                'description': 'Pure vitamin E oil for soft skin',
                'rating': 4.0,
                'brand': 'keep_it_simple',
                'image_url': 'https://via.placeholder.com/300?text=Vitamin+E+Oil'
            },
            {
                'name': 'Clinique Moisture Surge 72-Hour Auto-Replenishing Hydrator',
                'price': 2499,
                'skin_type': 'All Skin Types',
                'description': 'Gel-cream that continuously delivers hydration',
                'rating': 4.9,
                'brand': 'clinique',
                'image_url': 'https://via.placeholder.com/300?text=Clinique+Moisture+Surge'
            },
        ]
        
        # helper to generate placeholder image locally
        def make_placeholder(brand_name):
            from PIL import Image, ImageDraw, ImageFont
            fname = f"{brand_name}.png"
            path = os.path.join(app.root_path, 'static', 'images', fname)
            if os.path.exists(path):
                return fname
            # create simple image
            img = Image.new('RGB', (300, 300), color=(240,240,240))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype('arial.ttf', 24)
            except Exception:
                font = ImageFont.load_default()
            text = brand_name.replace('_', ' ').title()
            # compute text size
            try:
                bbox = draw.textbbox((0,0), text, font=font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
            except AttributeError:
                w, h = font.getsize(text)
            draw.text(((300-w)/2,(300-h)/2), text, fill=(50,50,50), font=font)
            img.save(path)
            return fname
        
        # convert specs into Product objects, generating image files
        skincare = []
        for spec in skincare_specs:
            # if a real URL is provided, use it directly; otherwise fallback to local placeholder
            if spec.get('image_url'):
                imgfile = spec['image_url']
            else:
                imgfile = make_placeholder(spec['brand'])
            skincare.append(Product(
                name=spec['name'],
                category='skin',
                price=spec['price'],
                skin_type=spec['skin_type'],
                description=spec['description'],
                rating=spec['rating'],
                image_url=imgfile
            ))

        
        # HAIRCARE PRODUCTS (branded with local placeholders)
        haircare_specs = [
            {'name': 'Pantene Pro-V Anti Hair Fall Shampoo', 'price': 349, 'hair_type': 'Hair Fall Prone', 'description': 'Nourishes roots and reduces breakage', 'rating': 4.5, 'brand': 'pantene', 'image_url': 'https://via.placeholder.com/300?text=Pantene+Anti+Hair+Fall'},
            {'name': 'Head & Shoulders Cool Menthol Shampoo', 'price': 399, 'hair_type': 'Dandruff & Oily', 'description': 'Anti-dandruff formula with menthol cool', 'rating': 4.6, 'brand': 'head_shoulders', 'image_url': 'https://via.placeholder.com/300?text=H%26S+Menthol'},
            {'name': 'L’Oreal Paris Total Repair 5 Masque', 'price': 549, 'hair_type': 'Dry & Damaged', 'description': 'Deep conditioning mask for five signs of damage', 'rating': 4.7, 'brand': 'loreal', 'image_url': 'https://via.placeholder.com/300?text=Loreal+Repair+5'},
            {'name': 'Tresemme Keratin Smooth Conditioner', 'price': 429, 'hair_type': 'Frizzy & Unruly', 'description': 'Smoothens hair and adds shine', 'rating': 4.4, 'brand': 'tresemme', 'image_url': 'https://via.placeholder.com/300?text=Tresemme+Keratin'},
            {'name': 'Mamaearth Argan Hair Oil', 'price': 599, 'hair_type': 'All Hair Types', 'description': 'Organic argan oil for long, shiny hair', 'rating': 4.8, 'brand': 'mamaearth', 'image_url': 'https://via.placeholder.com/300?text=Mamaearth+Argan+Oil'},
            {'name': 'The Body Shop Ginger Scalp Care Shampoo', 'price': 799, 'hair_type': 'Dry Scalp', 'description': 'Stimulates circulation and soothes scalp', 'rating': 4.5, 'brand': 'body_shop', 'image_url': 'https://via.placeholder.com/300?text=TBS+Ginger+Shampoo'},
            {'name': 'L’Oreal Paris Extraordinary Oil Serum', 'price': 699, 'hair_type': 'All Hair Types', 'description': 'Luxurious serum for frizz control and shine', 'rating': 4.6, 'brand': 'loreal_serum', 'image_url': 'https://via.placeholder.com/300?text=Loreal+Oil+Serum'},
            {'name': 'Garnier Fructis Grow Strong Shampoo', 'price': 349, 'hair_type': 'Thin Weak Hair', 'description': 'Strengthens hair fiber from root to tip', 'rating': 4.4, 'brand': 'garnier', 'image_url': 'https://via.placeholder.com/300?text=Garnier+Grow+Strong'},
            {'name': 'Dabur Amla Hair Oil', 'price': 459, 'hair_type': 'All Hair Types', 'description': 'Traditional oil for strong, shiny hair', 'rating': 4.2, 'brand': 'dabur_amla', 'image_url': 'https://via.placeholder.com/300?text=Dabur+Amla+Oil'},
            {'name': 'Sunsilk Perfect Straight Conditioner', 'price': 319, 'hair_type': 'Frizzy Hair', 'description': 'Anti-frizz conditioner for straight look', 'rating': 4.3, 'brand': 'sunsilk', 'image_url': 'https://via.placeholder.com/300?text=Sunsilk+Perfect+Straight'},
            {'name': 'Biotique Bio Bhringraj Therapeutic Oil', 'price': 299, 'hair_type': 'All Hair Types', 'description': 'Herbal oil for hair growth and shine', 'rating': 4.1, 'brand': 'biotique_hair', 'image_url': 'https://via.placeholder.com/300?text=Biotique+Bhringraj'},
            {'name': 'Nykaa Naturals Rosemary & Mint Shampoo', 'price': 299, 'hair_type': 'Oily Hair', 'description': 'Refreshing shampoo with rosemary & mint', 'rating': 4.0, 'brand': 'nykaa_rosmary', 'image_url': 'https://via.placeholder.com/300?text=Nykaa+Rosemary+Shampoo'},
            {'name': 'Love Beauty and Planet Coconut Water & Mimosa Flower Shampoo', 'price': 349, 'hair_type': 'Dry Hair', 'description': 'Eco-friendly shampoo for hydration', 'rating': 4.2, 'brand': 'love_beauty_planet', 'image_url': 'https://via.placeholder.com/300?text=Love+Beauty+Planet'},
            {'name': 'Forest Essentials Bhringraj Hair Conditioner', 'price': 1299, 'hair_type': 'Dry & Damaged', 'description': 'Ayurvedic conditioner for nourishing hair', 'rating': 4.5, 'brand': 'forest_essentials', 'image_url': 'https://via.placeholder.com/300?text=Forest+Essentials+Conditioner'},
            {'name': 'Khadi Natural Amla & Bhringraj Shampoo', 'price': 299, 'hair_type': 'All Hair Types', 'description': 'Herbal formula for stronger roots', 'rating': 4.1, 'brand': 'khadi', 'image_url': 'https://via.placeholder.com/300?text=Khadi+Amla+Shampoo'},
        ]
        
        haircare = []
        for spec in haircare_specs:
            if spec.get('image_url'):
                imgfile = spec['image_url']
            else:
                imgfile = make_placeholder(spec['brand'])
            haircare.append(Product(
                name=spec['name'],
                category='hair',
                price=spec['price'],
                hair_type=spec['hair_type'],
                description=spec['description'],
                rating=spec['rating'],
                image_url=imgfile
            ))

        
        all_products = skincare + haircare
        for product in all_products:
            db.session.add(product)
        
        db.session.commit()
        print(f"\n✓ Successfully seeded {len(all_products)} products")
        print(f"  - Skincare: {len(skincare)}")
        print(f"  - Haircare: {len(haircare)}")
        print("\n✓ Database reset and seeding complete!")

if __name__ == '__main__':
    reset_and_seed()
