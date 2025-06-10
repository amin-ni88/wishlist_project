#!/bin/bash

echo "📱 راه‌اندازی اپلیکیشن React Native"
echo "===================================="

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

# بررسی وجود node_modules
if [ ! -d "node_modules" ]; then
    print_warning "node_modules یافت نشد. در حال نصب dependencies..."
    npm install
    print_status "Dependencies نصب شدند"
fi

# انتخاب پلتفرم
echo "کدام پلتفرم را می‌خواهید اجرا کنید؟"
echo "1) Android"
echo "2) iOS"
echo "3) فقط Metro Bundler"

read -p "انتخاب کنید (1-3): " platform

case $platform in
    1)
        print_info "راه‌اندازی برای Android..."
        print_warning "مطمئن شوید که Android emulator یا دستگاه متصل است"
        npx react-native run-android
        ;;
    2)
        print_info "راه‌اندازی برای iOS..."
        print_warning "فقط روی macOS قابل اجرا است"
        npx react-native run-ios
        ;;
    3)
        print_info "راه‌اندازی Metro Bundler..."
        print_info "Metro در آدرس http://localhost:8081 در دسترس خواهد بود"
        npx react-native start
        ;;
    *)
        print_error "انتخاب نامعتبر"
        exit 1
        ;;
esac 