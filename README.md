# Road Map - حاسبة تكلفة الرحلة

تطبيق ويب لحساب تكلفة الرحلات باستخدام مواصفات المركبة والمسار.

## المميزات

- البحث عن المدن وإحداثياتها
- جلب مواصفات المركبات تلقائياً
- حساب المسار مع معلومات المرور
- حساب تكلفة الوقود
- عرض المسار على الخريطة

## المتطلبات

- Python 3.8+
- Flask
- Google Generative AI API
- OpenRoute API

## التثبيت

1. استنساخ المشروع:
```bash
git clone https://github.com/yourusername/road-map.git
cd road-map
```

2. إنشاء بيئة افتراضية:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

4. إنشاء ملف `.env` وإضافة مفاتيح API:
```
GEMINI_API_KEY=your_gemini_api_key
OPENROUTE_API_KEY=your_openroute_api_key
```

## التشغيل

```bash
python app.py
```

ثم افتح المتصفح على العنوان: `http://localhost:5000`

## هيكل المشروع

```
road-map/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── config/
│   │   └── config.py
│   ├── models/
│   │   └── vehicle.py
│   ├── services/
│   │   ├── route_service.py
│   │   └── vehicle_service.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   │   └── index.html
│   └── utils/
│       └── cache_utils.py
├── cache/
│   ├── routes/
│   └── vehicles/
├── .env
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

## المساهمة

نرحب بمساهماتكم! يرجى اتباع الخطوات التالية:

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة
3. تقديم Pull Request

## الترخيص

هذا المشروع مرخص تحت رخصة MIT. 