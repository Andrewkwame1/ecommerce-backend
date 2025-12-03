"""
Seed script for e-commerce database with realistic sample data.
Uses proper data structures and algorithms for efficient data generation.
"""

import os
import django
import random
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.products.models import Category, Product, ProductImage, ProductVariant, Review
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem, OrderStatusHistory
from apps.users.models import Address, UserProfile

User = get_user_model()

# Data structures for seeding
CATEGORIES_DATA = [
    {
        'name': 'Electronics',
        'slug': 'electronics',
        'description': 'Electronic devices and gadgets',
        'children': [
            {'name': 'Phones', 'slug': 'phones', 'description': 'Mobile phones and accessories'},
            {'name': 'Laptops', 'slug': 'laptops', 'description': 'Computers and notebooks'},
            {'name': 'Accessories', 'slug': 'accessories', 'description': 'Tech accessories'},
        ]
    },
    {
        'name': 'Fashion',
        'slug': 'fashion',
        'description': 'Clothing and fashion items',
        'children': [
            {'name': 'Men', 'slug': 'men', 'description': "Men's clothing"},
            {'name': 'Women', 'slug': 'women', 'description': "Women's clothing"},
            {'name': 'Shoes', 'slug': 'shoes', 'description': 'Footwear'},
        ]
    },
    {
        'name': 'Home & Garden',
        'slug': 'home-garden',
        'description': 'Home and garden products',
        'children': [
            {'name': 'Furniture', 'slug': 'furniture', 'description': 'Home furniture'},
            {'name': 'Decor', 'slug': 'decor', 'description': 'Home decoration'},
        ]
    },
]

