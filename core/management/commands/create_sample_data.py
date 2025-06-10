from django.core.management.base import BaseCommand
from decimal import Decimal
from core.models import (
    User, Category, Tag, Occasion, SubscriptionPlan,
    Wishlist, WishlistItem
)


class Command(BaseCommand):
    help = 'Create sample data for the wishlist platform'

    def handle(self, *args, **options):
        self.stdout.write("Creating sample data...")

        # Create Categories
        categories_data = [
            {'name': 'الکترونیک', 'name_en': 'Electronics',
                'icon': '📱', 'color': '#3b82f6'},
            {'name': 'کتاب', 'name_en': 'Books', 'icon': '📚', 'color': '#10b981'},
            {'name': 'لباس و پوشاک', 'name_en': 'Clothing',
                'icon': '👕', 'color': '#f59e0b'},
            {'name': 'خانه و آشپزخانه', 'name_en': 'Home & Kitchen',
                'icon': '🏠', 'color': '#8b5cf6'},
            {'name': 'ورزش', 'name_en': 'Sports', 'icon': '⚽', 'color': '#ef4444'},
            {'name': 'زیبایی', 'name_en': 'Beauty',
                'icon': '💄', 'color': '#ec4899'},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f"Created category: {category.name}")

        # Create Tags
        tags_data = [
            {'name': 'گران‌قیمت', 'color': '#dc2626'},
            {'name': 'پرطرفدار', 'color': '#059669'},
            {'name': 'جدید', 'color': '#2563eb'},
            {'name': 'ضروری', 'color': '#7c3aed'},
            {'name': 'هدیه', 'color': '#db2777'},
            {'name': 'تخفیف‌دار', 'color': '#ea580c'},
        ]

        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_data['name'],
                defaults=tag_data
            )
            if created:
                self.stdout.write(f"Created tag: {tag.name}")

        # Create Occasions
        occasions_data = [
            {'name': 'تولد', 'icon': '🎂', 'color': '#f59e0b', 'is_recurring': True},
            {'name': 'سالگرد ازدواج', 'icon': '💑',
                'color': '#ec4899', 'is_recurring': True},
            {'name': 'فارغ‌التحصیلی', 'icon': '🎓',
                'color': '#3b82f6', 'is_recurring': False},
            {'name': 'عید نوروز', 'icon': '🌸',
                'color': '#10b981', 'is_recurring': True},
            {'name': 'روز مادر', 'icon': '🌹',
                'color': '#ec4899', 'is_recurring': True},
            {'name': 'کریسمس', 'icon': '🎄', 'color': '#059669', 'is_recurring': True},
        ]

        for occ_data in occasions_data:
            occasion, created = Occasion.objects.get_or_create(
                name=occ_data['name'],
                defaults=occ_data
            )
            if created:
                self.stdout.write(f"Created occasion: {occasion.name}")

        # Create Subscription Plans
        plans_data = [
            {
                'name': 'رایگان',
                'name_en': 'Free',
                'description': 'برای شروع کار مناسب است',
                'monthly_price': Decimal('0.00'),
                'yearly_price': Decimal('0.00'),
                'max_wishlists': 3,
                'max_items_per_wishlist': 20,
                'max_image_uploads': 50,
                'color': '#6b7280',
                'sort_order': 1,
            },
            {
                'name': 'پایه',
                'name_en': 'Basic',
                'description': 'برای استفاده شخصی مناسب است',
                'monthly_price': Decimal('99000.00'),
                'yearly_price': Decimal('990000.00'),
                'yearly_discount_percentage': 20,
                'max_wishlists': 10,
                'max_items_per_wishlist': 50,
                'max_image_uploads': 200,
                'color': '#3b82f6',
                'sort_order': 2,
            },
            {
                'name': 'پریمیوم',
                'name_en': 'Premium',
                'description': 'برای استفاده حرفه‌ای با تمام امکانات',
                'monthly_price': Decimal('199000.00'),
                'yearly_price': Decimal('1990000.00'),
                'yearly_discount_percentage': 25,
                'max_wishlists': 50,
                'max_items_per_wishlist': 200,
                'max_image_uploads': 1000,
                'can_use_custom_domains': True,
                'can_export_data': True,
                'priority_support': True,
                'advanced_analytics': True,
                'color': '#8b5cf6',
                'sort_order': 3,
                'is_popular': True,
            },
        ]

        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f"Created subscription plan: {plan.name}")

        # Create sample users
        self.stdout.write("Creating sample users...")
        sample_users = [
            {
                'username': 'sara_m',
                'email': 'sara@example.com',
                'first_name': 'سارا',
                'last_name': 'محمدی',
                'wallet_balance': Decimal('500000.00')
            },
            {
                'username': 'ali_k',
                'email': 'ali@example.com',
                'first_name': 'علی',
                'last_name': 'کریمی',
                'wallet_balance': Decimal('750000.00')
            },
        ]

        for user_data in sample_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(f"Created user: {user.username}")

        # Create sample wishlists
        self.stdout.write("Creating sample wishlists...")
        admin_user = User.objects.get(username='admin')
        sara_user = User.objects.get(username='sara_m')

        birthday_occasion = Occasion.objects.get(name='تولد')
        electronics_cat = Category.objects.get(name='الکترونیک')
        book_cat = Category.objects.get(name='کتاب')

        expensive_tag = Tag.objects.get(name='گران‌قیمت')
        popular_tag = Tag.objects.get(name='پرطرفدار')

        # Admin's birthday wishlist
        admin_wishlist, created = Wishlist.objects.get_or_create(
            title='لیست تولد من',
            owner=admin_user,
            defaults={
                'description': 'چیزهایی که برای تولدم می‌خواهم',
                'occasion': birthday_occasion,
                'visibility': 'PUBLIC',
                'theme_color': '#f59e0b'
            }
        )

        if created:
            self.stdout.write(f"Created wishlist: {admin_wishlist.title}")

            # Add items to admin's wishlist
            items_data = [
                {
                    'name': 'آیفون 15 Pro',
                    'description': 'گوشی آیفون مدل جدید با ظرفیت 256 گیگابایت',
                    'price': Decimal('45000000.00'),
                    'category': electronics_cat,
                    'priority': 5,
                    'product_url': 'https://apple.com'
                },
                {
                    'name': 'کتاب "هری پاتر مجموعه کامل"',
                    'description': 'مجموعه کامل کتاب‌های هری پاتر به فارسی',
                    'price': Decimal('850000.00'),
                    'category': book_cat,
                    'priority': 3,
                },
                {
                    'name': 'هدفون AirPods Pro',
                    'description': 'هدفون بی‌سیم اپل با قابلیت حذف نویز',
                    'price': Decimal('8500000.00'),
                    'category': electronics_cat,
                    'priority': 4,
                }
            ]

            for item_data in items_data:
                item = WishlistItem.objects.create(
                    wishlist=admin_wishlist,
                    **item_data
                )

                # Add tags
                if item_data['price'] > Decimal('5000000.00'):
                    item.tags.add(expensive_tag)
                item.tags.add(popular_tag)

                self.stdout.write(f"Created item: {item.name}")

        # Sara's wishlist
        sara_wishlist, created = Wishlist.objects.get_or_create(
            title='لیست آرزوهای من',
            owner=sara_user,
            defaults={
                'description': 'چیزهایی که دوست دارم داشته باشم',
                'visibility': 'PUBLIC',
                'allow_contributions': True,
                'theme_color': '#ec4899'
            }
        )

        if created:
            self.stdout.write(f"Created wishlist: {sara_wishlist.title}")

        self.stdout.write(self.style.SUCCESS(
            '\n✅ Sample data created successfully!'))
        self.stdout.write('\n🔗 Admin Login:')
        self.stdout.write('Username: admin')
        self.stdout.write('Password: admin123')
        self.stdout.write('\n🔗 Test Users:')
        self.stdout.write('Username: sara_m, Password: testpass123')
        self.stdout.write('Username: ali_k, Password: testpass123')
        self.stdout.write('\n🌐 URLs:')
        self.stdout.write('Admin Panel: http://localhost:8000/admin/')
        self.stdout.write('API Docs: http://localhost:8000/api/docs/')
        self.stdout.write('API Base: http://localhost:8000/api/')
