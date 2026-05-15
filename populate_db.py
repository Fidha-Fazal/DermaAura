from app import create_app, db
from models import Product
import random

app = create_app()

BRANDS = ['Lumina', 'DermaCo', 'Minimalist', 'Essence', 'Aura', 'GlowDr', 'VitaSkin', 'PureLocks', 'Silk & Shine', 'Botanica']
SKIN_TYPES = ['Oily', 'Dry', 'Combination', 'Normal', 'Acne-Prone', 'Sensitive']
HAIR_TYPES = ['Curly', 'Straight', 'Wavy', 'Thinning', 'Dry', 'Color-Treated']
SKIN_CONDITIONS = ['Acne', 'Aging', 'Hyperpigmentation', 'Redness', 'Dullness', 'Uneven Texture']
HAIR_CONDITIONS = ['Frizz', 'Dandruff', 'Hair Fall', 'Split Ends', 'Scalp Care']

SKIN_PRODUCTS = [
    ("Hydrating Cleanser", "A gentle cleanser that removes impurities without stripping moisture."),
    ("Vitamin C Serum", "Brightens the skin and reduces dark spots effectively."),
    ("Niacinamide 10%", "Refines pores and balances sebum production for a flawless look."),
    ("Lightweight Moisturizer", "Locks in hydration with a non-greasy, refreshing finish."),
    ("Broad Spectrum SPF 50", "Provides robust protection against UVA and UVB rays."),
    ("Exfoliating AHA/BHA Peel", "Gently removes dead skin cells revealing a glowing complexion."),
    ("Overnight Repair Mask", "Intensely nourishes and repairs the skin barrier while you sleep."),
    ("Hyaluronic Acid Serum", "Plumps the skin and delivers deep, lasting hydration."),
    ("Retinol Night Cream", "Targets fine lines and promotes collagen generation overnight."),
    ("Soothing Aloe Gel", "Calms irritated skin and provides immediate cooling relief.")
]

HAIR_PRODUCTS = [
    ("Nourishing Shampoo", "Cleanses hair gently while infusing essential nutrients."),
    ("Deep Conditioning Mask", "Restores moisture and repairs dry, damaged hair."),
    ("Argan Oil Hair Serum", "Tames frizz and adds a brilliant, healthy shine."),
    ("Volumizing Mousse", "Provides lift and body to flat, lifeless hair."),
    ("Scalp Detox Scrub", "Removes buildup and promotes a healthy scalp environment."),
    ("Leave-In Conditioner", "Detangles and protects hair from heat and environmental damage."),
    ("Color Protect Shampoo", "Preserves hair color vibrancy and prevents fading."),
    ("Keratin Smooth Treatment", "Smooths the hair cuticle for a sleek, polished look."),
    ("Biotin Hair Growth Tonic", "Stimulates follicles and encourages thicker hair growth."),
    ("Anti-Dandruff Lotion", "Soothes the scalp and eliminates flakes effectively.")
]

IMAGES = [
    "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1599305090598-fe179d501227?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1615397323136-2bad9a103fe0?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1556228578-8d89b6acd8d3?auto=format&fit=crop&w=400&q=80"
]

def populate():
    with app.app_context():
        # Clear existing products to ensure a clean slate
        db.session.query(Product).delete()

        products = []
        
        # Generate 40 skin products
        for i in range(40):
            kind = random.choice(SKIN_PRODUCTS)
            name = f"{random.choice(BRANDS)} {kind[0]} {i}"
            p = Product(
                name=name,
                category='skin',
                price=round(random.uniform(299.0, 1999.0), 2),
                skin_type=random.choice(SKIN_TYPES),
                image_url=random.choice(IMAGES),
                description=kind[1],
                rating=round(random.uniform(3.5, 5.0), 1),
                stock_count=random.randint(0, 150),
                target_condition=random.choice(SKIN_CONDITIONS)
            )
            products.append(p)
            
        # Generate 20 hair products
        for i in range(20):
            kind = random.choice(HAIR_PRODUCTS)
            name = f"{random.choice(BRANDS)} {kind[0]} {i}"
            p = Product(
                name=name,
                category='hair',
                price=round(random.uniform(199.0, 1499.0), 2),
                hair_type=random.choice(HAIR_TYPES),
                image_url=random.choice(IMAGES),
                description=kind[1],
                rating=round(random.uniform(3.5, 5.0), 1),
                stock_count=random.randint(0, 150),
                target_condition=random.choice(HAIR_CONDITIONS)
            )
            products.append(p)
            
        db.session.bulk_save_objects(products)
        db.session.commit()
        print(f"Successfully added {len(products)} products to the database.")

if __name__ == '__main__':
    populate()
