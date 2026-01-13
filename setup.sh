#!/bin/bash

# ======================================
# Apartment Sharing Platform Setup Script
# ======================================

echo "🏢 مرحباً بك في منصة الاستثمار العقاري"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 غير مثبت. يرجى تثبيته أولاً."
    exit 1
fi

echo "✅ Python 3 مثبت"
echo ""

# Create virtual environment
echo "📦 إنشاء البيئة الافتراضية..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 تفعيل البيئة الافتراضية..."
source venv/bin/activate

# Install requirements
echo "📥 تثبيت المكتبات المطلوبة..."
pip install -r requirements.txt

echo ""
echo "✅ تم تثبيت جميع المكتبات بنجاح!"
echo ""

# Ask if user wants to add seed data
read -p "هل تريد إضافة بيانات تجريبية؟ (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌱 إضافة البيانات التجريبية..."
    python seed_data.py
    echo "✅ تمت إضافة البيانات بنجاح!"
fi

echo ""
echo "======================================"
echo "🎉 التثبيت اكتمل بنجاح!"
echo "======================================"
echo ""
echo "📝 بيانات الدخول:"
echo "   المسؤول:"
echo "   البريد: admin@apartmentshare.com"
echo "   كلمة المرور: admin123"
echo ""
echo "   مستخدم تجريبي:"
echo "   البريد: ahmed@example.com"
echo "   كلمة المرور: password123"
echo ""
echo "🚀 لتشغيل التطبيق:"
echo "   python run.py"
echo ""
echo "🌐 ثم افتح المتصفح على:"
echo "   http://localhost:5000"
echo ""

# Ask if user wants to start the application
read -p "هل تريد تشغيل التطبيق الآن؟ (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 تشغيل التطبيق..."
    python run.py
fi
