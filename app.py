import streamlit as st
import os
from dotenv import load_dotenv
from vehicle_utils import get_vehicle_specs
from geocoding_utils import get_coordinates
from routing_utils import get_routes
from fuel_calculator import calculate_fuel_cost, extract_fuel_consumption
from map_utils import create_map, display_map
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تحميل المتغيرات البيئية
load_dotenv()

# تكوين الصفحة
st.set_page_config(page_title="حاسبة تكلفة الرحلة", page_icon="🚗", layout="wide")

# العنوان
st.title("حاسبة تكلفة الرحلة 🚗")

# التحقق من وجود مفاتيح API
if not os.getenv("GEMINI_API_KEY"):
    st.error("مفتاح Gemini API غير موجود. الرجاء إضافة المفتاح في ملف .env")
    st.stop()

if not os.getenv("OPENROUTE_API_KEY"):
    st.error("مفتاح OpenRoute API غير موجود. الرجاء إضافة المفتاح في ملف .env")
    st.stop()

# إدخال بيانات المركبة
st.header("بيانات المركبة")
brand = st.text_input("الماركة")
model = st.text_input("الموديل")
year = st.number_input("سنة التصنيع", min_value=1900, max_value=2024, value=2020)
fuel_type = st.selectbox("نوع الوقود", ["بنزين 95", "بنزين 91", "ديزل"])

# تخزين المواصفات في حالة الجلسة
if 'specs' not in st.session_state:
    st.session_state.specs = None

# تخزين معلومات البلد في حالة الجلسة
if 'origin_country_info' not in st.session_state:
    st.session_state.origin_country_info = None
if 'destination_country_info' not in st.session_state:
    st.session_state.destination_country_info = None

# زر جلب المواصفات
if st.button("جلب المواصفات"):
    if brand and model and year:
        with st.spinner("جاري جلب المواصفات..."):
            try:
                specs = get_vehicle_specs(
                    brand, 
                    model, 
                    year, 
                    os.getenv("GEMINI_API_KEY")
                )
                
                if specs:
                    st.session_state.specs = specs
                    st.success("تم جلب المواصفات بنجاح!")
                    st.json(specs)
                else:
                    st.error("حدث خطأ أثناء جلب المواصفات")
            except Exception as e:
                logger.error(f"Error getting vehicle specs: {e}")
                st.error("حدث خطأ غير متوقع أثناء جلب المواصفات")
    else:
        st.warning("الرجاء إدخال جميع بيانات المركبة")