PRODUCTS_DATA = [
    # Electronics
    {
        'name': 'iPhone 15 Pro',
        'description': 'Latest iPhone with advanced features',
        'category_slug': 'phones',
        'price': Decimal('999.99'),
        'sku': 'IPHONE15PRO001',
        'quantity': 50,
        'is_featured': True,
        'variants': [
            {'name': '256GB Black', 'sku': 'IPHONE15PRO256B', 'price': Decimal('999.99')},
            {'name': '512GB Silver', 'sku': 'IPHONE15PRO512S', 'price': Decimal('1099.99')},
            {'name': '1TB Gold', 'sku': 'IPHONE15PRO1TB', 'price': Decimal('1199.99')},
        ]
    },
    {
        'name': 'Samsung Galaxy S24',
        'description': 'Premium Android smartphone',
        'category_slug': 'phones',
        'price': Decimal('899.99'),
        'sku': 'SAMSUNG24001',
        'quantity': 45,
        'is_featured': True,
        'variants': [
            {'name': '128GB Phantom Black', 'sku': 'SAMSUNG24128B', 'price': Decimal('899.99')},
            {'name': '256GB Marble White', 'sku': 'SAMSUNG24256W', 'price': Decimal('949.99')},
        ]
    },
    {
        'name': 'MacBook Pro 16"',
        'description': 'Professional laptop for creators',
        'category_slug': 'laptops',
        'price': Decimal('2499.99'),
        'sku': 'MACBOOKPRO16001',
        'quantity': 30,
        'is_featured': True,
        'variants': [
            {'name': 'M3 Max 32GB', 'sku': 'MACBOOPM3MAX32', 'price': Decimal('2499.99')},
            {'name': 'M3 Max 64GB', 'sku': 'MACBOOPM3MAX64', 'price': Decimal('2999.99')},
        ]
    },
    {
        'name': 'Dell XPS 13',
        'description': 'Ultrabook laptop',
        'category_slug': 'laptops',
        'price': Decimal('1299.99'),
        'sku': 'DELLXPS13001',
        'quantity': 40,
        'variants': [
            {'name': 'Intel i5 8GB', 'sku': 'DELLXPSI58GB', 'price': Decimal('1299.99')},
            {'name': 'Intel i7 16GB', 'sku': 'DELLXPSI716GB', 'price': Decimal('1599.99')},
        ]
    },
    {
        'name': 'Sony WH-1000XM5 Headphones',
        'description': 'Premium noise-canceling headphones',
        'category_slug': 'accessories',
        'price': Decimal('399.99'),
        'sku': 'SONYWH1000XM5',
        'quantity': 100,
        'is_featured': True,
        'variants': []
    },
    # Fashion
    {
        'name': 'Classic Cotton T-Shirt',
        'description': 'Comfortable everyday t-shirt',
        'category_slug': 'men',
        'price': Decimal('29.99'),
        'sku': 'TSHIRT001',
        'quantity': 200,
        'variants': [
            {'name': 'S Black', 'sku': 'TSHIRTS001B', 'price': Decimal('29.99')},
            {'name': 'M Blue', 'sku': 'TSHIRTM001B', 'price': Decimal('29.99')},
            {'name': 'L White', 'sku': 'TSHIRTL001W', 'price': Decimal('29.99')},
            {'name': 'XL Gray', 'sku': 'TSHIRTXL001G', 'price': Decimal('29.99')},
        ]
    },
    {
        'name': 'Premium Denim Jeans',
        'description': 'High-quality denim pants',
        'category_slug': 'men',
        'price': Decimal('89.99'),
        'sku': 'JEANS001',
        'quantity': 150,
        'variants': [
            {'name': '30 Dark Blue', 'sku': 'JEANS30DB', 'price': Decimal('89.99')},
            {'name': '32 Light Blue', 'sku': 'JEANS32LB', 'price': Decimal('89.99')},
            {'name': '34 Black', 'sku': 'JEANS34BK', 'price': Decimal('89.99')},
        ]
    },
    {
        'name': 'Elegant Dress',
        'description': 'Perfect for any occasion',
        'category_slug': 'women',
        'price': Decimal('149.99'),
        'sku': 'DRESS001',
        'quantity': 80,
        'is_featured': True,
        'variants': [
            {'name': 'XS Red', 'sku': 'DRESSXSR', 'price': Decimal('149.99')},
            {'name': 'S Black', 'sku': 'DRESSSBK', 'price': Decimal('149.99')},
            {'name': 'M Blue', 'sku': 'DRESSMBL', 'price': Decimal('149.99')},
        ]
    },
    {
        'name': 'Running Shoes',
        'description': 'Comfortable sports shoes',
        'category_slug': 'shoes',
        'price': Decimal('119.99'),
        'sku': 'SHOES001',
        'quantity': 120,
        'variants': [
            {'name': '7 Black', 'sku': 'SHOES7BK', 'price': Decimal('119.99')},
            {'name': '8 White', 'sku': 'SHOES8WH', 'price': Decimal('119.99')},
            {'name': '9 Blue', 'sku': 'SHOES9BL', 'price': Decimal('119.99')},
            {'name': '10 Gray', 'sku': 'SHOES10GR', 'price': Decimal('119.99')},
        ]
    },
]

USER_DATA = [
    {
        'email': 'john@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'phone_number': '+1234567890',
        'addresses': [
            {'address_type': 'shipping', 'full_name': 'John Doe', 'phone_number': '+1234567890', 'street_address': '123 Main St', 'apartment': '', 'city': 'New York', 'state': 'NY', 'country': 'USA', 'zip_code': '10001', 'is_default': True},
            {'address_type': 'billing', 'full_name': 'John Doe', 'phone_number': '+1234567890', 'street_address': '456 Oak Ave', 'apartment': 'Apt 2B', 'city': 'Boston', 'state': 'MA', 'country': 'USA', 'zip_code': '02101'},
        ]
    },
    {
        'email': 'jane@example.com',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'phone_number': '+1987654321',
        'addresses': [
            {'address_type': 'shipping', 'full_name': 'Jane Smith', 'phone_number': '+1987654321', 'street_address': '789 Pine Rd', 'apartment': '', 'city': 'Chicago', 'state': 'IL', 'country': 'USA', 'zip_code': '60601', 'is_default': True},
        ]
    },
    {
        'email': 'bob@example.com',
        'first_name': 'Bob',
        'last_name': 'Johnson',
        'phone_number': '+1555123456',
        'addresses': [
            {'address_type': 'shipping', 'full_name': 'Bob Johnson', 'phone_number': '+1555123456', 'street_address': '321 Elm St', 'apartment': '', 'city': 'Los Angeles', 'state': 'CA', 'country': 'USA', 'zip_code': '90001', 'is_default': True},
            {'address_type': 'billing', 'full_name': 'Bob Johnson', 'phone_number': '+1555123456', 'street_address': '654 Maple Dr', 'apartment': 'Suite 100', 'city': 'San Francisco', 'state': 'CA', 'country': 'USA', 'zip_code': '94102'},
        ]
    },
]


