# حاسبة تكلفة الرحلة

تطبيق ويب لحساب تكلفة الرحلة بناءً على نوع المركبة والمسافة والوقود.

## المميزات

- حساب تكلفة الرحلة بناءً على نوع المركبة
- عرض المسارات على الخريطة
- عرض معلومات الازدحام المروري
- دعم المدن الفلسطينية
- واجهة مستخدم سهلة الاستخدام

## المتطلبات

- Python 3.8+
- Flask
- OpenRoute API
- Gemini API

## التثبيت

1. قم بتثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

2. قم بإنشاء ملف `.env` وأضف مفاتيح API:
```
OPENROUTE_API_KEY=your_openroute_api_key
GEMINI_API_KEY=your_gemini_api_key
```

3. قم بتشغيل التطبيق:
```bash
python app.py
```

## الاستخدام

1. افتح المتصفح وانتقل إلى `http://localhost:5000`
2. أدخل بيانات المركبة
3. اختر نقاط البداية والنهاية
4. اضغط على "احسب المسارات" لعرض النتائج

## المساهمة

نرحب بمساهماتكم! يرجى اتباع الخطوات التالية:

1. قم بعمل fork للمشروع
2. قم بإنشاء فرع جديد (`git checkout -b feature/amazing-feature`)
3. قم بعمل commit للتغييرات (`git commit -m 'Add some amazing feature'`)
4. قم بعمل push للفرع (`git push origin feature/amazing-feature`)
5. قم بفتح طلب pull request

## الترخيص

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل. 