# عرض حقول إدخال العناوين إذا كانت المواصفات متوفرة
if st.session_state.specs:
    st.header("نقاط الرحلة")
    origin = st.text_input("من")
    destination = st.text_input("إلى")
    
    # إضافة اختيار نوع المسار
    route_type = st.selectbox(
        "نوع المسار",
        ["أقصر مسار", "مسار الضفة الغربية فقط"],
        help="اختر نوع المسار المفضل"
    )
    
    # عرض معلومات البلد إذا تم إدخال العنوان
    if origin:
        with st.spinner("جاري جلب معلومات البلد..."):
            try:
                origin_coords = get_coordinates(origin)
                if origin_coords and 'country_info' in origin_coords:
                    st.session_state.origin_country_info = origin_coords['country_info']
                    st.subheader(f"معلومات البلد: {origin}")
                    
                    # عرض معلومات البلد بشكل أفضل
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("البلد", origin_coords['country_info']['country'])
                        st.metric("العملة", f"{origin_coords['country_info']['currency']['name']} ({origin_coords['country_info']['currency']['symbol']})")
                    with col2:
                        st.metric("سعر البنزين 95", f"{origin_coords['country_info']['fuel_prices']['95']} {origin_coords['country_info']['currency']['symbol']}")
                        st.metric("سعر البنزين 91", f"{origin_coords['country_info']['fuel_prices']['91']} {origin_coords['country_info']['currency']['symbol']}")
                        st.metric("سعر الديزل", f"{origin_coords['country_info']['fuel_prices']['diesel']} {origin_coords['country_info']['currency']['symbol']}")
                else:
                    st.error("لم يتم العثور على معلومات البلد")
                    st.session_state.origin_country_info = None
            except Exception as e:
                logger.error(f"Error getting origin coordinates: {e}")
                st.error("حدث خطأ غير متوقع أثناء جلب معلومات البلد")
    
    if destination:
        with st.spinner("جاري جلب معلومات البلد..."):
            try:
                destination_coords = get_coordinates(destination)
                if destination_coords and 'country_info' in destination_coords:
                    st.session_state.destination_country_info = destination_coords['country_info']
                    st.subheader(f"معلومات البلد: {destination}")
                    
                    # عرض معلومات البلد بشكل أفضل
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("البلد", destination_coords['country_info']['country'])
                        st.metric("العملة", f"{destination_coords['country_info']['currency']['name']} ({destination_coords['country_info']['currency']['symbol']})")
                    with col2:
                        st.metric("سعر البنزين 95", f"{destination_coords['country_info']['fuel_prices']['95']} {destination_coords['country_info']['currency']['symbol']}")
                        st.metric("سعر البنزين 91", f"{destination_coords['country_info']['fuel_prices']['91']} {destination_coords['country_info']['currency']['symbol']}")
                        st.metric("سعر الديزل", f"{destination_coords['country_info']['fuel_prices']['diesel']} {destination_coords['country_info']['currency']['symbol']}")
                else:
                    st.error("لم يتم العثور على معلومات البلد")
                    st.session_state.destination_country_info = None
            except Exception as e:
                logger.error(f"Error getting destination coordinates: {e}")
                st.error("حدث خطأ غير متوقع أثناء جلب معلومات البلد")
    
    if st.button("احسب المسارات"):
        if origin and destination:
            with st.spinner("جاري حساب المسارات..."):
                try:
                    # تحويل العناوين إلى إحداثيات
                    origin_coords = get_coordinates(origin)
                    destination_coords = get_coordinates(destination)
                    
                    if origin_coords and destination_coords:
                        # الحصول على المسارات
                        routes = get_routes(
                            origin_coords,
                            destination_coords,
                            os.getenv("OPENROUTE_API_KEY"),
                            route_type=route_type
                        )
                        
                        if routes:
                            # استخراج معدل استهلاك الوقود
                            fuel_consumption = extract_fuel_consumption(st.session_state.specs)
                            
                            # استخدام سعر الوقود المناسب حسب النوع المختار
                            if st.session_state.origin_country_info and 'fuel_prices' in st.session_state.origin_country_info:
                                if fuel_type == "بنزين 95":
                                    fuel_price = st.session_state.origin_country_info['fuel_prices']['95']
                                elif fuel_type == "بنزين 91":
                                    fuel_price = st.session_state.origin_country_info['fuel_prices']['91']
                                else:  # ديزل
                                    fuel_price = st.session_state.origin_country_info['fuel_prices']['diesel']
                                
                                # عرض النتائج
                                st.header("نتائج الرحلة")
                                
                                # إنشاء وعرض الخريطة
                                m = create_map(origin_coords, destination_coords, routes)
                                display_map(m)
                                
                                for i, route in enumerate(routes):
                                    # حساب تكلفة الوقود
                                    fuel_cost = calculate_fuel_cost(
                                        route['distance'],
                                        fuel_consumption,
                                        fuel_price
                                    )
                                    
                                    # عرض المعلومات
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("المسافة", f"{route['distance']} كم")
                                    with col2:
                                        st.metric("الوقت", f"{route['duration']} دقيقة")
                                    with col3:
                                        currency_symbol = st.session_state.origin_country_info.get('currency', {}).get('symbol', '₪') if st.session_state.origin_country_info else '₪'
                                        st.metric("تكلفة الوقود", f"{fuel_cost['total_cost']} {currency_symbol}")
                                    
                                    # عرض تفاصيل الحساب
                                    st.subheader("تفاصيل الحساب")
                                    st.write(f"معدل استهلاك الوقود: {fuel_cost['consumption_rate']} لتر/100 كم")
                                    st.write(f"كفاءة استهلاك الوقود: {fuel_cost['efficiency']} كم/لتر")
                                    st.write(f"سعر الوقود: {fuel_price} {currency_symbol}/لتر")
                                    st.write(f"كمية الوقود المطلوبة: {fuel_cost['fuel_needed_liters']} لتر")
                                    st.write(f"تكلفة الوقود: {fuel_cost['total_cost']} {currency_symbol}")
                                    st.write(f"نوع الوقود: {fuel_type}")
                        else:
                            st.error("لم يتم العثور على المسارات")
                    else:
                        st.error("لم يتم العثور على الإحداثيات للعناوين المدخلة")
                except Exception as e:
                    logger.error(f"Error calculating routes: {e}")
                    st.error("حدث خطأ غير متوقع أثناء حساب المسارات")
        else:
            st.warning("الرجاء إدخال نقاط البداية والنهاية") 