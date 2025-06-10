#!/usr/bin/env python
from core.models import Category, Tag, Plan
import django
import os
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wishlist_project.settings')

django.setup()


def create_sample_data():
    # Create Categories
    tech, created = Category.objects.get_or_create(
        name='تکنولوژی',
        defaults={'description': 'گجت ها و تجهیزات فناوری'}
    )

    fashion, created = Category.objects.get_or_create(
        name='مد و پوشاک',
        defaults={'description': 'لباس و اکسسوری'}
    )

    books, created = Category.objects.get_or_create(
        name='کتاب',
        defaults={'description': 'کتاب های مختلف'}
    )

    # Create Tags
    expensive, created = Tag.objects.get_or_create(
        name='گران',
        defaults={'color': '#FF5722'}
    )

    gift, created = Tag.objects.get_or_create(
        name='هدیه',
        defaults={'color': '#4CAF50'}
    )

    urgent, created = Tag.objects.get_or_create(
        name='فوری',
        defaults={'color': '#F44336'}
    )

    # Create Plans
    free_plan, created = Plan.objects.get_or_create(
        name='رایگان',
        defaults={
            'type': 'FREE',
            'monthly_price': 0,
            'yearly_price': 0,
            'max_wishlists': 1,
            'max_items_per_list': 5,
            'can_add_images': False,
            'can_receive_contributions': False,
            'description': 'پلن رایگان با امکانات محدود'
        }
    )

    basic_plan, created = Plan.objects.get_or_create(
        name='پایه',
        defaults={
            'type': 'BASIC',
            'monthly_price': 50000,
            'yearly_price': 500000,
            'max_wishlists': 3,
            'max_items_per_list': 20,
            'can_add_images': True,
            'can_receive_contributions': True,
            'description': 'پلن پایه با امکانات بیشتر'
        }
    )

    premium_plan, created = Plan.objects.get_or_create(
        name='حرفه‌ای',
        defaults={
            'type': 'PREMIUM',
            'monthly_price': 100000,
            'yearly_price': 1000000,
            'max_wishlists': 10,
            'max_items_per_list': 100,
            'can_add_images': True,
            'can_receive_contributions': True,
            'priority_support': True,
            'description': 'پلن حرفه‌ای با تمام امکانات'
        }
    )

    print("✅ Sample data created successfully!")
    print(f"Categories: {Category.objects.count()}")
    print(f"Tags: {Tag.objects.count()}")
    print(f"Plans: {Plan.objects.count()}")


if __name__ == '__main__':
    create_sample_data()
