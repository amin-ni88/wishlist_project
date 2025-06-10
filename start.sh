#!/bin/bash

echo "🎁 راه‌اندازی پروژه لیست آرزو"
echo "================================"

# رنگ‌ها برای خروجی
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# تابع برای چاپ پیام‌های رنگی
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# بررسی وجود محیط مجازی
if [ ! -d "venv" ]; then
    print_warning "محیط مجازی یافت نشد. در حال ایجاد..."
    python3 -m venv venv
    print_status "محیط مجازی ایجاد شد"
fi

# فعال‌سازی محیط مجازی
print_info "فعال‌سازی محیط مجازی..."
source venv/bin/activate

# نصب dependencies
print_info "نصب dependencies..."
pip install -r requirements.txt

# اجرای migrations
print_info "اجرای migrations..."
python manage.py makemigrations
python manage.py migrate

# ایجاد superuser (اختیاری)
read -p "آیا می‌خواهید superuser ایجاد کنید؟ (y/n): " create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    python manage.py createsuperuser
fi

# راه‌اندازی سرور
print_status "راه‌اندازی سرور Django..."
print_info "سرور در آدرس http://127.0.0.1:8001 در دسترس خواهد بود"
print_info "برای توقف سرور از Ctrl+C استفاده کنید"

python manage.py runserver 8001 