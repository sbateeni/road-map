# حاسبة تكلفة الرحلات

تطبيق Python لحساب تكلفة الرحلات بناءً على مواصفات المركبة والمسافة.

## المميزات

- جلب مواصفات المركبة باستخدام Gemini API
- تحويل العناوين إلى إحداثيات باستخدام Nominatim
- حساب المسارات باستخدام OpenRouteService
- حساب تكلفة الوقود بناءً على المسافة ومعدل الاستهلاك
- تخزين مؤقت للبيانات لتقليل استهلاك API

## المتطلبات

- Python 3.8+
- المكتبات المذكورة في `requirements.txt`

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
streamlit run app.py
```

## الاستخدام

1. أدخل بيانات المركبة (الماركة، الموديل، السنة)
2. انقر على "جلب المواصفات"
3. أدخل نقطة البداية والنهاية
4. انقر على "احسب المسارات"
5. اعرض النتائج (المسافة، الوقت، تكلفة الوقود)

## التخزين المؤقت

يستخدم التطبيق نظام تخزين مؤقت لتقليل استهلاك API:
- مواصفات المركبة: `cache/vehicles/`
- إحداثيات العناوين: `cache/geocode/`
- مسارات الرحلة: `cache/routes/`

## المساهمة

نرحب بمساهماتكم! يرجى إنشاء fork للمشروع وإرسال pull request.

## الترخيص

هذا المشروع مرخص تحت رخصة MIT. 