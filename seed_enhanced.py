from app import create_app, db
from models import User, Product

def seed_database():
    """Seed database with admin user and 20+ products with proper categories"""
    app = create_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if admin exists
        admin = User.query.filter_by(email='admin@test.com').first()
        if not admin:
            admin = User(
                email='admin@test.com',
                username='Admin User',
                phone='9876543210',
                role='admin'
            )
            admin.set_password('testpass123')
            db.session.add(admin)
            print("✓ Admin user created: admin@test.com / testpass123")
        
        # Check if products already exist
        existing = Product.query.count()
        if existing > 0:
            print(f"✓ Database already has {existing} products. Skipping product seed.")
            db.session.commit()
            return
        
        # SKINCARE PRODUCTS
        skincare = [
            Product(
                name='Hydrating Facial Moisturizer',
                category='skin',
                price=599,
                skin_type='All Skin Types',
                description='Deep hydrating cream with hyaluronic acid for smooth, glowing skin',
                rating=4.5,
                image_url='placeholder_hydrating.png'
            ),
            Product(
                name='Vitamin C Brightening Serum',
                category='skin',
                price=899,
                skin_type='Dull & Dark Skin',
                description='Pure vitamin C serum for radiant, brightened complexion',
                rating=4.7,
                image_url='placeholder_vitamin_c.png'
            ),
            Product(
                name='Neem & Tulsi Acne Face Wash',
                category='skin',
                price=299,
                skin_type='Oily & Acne Prone',
                description='Powerful anti-bacterial face wash for clear, oil-free skin',
                rating=4.6,
                image_url='placeholder_neem.png'
            ),
            Product(
                name='Rose Hip Oil Night Serum',
                category='skin',
                price=1299,
                skin_type='Dry & Sensitive',
                description='Premium rose hip oil for intense overnight nourishment',
                rating=4.8,
                image_url='placeholder_rose_hip.png'
            ),
            Product(
                name='Retinol Anti-Aging Cream',
                category='skin',
                price=1599,
                skin_type='Mature & Fine Lines',
                description='Advanced retinol formula to reduce wrinkles and fine lines',
                rating=4.7,
                image_url='placeholder_retinol.png'
            ),
            Product(
                name='Clay Detox Face Mask',
                category='skin',
                price=499,
                skin_type='Oily & Combination',
                description='Deep pore cleansing clay mask for detoxified skin',
                rating=4.5,
                image_url='placeholder_clay.png'
            ),
            Product(
                name='Hyaluronic Acid Serumless Hydrator',
                category='skin',
                price=749,
                skin_type='All Skin Types',
                description='Lightweight hydration without serum consistency',
                rating=4.6,
                image_url='placeholder_hyaluronic.png'
            ),
            Product(
                name='Silicone-Free Priming Lotion',
                category='skin',
                price=599,
                skin_type='Sensitive Skin',
                description='Gentle priming lotion for makeup base without silicones',
                rating=4.4,
                image_url='placeholder_primer.png'
            ),
            Product(
                name='Potent Eye Cream',
                category='skin',
                price=899,
                skin_type='All Skin Types',
                description='Targeted eye cream to reduce dark circles and puffiness',
                rating=4.5,
                image_url='placeholder_eye_cream.png'
            ),
            Product(
                name='Glycolic Acid Exfoliating Toner',
                category='skin',
                price=649,
                skin_type='Dull & Textured',
                description='Chemical exfoliant for smooth, refined skin texture',
                rating=4.7,
                image_url='placeholder_glycolic.png'
            ),
        ]
        
        # HAIRCARE PRODUCTS
        haircare = [
            Product(
                name='Anti-Dandruff Shampoo',
                category='hair',
                price=349,
                hair_type='Dandruff & Flaky',
                description='Medicated shampoo with zinc pyrithione to eliminate dandruff',
                rating=4.6,
                image_url='placeholder_anti_dandruff.png'
            ),
            Product(
                name='Volumizing Conditioner',
                category='hair',
                price=399,
                hair_type='Thin & Fine Hair',
                description='Lightweight conditioning formula for voluminous, bouncy hair',
                rating=4.5,
                image_url='placeholder_volume.png'
            ),
            Product(
                name='Hair Growth Oil',
                category='hair',
                price=599,
                hair_type='Hair Loss & Weak',
                description='Ayurvedic oil blend with herbs to promote hair growth',
                rating=4.7,
                image_url='placeholder_growth_oil.png'
            ),
            Product(
                name='Deep Moisture Hair Mask',
                category='hair',
                price=499,
                hair_type='Dry & Damaged',
                description='Intensive conditioning mask for frizz-free, shiny hair',
                rating=4.8,
                image_url='placeholder_hair_mask.png'
            ),
            Product(
                name='Protein-Rich Hair Serum',
                category='hair',
                price=449,
                hair_type='Damaged & Frizzy',
                description='Silky serum with keratin for smooth, sleek finish',
                rating=4.6,
                image_url='placeholder_protein_serum.png'
            ),
            Product(
                name='Color Protection Shampoo',
                category='hair',
                price=429,
                hair_type='Colored Hair',
                description='pH-balanced shampoo to maintain color vibrancy',
                rating=4.5,
                image_url='placeholder_color_protect.png'
            ),
            Product(
                name='Scalp Treatment Lotion',
                category='hair',
                price=549,
                hair_type='Oily Scalp',
                description='Balancing lotion to control scalp oiliness and itching',
                rating=4.4,
                image_url='placeholder_scalp.png'
            ),
            Product(
                name='Heat Protection Spray',
                category='hair',
                price=329,
                hair_type='All Hair Types',
                description='Lightweight spray shield against heat styling damage',
                rating=4.5,
                image_url='placeholder_heat_protect.png'
            ),
            Product(
                name='Strengthening Hair Oil',
                category='hair',
                price=579,
                hair_type='Weak & Brittle',
                description='Premium oil with biotin and vitamin E for strong hair',
                rating=4.7,
                image_url='placeholder_strength_oil.png'
            ),
            Product(
                name='Intensive Repair Conditioner',
                category='hair',
                price=479,
                hair_type='Very Damaged Hair',
                description='Professional repair conditioner with peptides',
                rating=4.6,
                image_url='placeholder_repair.png'
            ),
        ]
        
        # ADD ALL PRODUCTS
        all_products = skincare + haircare
        
        for product in all_products:
            db.session.add(product)
        
        db.session.commit()
        print(f"✓ Successfully seeded {len(all_products)} products (Skincare: {len(skincare)}, Haircare: {len(haircare)})")
        print("\nSeeding complete!")

if __name__ == '__main__':
    seed_database()