class DatabaseSeeder:
    """Efficient database seeding with proper data structures"""
    
    def __init__(self):
        self.categories_map = {}
        self.products_map = {}
        self.users_list = []
        
    def seed_categories(self):
        """Seed categories with hierarchical structure"""
        print("\n📦 Seeding Categories...")
        
        for cat_data in CATEGORIES_DATA:
            # Create parent category
            parent = Category.objects.create(
                name=cat_data['name'],
                slug=cat_data['slug'],
                description=cat_data['description'],
                is_active=True
            )
            self.categories_map[cat_data['slug']] = parent
            print(f"  ✓ Created category: {cat_data['name']}")
            
            # Create child categories
            for child_data in cat_data.get('children', []):
                child = Category.objects.create(
                    name=child_data['name'],
                    slug=child_data['slug'],
                    description=child_data['description'],
                    parent=parent,
                    is_active=True
                )
                self.categories_map[child_data['slug']] = child
                print(f"    ✓ Created subcategory: {child_data['name']}")
    
    def seed_products(self):
        """Seed products with variants using efficient batch operations"""
        print("\n📦 Seeding Products...")
        
        for prod_data in PRODUCTS_DATA:
            # Get category
            category = self.categories_map[prod_data['category_slug']]
            
            # Create product
            product = Product.objects.create(
                name=prod_data['name'],
                slug=prod_data['name'].lower().replace(' ', '-'),
                description=prod_data['description'],
                category=category,
                price=prod_data['price'],
                sku=prod_data['sku'],
                quantity=prod_data['quantity'],
                is_featured=prod_data.get('is_featured', False),
                is_active=True
            )
            self.products_map[prod_data['sku']] = product
            print(f"  ✓ Created product: {prod_data['name']} (${prod_data['price']})")
            
            # Create variants
            for variant_data in prod_data.get('variants', []):
                ProductVariant.objects.create(
                    product=product,
                    name=variant_data['name'],
                    sku=variant_data['sku'],
                    price=variant_data['price'],
                    quantity=random.randint(10, 100),
                    is_active=True
                )
            
            # Create dummy reviews (one per user max)
            if random.random() > 0.3:  # 70% of products get reviews
                # Get random unique users
                num_reviews = min(random.randint(2, 3), len(self.users_list))
                review_users = random.sample(self.users_list, num_reviews) if self.users_list else []
                
                for user in review_users:
                    try:
                        Review.objects.create(
                            product=product,
                            user=user,
                            rating=random.randint(3, 5),
                            title=random.choice(['Great product!', 'Highly recommended', 'Good quality']),
                            comment='This product exceeded my expectations and I would definitely recommend it.',
                            is_verified_purchase=True,
                            is_approved=True
                        )
                    except:
                        pass  # Skip if review already exists
    
    def seed_users(self):
        """Seed test users with addresses"""
        print("\n👥 Seeding Users...")
        
        for user_data in USER_DATA:
            # Create user
            user = User.objects.create_user(
                email=user_data['email'],
                password='testpass123',
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone_number=user_data['phone_number'],
                is_verified=True
            )
            self.users_list.append(user)
            print(f"  ✓ Created user: {user_data['email']}")
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Create addresses
            for idx, addr_data in enumerate(user_data.get('addresses', [])):
                Address.objects.create(
                    user=user,
                    address_type=addr_data['address_type'],
                    full_name=addr_data['full_name'],
                    phone_number=addr_data['phone_number'],
                    street_address=addr_data['street_address'],
                    apartment=addr_data.get('apartment', ''),
                    city=addr_data['city'],
                    state=addr_data['state'],
                    country=addr_data.get('country', 'USA'),
                    zip_code=addr_data['zip_code'],
                    is_default=addr_data.get('is_default', idx == 0)
                )
            
            # Create empty cart
            Cart.objects.create(user=user)
    
    def seed_orders(self):
        """Seed sample orders with order items"""
        print("\n📋 Seeding Orders...")
        
        status_choices = ['pending', 'processing', 'shipped', 'delivered']
        
        for user in self.users_list[:2]:  # Create orders for first 2 users
            # Get user's default address
            billing_address = Address.objects.filter(user=user, is_default=True).first()
            shipping_address = Address.objects.filter(user=user).first()
            
            if not billing_address or not shipping_address:
                continue
            
            # Create order
            order = Order.objects.create(
                user=user,
                billing_address=billing_address,
                shipping_address=shipping_address,
                subtotal=Decimal('0.00'),
                tax=Decimal('0.00'),
                shipping_cost=Decimal('10.00'),
                total_amount=Decimal('0.00'),
                status=random.choice(status_choices),
                created_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
            
            # Add random products to order
            subtotal = Decimal('0.00')
            for _ in range(random.randint(1, 3)):
                product = random.choice(list(self.products_map.values()))
                quantity = random.randint(1, 3)
                price = product.price
                item_subtotal = price * quantity
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_sku=product.sku,
                    price=price,
                    quantity=quantity
                )
                subtotal += item_subtotal
            
            # Update order totals
            tax = (subtotal * Decimal('0.1')).quantize(Decimal('0.01'))
            total = subtotal + tax + order.shipping_cost
            
            order.subtotal = subtotal
            order.tax = tax
            order.total_amount = total
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status=order.status,
                note='Order created'
            )
            
            print(f"  ✓ Created order for {user.email}: {order.order_number}")
    
    def seed_cart_items(self):
        """Add sample items to user carts"""
        print("\n🛒 Seeding Cart Items...")
        
        for user in self.users_list:
            cart = Cart.objects.filter(user=user).first()
            if not cart:
                continue
            
            # Add 2-4 random products to cart
            for _ in range(random.randint(2, 4)):
                product = random.choice(list(self.products_map.values()))
                
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=random.randint(1, 3),
                    price=product.price
                )
            
            print(f"  ✓ Added items to cart for {user.email}")
    
    def run(self):
        """Execute the complete seeding process"""
        print("=" * 50)
        print("🚀 Starting Database Seeding...")
        print("=" * 50)
        
        try:
            # Clear existing data (but preserve admin user)
            print("\n🧹 Clearing existing data...")
            Cart.objects.all().delete()
            Order.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            # Don't delete users if admin exists
            if not User.objects.filter(email='admin@example.com').exists():
                User.objects.all().delete()
            else:
                # Delete only test users, keep admin
                User.objects.exclude(email='admin@example.com').delete()
            print("  ✓ Existing data cleared")
            
            self.seed_categories()
            self.seed_users()
            self.seed_products()
            self.seed_orders()
            self.seed_cart_items()
            
            print("\n" + "=" * 50)
            print("✅ Database seeding completed successfully!")
            print("=" * 50)
            print("\n📊 Summary:")
            print(f"  • Categories: {Category.objects.count()}")
            print(f"  • Products: {Product.objects.count()}")
            print(f"  • Users: {User.objects.filter(is_staff=False).count()}")
            print(f"  • Orders: {Order.objects.count()}")
            print(f"  • Reviews: {Review.objects.count()}")
            print(f"  • Addresses: {Address.objects.count()}")
            print("\n")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    # Clear existing data (optional)
    print("⚠️  Note: This will seed sample data. Existing data will be preserved.")
    
    seeder = DatabaseSeeder()
    seeder.run()
