from app import create_app, db
from models import User, Product
import os

def seed_large_dataset():
    """Reset all data and seed 60+ products for a robust e-commerce experience."""
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
        print("✓ Admin user created: admin@test.com / pass: testpass123")
        
        # 30 SKINCARE PRODUCTS
        skincare_specs = [
            {'name': 'Cetaphil Moisturizing Lotion', 'price': 699, 'skin_type': 'Dry & Sensitive', 'target_condition': 'Dry & Sensitive', 'description': 'Lightweight moisturizer trusted by dermatologists', 'rating': 4.6, 'brand': 'Cetaphil'},
            {'name': 'Cetaphil Gentle Skin Cleanser', 'price': 549, 'skin_type': 'All Skin Types', 'target_condition': 'Dry & Sensitive', 'description': 'Iconic gentle cleanser for sensitive skin', 'rating': 4.5, 'brand': 'Cetaphil'},
            {'name': 'Minimalist 10% Vitamin C Serum', 'price': 749, 'skin_type': 'All', 'target_condition': 'Dullness', 'description': 'Stable Vitamin C serum for brightening', 'rating': 4.7, 'brand': 'Minimalist'},
            {'name': 'Minimalist 2% Salicylic Acid', 'price': 699, 'skin_type': 'Oily & Acne Prone', 'target_condition': 'Oily & Acne Prone', 'description': 'Exfoliant for acne and blackheads', 'rating': 4.6, 'brand': 'Minimalist'},
            {'name': 'Minimalist 5% Niacinamide Body Lotion', 'price': 499, 'skin_type': 'Dry', 'target_condition': 'Dry & Sensitive', 'description': 'Nourishes body and smooths skin', 'rating': 4.5, 'brand': 'Minimalist'},
            {'name': 'Plum Green Tea Clear Face Wash', 'price': 249, 'skin_type': 'Oily & Acne Prone', 'target_condition': 'Oily & Acne Prone', 'description': 'Salicylic acid infused face wash', 'rating': 4.4, 'brand': 'Plum'},
            {'name': 'Plum Green Tea Oil-Free Moisturizer', 'price': 399, 'skin_type': 'Oily', 'target_condition': 'Oily & Acne Prone', 'description': 'Light moisturizer with green tea', 'rating': 4.5, 'brand': 'Plum'},
            {'name': 'Lakme 9 to 5 Vitamin C Gel', 'price': 599, 'skin_type': 'All Skin Types', 'target_condition': 'Dullness', 'description': 'Vitamin C gel creme pack', 'rating': 4.3, 'brand': 'Lakme'},
            {'name': 'Lakme Absolute Perfect Radiance', 'price': 899, 'skin_type': 'Normal', 'target_condition': 'Combination', 'description': 'Skin brightening day cream', 'rating': 4.4, 'brand': 'Lakme'},
            {'name': 'Neutrogena Hydro Boost Water Gel', 'price': 849, 'skin_type': 'Oily & Combination', 'target_condition': 'Combination', 'description': 'Gel-cream with hyaluronic acid', 'rating': 4.7, 'brand': 'Neutrogena'},
            {'name': 'Neutrogena Deep Clean Scrub', 'price': 329, 'skin_type': 'Oily', 'target_condition': 'Oily & Acne Prone', 'description': 'Exfoliating wash for deep cleaning', 'rating': 4.3, 'brand': 'Neutrogena'},
            {'name': 'La Roche-Posay Effaclar Purifying Foaming Gel', 'price': 1499, 'skin_type': 'Oily & Acne Prone', 'target_condition': 'Oily & Acne Prone', 'description': 'Cleansing gel for acne', 'rating': 4.8, 'brand': 'La_Roche_Posay'},
            {'name': 'Olay Regenerist Micro-Sculpting Cream', 'price': 1599, 'skin_type': 'Mature', 'target_condition': 'Aging', 'description': 'Anti-aging moisturizer', 'rating': 4.6, 'brand': 'Olay'},
            {'name': 'Olay Luminous Vitamin C Serum', 'price': 1299, 'skin_type': 'All', 'target_condition': 'Dullness', 'description': 'Glow boosting daily serum', 'rating': 4.5, 'brand': 'Olay'},
            {'name': 'Biotique Morning Nectar Flawless Lotion', 'price': 299, 'skin_type': 'All', 'target_condition': 'Combination', 'description': 'Ayurvedic clear skin lotion', 'rating': 4.2, 'brand': 'Biotique'},
            {'name': 'Biotique Bio Papaya Tan Removal Scrub', 'price': 199, 'skin_type': 'All', 'target_condition': 'Dullness', 'description': 'Exfoliant to remove tan', 'rating': 4.3, 'brand': 'Biotique'},
            {'name': 'Mamaearth Ubtan Face Wash', 'price': 299, 'skin_type': 'All', 'target_condition': 'Dullness', 'description': 'Tan removal with turmeric & saffron', 'rating': 4.4, 'brand': 'Mamaearth'},
            {'name': 'Mamaearth Vitamin C Sleeping Mask', 'price': 499, 'skin_type': 'All', 'target_condition': 'Dry & Sensitive', 'description': 'Overnight radiance booster', 'rating': 4.5, 'brand': 'Mamaearth'},
            {'name': 'COSRX Snail Mucin 96% Power Essence', 'price': 1099, 'skin_type': 'Dry & Sensitive', 'target_condition': 'Dry & Sensitive', 'description': 'repairing barrier and intense hydration', 'rating': 4.8, 'brand': 'COSRX'},
            {'name': 'The Ordinary Niacinamide 10% + Zinc 1%', 'price': 399, 'skin_type': 'Oily & Acne Prone', 'target_condition': 'Oily & Acne Prone', 'description': 'High-strength vitamin and mineral blemish formula', 'rating': 4.5, 'brand': 'The_Ordinary'},
            {'name': 'Clinique Moisture Surge 72-Hour', 'price': 2499, 'skin_type': 'All', 'target_condition': 'Dry & Sensitive', 'description': 'Auto-replenishing hydrator', 'rating': 4.9, 'brand': 'Clinique'},
            {'name': 'CeraVe Hydrating Facial Cleanser', 'price': 1299, 'skin_type': 'Dry', 'target_condition': 'Dry & Sensitive', 'description': 'Cleanser for normal to dry skin with ceramides', 'rating': 4.7, 'brand': 'CeraVe'},
            {'name': 'CeraVe Moisturizing Cream', 'price': 1499, 'skin_type': 'Dry', 'target_condition': 'Dry & Sensitive', 'description': 'Barrier repair cream', 'rating': 4.8, 'brand': 'CeraVe'},
            {'name': 'Beauty of Joseon Relief Sun Rice + Probiotics', 'price': 1250, 'skin_type': 'All', 'target_condition': 'Combination', 'description': 'Korean Sunscreen', 'rating': 4.8, 'brand': 'Beauty_of_Joseon'},
            {'name': 'Laneige Lip Sleeping Mask', 'price': 1300, 'skin_type': 'All', 'target_condition': 'Dry Lips', 'description': 'Berry flavor lip repair mask', 'rating': 4.7, 'brand': 'Laneige'},
            {'name': 'Glow Recipe Watermelon Glow PHA+BHA', 'price': 2500, 'skin_type': 'All', 'target_condition': 'Combination', 'description': 'Pore-tightening toner', 'rating': 4.6, 'brand': 'Glow_Recipe'},
            {'name': 'Innisfree Green Tea Seed Serum', 'price': 1950, 'skin_type': 'Combination', 'target_condition': 'Combination', 'description': 'Deep hydration serum', 'rating': 4.5, 'brand': 'Innisfree'},
            {'name': 'Pixi Glow Tonic 5% Glycolic Acid', 'price': 1500, 'skin_type': 'All', 'target_condition': 'Dullness', 'description': 'Exfoliating toner', 'rating': 4.6, 'brand': 'Pixi'},
            {'name': 'Paula\'s Choice 2% BHA Liquid Exfoliant', 'price': 2700, 'skin_type': 'Oily & Acne Prone', 'target_condition': 'Oily & Acne Prone', 'description': 'Salicylic acid leave-on exfoliant', 'rating': 4.8, 'brand': 'Paulas_Choice'},
            {'name': 'Kiehl\'s Ultra Facial Cream', 'price': 3200, 'skin_type': 'Dry', 'target_condition': 'Dry & Sensitive', 'description': '24-hour daily moisturizer', 'rating': 4.7, 'brand': 'Kiehls'},
        ]
        
        # 30 HAIRCARE PRODUCTS
        haircare_specs = [
            {'name': 'Pantene Pro-V Anti Hair Fall Shampoo', 'price': 349, 'hair_type': 'Hair Fall', 'target_condition': 'Hair Fall', 'description': 'Nourishes roots and reduces breakage', 'rating': 4.5, 'brand': 'Pantene'},
            {'name': 'Pantene Open Hair Miracle', 'price': 249, 'hair_type': 'Damaged & Frizzy', 'target_condition': 'Damaged & Frizzy', 'description': 'Leave-in conditioner and serum', 'rating': 4.4, 'brand': 'Pantene'},
            {'name': 'Head & Shoulders Cool Menthol', 'price': 399, 'hair_type': 'Dandruff', 'target_condition': 'Dandruff', 'description': 'Anti-dandruff formula with menthol', 'rating': 4.6, 'brand': 'Head_Shoulders'},
            {'name': 'Head & Shoulders Smooth & Silky', 'price': 379, 'hair_type': 'Dandruff', 'target_condition': 'Dandruff', 'description': 'Frizz control anti-dandruff', 'rating': 4.5, 'brand': 'Head_Shoulders'},
            {'name': 'L’Oreal Paris Total Repair 5 Masque', 'price': 549, 'hair_type': 'Damaged', 'target_condition': 'Damaged & Frizzy', 'description': 'Deep conditioning mask for damage', 'rating': 4.7, 'brand': 'Loreal'},
            {'name': 'L’Oreal Paris Extraordinary Oil Serum', 'price': 699, 'hair_type': 'All', 'target_condition': 'Damaged & Frizzy', 'description': 'Luxurious serum for frizz control', 'rating': 4.6, 'brand': 'Loreal'},
            {'name': 'Tresemme Keratin Smooth Shampoo', 'price': 429, 'hair_type': 'Frizzy', 'target_condition': 'Damaged & Frizzy', 'description': 'Smoothens hair and adds shine', 'rating': 4.4, 'brand': 'Tresemme'},
            {'name': 'Tresemme Keratin Smooth Conditioner', 'price': 449, 'hair_type': 'Frizzy', 'target_condition': 'Damaged & Frizzy', 'description': 'Detangling frizz control conditioner', 'rating': 4.5, 'brand': 'Tresemme'},
            {'name': 'Mamaearth Onion Hair Oil', 'price': 499, 'hair_type': 'Hair Fall', 'target_condition': 'Hair Fall', 'description': 'Reduces hair fall and promotes growth', 'rating': 4.3, 'brand': 'Mamaearth'},
            {'name': 'Mamaearth Rice Water Shampoo', 'price': 399, 'hair_type': 'Damaged', 'target_condition': 'Damaged & Frizzy', 'description': 'Damage repair with keratin', 'rating': 4.4, 'brand': 'Mamaearth'},
            {'name': 'The Body Shop Ginger Scalp Care', 'price': 799, 'hair_type': 'Dry Scalp', 'target_condition': 'Dandruff', 'description': 'Stimulates circulation and soothes scalp', 'rating': 4.5, 'brand': 'Body_Shop'},
            {'name': 'The Body Shop Banana True Moisture', 'price': 699, 'hair_type': 'Dry', 'target_condition': 'Damaged & Frizzy', 'description': 'Hydrating mask for dry hair', 'rating': 4.6, 'brand': 'Body_Shop'},
            {'name': 'Garnier Fructis Grow Strong Shampoo', 'price': 349, 'hair_type': 'Weak', 'target_condition': 'Hair Fall', 'description': 'Strengthens fiber from root to tip', 'rating': 4.4, 'brand': 'Garnier'},
            {'name': 'Garnier Fructis Hair Food Papaya', 'price': 549, 'hair_type': 'Damaged', 'target_condition': 'Damaged & Frizzy', 'description': 'Repairing mask for damaged hair', 'rating': 4.5, 'brand': 'Garnier'},
            {'name': 'Dabur Vatika Enriched Coconut Hair Oil', 'price': 199, 'hair_type': 'All', 'target_condition': 'Damaged & Frizzy', 'description': 'Volume & thickness builder', 'rating': 4.2, 'brand': 'Dabur'},
            {'name': 'Sunsilk Perfect Straight Conditioner', 'price': 319, 'hair_type': 'Frizzy', 'target_condition': 'Damaged & Frizzy', 'description': 'Anti-frizz straight look', 'rating': 4.3, 'brand': 'Sunsilk'},
            {'name': 'Biotique Bio Bhringraj Therapeutic Oil', 'price': 299, 'hair_type': 'Hair Fall', 'target_condition': 'Hair Fall', 'description': 'Herbal oil for growth', 'rating': 4.1, 'brand': 'Biotique'},
            {'name': 'Nykaa Naturals Rosemary Oil', 'price': 350, 'hair_type': 'Hair Fall', 'target_condition': 'Hair Fall', 'description': 'Essential oil for hair density', 'rating': 4.7, 'brand': 'Nykaa'},
            {'name': 'Love Beauty and Planet Coconut Water', 'price': 349, 'hair_type': 'Dry', 'target_condition': 'Oily Scalp', 'description': 'Hydration without weigh-down', 'rating': 4.2, 'brand': 'Love_Beauty_Planet'},
            {'name': 'Forest Essentials Hair Cleanser Bhringraj', 'price': 1299, 'hair_type': 'Damaged', 'target_condition': 'Damaged & Frizzy', 'description': 'Ayurvedic sulphate-free cleanser', 'rating': 4.5, 'brand': 'Forest_Essentials'},
            {'name': 'Khadi Natural Amla & Reetha Shampoo', 'price': 299, 'hair_type': 'Oily Scalp', 'target_condition': 'Oily Scalp', 'description': 'Herbal deep clean formula', 'rating': 4.1, 'brand': 'Khadi'},
            {'name': 'Moroccanoil Treatment Original', 'price': 3500, 'hair_type': 'All', 'target_condition': 'Damaged & Frizzy', 'description': 'Argan oil infused treatment', 'rating': 4.8, 'brand': 'Moroccanoil'},
            {'name': 'Olaplex No. 7 Bonding Oil', 'price': 2900, 'hair_type': 'Damaged', 'target_condition': 'Damaged & Frizzy', 'description': 'Reparative styling oil', 'rating': 4.9, 'brand': 'Olaplex'},
            {'name': 'Kerastase Resistance Bain Force Architecte', 'price': 2400, 'hair_type': 'Damaged', 'target_condition': 'Damaged & Frizzy', 'description': 'Reconstructing shampoo for brittle hair', 'rating': 4.7, 'brand': 'Kerastase'},
            {'name': 'Dove Intense Repair Shampoo', 'price': 399, 'hair_type': 'Damaged', 'target_condition': 'Damaged & Frizzy', 'description': 'Nourishes to repair damage', 'rating': 4.4, 'brand': 'Dove'},
            {'name': 'Wella Professionals Invigo Nutri-Enrich', 'price': 700, 'hair_type': 'Dry', 'target_condition': 'Damaged & Frizzy', 'description': 'Deep nourishing conditioner', 'rating': 4.5, 'brand': 'Wella'},
            {'name': 'Schwarzkopf Professional BC Bonacure', 'price': 900, 'hair_type': 'Damaged', 'target_condition': 'Damaged & Frizzy', 'description': 'Peptide repair rescue spray', 'rating': 4.6, 'brand': 'Schwarzkopf'},
            {'name': 'BBlunt Intense Moisture Hair Serum', 'price': 599, 'hair_type': 'Frizzy', 'target_condition': 'Damaged & Frizzy', 'description': 'Moisture serum with avocado oil', 'rating': 4.3, 'brand': 'BBlunt'},
            {'name': 'Matrix Biolage Smoothproof Shampoo', 'price': 450, 'hair_type': 'Frizzy', 'target_condition': 'Damaged & Frizzy', 'description': 'Camellia serum infused for frizz control', 'rating': 4.4, 'brand': 'Matrix'},
            {'name': 'Aveda Invati Advanced Scalp Revitalizer', 'price': 4500, 'hair_type': 'Thinning', 'target_condition': 'Hair Fall', 'description': 'Reduces hair loss', 'rating': 4.7, 'brand': 'Aveda'},
        ]
        
        
        # Helper to generate real images using Bing Search API hack
        def fetch_real_image(name):
            import requests, re, os, time
            
            # Simple file cache to prevent re-downloading if script is run multiple times
            cache_dir = os.path.join(app.root_path, 'static', 'images', 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            cache_file = os.path.join(cache_dir, f"{safe_name.replace(' ', '_')}.txt")
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return f.read().strip()
            
            print(f"  -> Fetching real image for: {name} ...", end="", flush=True)
            url = f"https://www.bing.com/images/search?q={requests.utils.quote(name + ' product bottle white background')}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            
            try:
                response = requests.get(url, headers=headers, timeout=5)
                matches = re.findall(r'murl&quot;:&quot;(.*?)&quot;', response.text)
                if matches:
                    img_url = matches[0]
                    # save to cache
                    with open(cache_file, 'w') as f:
                        f.write(img_url)
                    print(f" OK")
                    time.sleep(0.5) # respect rate limit
                    return img_url
            except Exception as e:
                pass
            
            print(f" Failed (Using fallback)")
            return f"https://via.placeholder.com/400x400/FFE4ED/90EE90?text={requests.utils.quote(name)}"
            
        # EXTRA BRANDED PRODUCTS
        extra_skincare = [
            {'name': 'The Face Shop Rice Water Bright Cleansing Foam', 'price': 850, 'skin_type': 'All', 'target_condition': 'Dullness', 'description': 'Brightening deep foaming cleanser', 'rating': 4.7, 'brand': 'The_Face_Shop'},
            {'name': 'Dot & Key Vitamin C + E Super Bright Moisturizer', 'price': 595, 'skin_type': 'All', 'target_condition': 'Dullness', 'description': 'Lightweight glowing moisturizer', 'rating': 4.5, 'brand': 'Dot_and_Key'},
            {'name': 'Nykaa SkinRX 10% Vitamin C Serum', 'price': 699, 'skin_type': 'All', 'target_condition': 'Dullness', 'description': 'Illuminating serum for glowing skin', 'rating': 4.4, 'brand': 'Nykaa'},
            {'name': 'Loreal Paris Revitalift Hyaluronic Acid Serum', 'price': 999, 'skin_type': 'Dry', 'target_condition': 'Dry & Sensitive', 'description': 'Plumping hydration serum', 'rating': 4.8, 'brand': 'Loreal'},
            {'name': 'Estee Lauder Advanced Night Repair', 'price': 8900, 'skin_type': 'Mature', 'target_condition': 'Aging', 'description': 'Premium synchronized multi-recovery complex', 'rating': 4.9, 'brand': 'Estee_Lauder'},
            {'name': 'M.A.C Prep + Prime Fix+', 'price': 2200, 'skin_type': 'All', 'target_condition': 'Combination', 'description': 'Hydrating setting spray', 'rating': 4.8, 'brand': 'MAC'},
            {'name': 'Kama Ayurveda Pure Rose Water', 'price': 1350, 'skin_type': 'Sensitive', 'target_condition': 'Dry & Sensitive', 'description': '100% pure steam distilled rose water', 'rating': 4.6, 'brand': 'Kama_Ayurveda'},
            {'name': 'Simple Kind To Skin Micellar Cleansing Water', 'price': 450, 'skin_type': 'Sensitive', 'target_condition': 'Dry & Sensitive', 'description': 'Gentle makeup remover', 'rating': 4.7, 'brand': 'Simple'},
            {'name': 'DermaCo 1% Hyaluronic Sunscreen Aqua Gel', 'price': 499, 'skin_type': 'All', 'target_condition': 'Combination', 'description': 'Broad spectrum SPF 50 sunscreen', 'rating': 4.6, 'brand': 'Derma_Co'},
            {'name': 'Aqualogica Glow+ Dewy Sunscreen', 'price': 399, 'skin_type': 'All', 'target_condition': 'Dullness', 'description': 'Vitamin C & Papaya extracts sunscreen', 'rating': 4.5, 'brand': 'Aqualogica'},
        ]
        
        extra_haircare = [
            {'name': 'Anomaly Clarifying Shampoo', 'price': 750, 'hair_type': 'Oily Scalp', 'target_condition': 'Oily Scalp', 'description': 'Eucalyptus & Rosemary deep clean', 'rating': 4.4, 'brand': 'Anomaly'},
            {'name': 'Pilgrim Spanish Rosemary & Biotin Hair Growth Oil', 'price': 450, 'hair_type': 'Thinning', 'target_condition': 'Hair Fall', 'description': 'Stimulates roots and increases density', 'rating': 4.6, 'brand': 'Pilgrim'},
            {'name': 'Traya Scalp Oil', 'price': 500, 'hair_type': 'Hair Fall', 'target_condition': 'Hair Fall', 'description': 'Ayurvedic root strengthening oil', 'rating': 4.5, 'brand': 'Traya'},
            {'name': 'Plum Avocado Nourish Up Hair Mask', 'price': 675, 'hair_type': 'Frizzy', 'target_condition': 'Damaged & Frizzy', 'description': 'Argan & Avocado deep conditioning', 'rating': 4.7, 'brand': 'Plum'},
            {'name': 'Anomalous Hair Bonding Serum', 'price': 850, 'hair_type': 'Damaged', 'target_condition': 'Damaged & Frizzy', 'description': 'Restores broken bonds', 'rating': 4.8, 'brand': 'Anomaly'},
            {'name': 'Yves Rocher Anti-Pollution Rinsing Vinegar', 'price': 950, 'hair_type': 'All', 'target_condition': 'Oily Scalp', 'description': 'Scalp detox & shiny hair rinse', 'rating': 4.6, 'brand': 'Yves_Rocher'},
            {'name': 'Bare Anatomy Anti-Frizz Leave-In Serum', 'price': 549, 'hair_type': 'Frizzy', 'target_condition': 'Damaged & Frizzy', 'description': 'Moisture lock formula', 'rating': 4.5, 'brand': 'Bare_Anatomy'},
            {'name': 'Streax Professional Vitariche Gloss Hair Serum', 'price': 250, 'hair_type': 'All', 'target_condition': 'Damaged & Frizzy', 'description': 'Macadamia oil & Vitamin E serum', 'rating': 4.4, 'brand': 'Streax'},
            {'name': 'Sebamed Anti-Dandruff Shampoo', 'price': 650, 'hair_type': 'Dandruff', 'target_condition': 'Dandruff', 'description': 'pH 5.5 medicated dandruff relief', 'rating': 4.8, 'brand': 'Sebamed'},
            {'name': 'Minimalist 18% Hair Growth Actives', 'price': 799, 'hair_type': 'Hair Fall', 'target_condition': 'Hair Fall', 'description': 'Redensyl + Procapil peptide serum', 'rating': 4.7, 'brand': 'Minimalist'},
        ]
        
        skincare_specs.extend(extra_skincare)
        haircare_specs.extend(extra_haircare)
        
        all_products = []
        for p_list, category in [(skincare_specs, 'skin'), (haircare_specs, 'hair')]:
            for spec in p_list:
                imgfile = fetch_real_image(spec['name'])
                prod = Product(
                    name=spec['name'],
                    category=category,
                    price=spec['price'],
                    skin_type=spec.get('skin_type'),
                    hair_type=spec.get('hair_type'),
                    target_condition=spec['target_condition'],
                    description=spec['description'],
                    rating=spec['rating'],
                    image_url=imgfile,
                    stock_count=100
                )
                all_products.append(prod)
                
        for product in all_products:
            db.session.add(product)
            
        db.session.commit()
        print(f"\n✓ Successfully seeded {len(all_products)} products")
        print("✓ Database reset and 60-product seeding complete!")

if __name__ == '__main__':
    seed_large_dataset()
