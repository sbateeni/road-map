import streamlit as st
import os
from dotenv import load_dotenv
from vehicle_utils import get_vehicle_specs, get_vehicle_models
from geocoding_utils import get_coordinates, search_cities, get_country_info
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
if brand:
    with st.spinner("جاري البحث عن الموديلات..."):
        models = get_vehicle_models(brand, os.getenv("GEMINI_API_KEY"))
        if models:
            model = st.selectbox("الموديل", options=models)
        else:
            st.warning("لم يتم العثور على موديلات لهذه الماركة")
            model = st.text_input("الموديل")
else:
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

# تخزين نتائج البحث في حالة الجلسة
if 'origin_cities' not in st.session_state:
    st.session_state.origin_cities = []
if 'destination_cities' not in st.session_state:
    st.session_state.destination_cities = []

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
    
    # حقل البحث لنقطة البداية
    origin_query = st.text_input("من", key="origin_search")
    if origin_query:
        with st.spinner("جاري البحث عن المدن..."):
            cities = search_cities(origin_query)
            if cities:
                st.session_state.origin_cities = cities
                origin = st.selectbox(
                    "اختر المدينة",
                    options=[city['name'] for city in cities],
                    key="origin_select"
                )
            else:
                st.warning("لم يتم العثور على مدن تطابق البحث")
    
    # حقل البحث لنقطة النهاية
    destination_query = st.text_input("إلى", key="destination_search")
    if destination_query:
        with st.spinner("جاري البحث عن المدن..."):
            cities = search_cities(destination_query)
            if cities:
                st.session_state.destination_cities = cities
                destination = st.selectbox(
                    "اختر المدينة",
                    options=[city['name'] for city in cities],
                    key="destination_select"
                )
            else:
                st.warning("لم يتم العثور على مدن تطابق البحث")
    
    # إضافة اختيار نوع المسار
    route_type = st.selectbox(
        "نوع المسار",
        ["أقصر مسار", "مسار الضفة الغربية فقط"],
        help="اختر نوع المسار المفضل"
    )
    
    # عرض معلومات البلد إذا تم إدخال العنوان
    if 'origin' in locals() and origin:
        with st.spinner("جاري جلب معلومات البلد..."):
            try:
                # استخدام الإحداثيات من نتائج البحث
                selected_city = next((city for city in st.session_state.origin_cities if city['name'] == origin), None)
                if selected_city:
                    origin_coords = {
                        "latitude": selected_city['coordinates']['latitude'],
                        "longitude": selected_city['coordinates']['longitude'],
                        "address": origin
                    }
                    
                    # الحصول على معلومات البلد
                    country_info = get_country_info(origin_coords['latitude'], origin_coords['longitude'])
                    if country_info:
                        st.session_state.origin_country_info = country_info
                        
                        st.subheader(f"معلومات البلد: {origin}")
                        
                        # عرض معلومات البلد بشكل أفضل
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("البلد", country_info['country'])
                            st.metric("العملة", f"{country_info['currency']['name']} ({country_info['currency']['symbol']})")
                        with col2:
                            st.metric("سعر البنزين 95", f"{country_info['fuel_prices']['95']} {country_info['currency']['symbol']}")
                            st.metric("سعر البنزين 91", f"{country_info['fuel_prices']['91']} {country_info['currency']['symbol']}")
                            st.metric("سعر الديزل", f"{country_info['fuel_prices']['diesel']} {country_info['currency']['symbol']}")
                    else:
                        st.error("لم يتم العثور على معلومات البلد")
                        st.session_state.origin_country_info = None
                else:
                    st.error("لم يتم العثور على معلومات المدينة")
            except Exception as e:
                logger.error(f"Error getting origin coordinates: {e}")
                st.error("حدث خطأ غير متوقع أثناء جلب معلومات البلد")
    
    if 'destination' in locals() and destination:
        with st.spinner("جاري جلب معلومات البلد..."):
            try:
                # استخدام الإحداثيات من نتائج البحث
                selected_city = next((city for city in st.session_state.destination_cities if city['name'] == destination), None)
                if selected_city:
                    destination_coords = {
                        "latitude": selected_city['coordinates']['latitude'],
                        "longitude": selected_city['coordinates']['longitude'],
                        "address": destination
                    }
                    
                    # الحصول على معلومات البلد
                    country_info = get_country_info(destination_coords['latitude'], destination_coords['longitude'])
                    if country_info:
                        st.session_state.destination_country_info = country_info
                        
                        st.subheader(f"معلومات البلد: {destination}")
                        
                        # عرض معلومات البلد بشكل أفضل
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("البلد", country_info['country'])
                            st.metric("العملة", f"{country_info['currency']['name']} ({country_info['currency']['symbol']})")
                        with col2:
                            st.metric("سعر البنزين 95", f"{country_info['fuel_prices']['95']} {country_info['currency']['symbol']}")
                            st.metric("سعر البنزين 91", f"{country_info['fuel_prices']['91']} {country_info['currency']['symbol']}")
                            st.metric("سعر الديزل", f"{country_info['fuel_prices']['diesel']} {country_info['currency']['symbol']}")
                    else:
                        st.error("لم يتم العثور على معلومات البلد")
                        st.session_state.destination_country_info = None
                else:
                    st.error("لم يتم العثور على معلومات المدينة")
            except Exception as e:
                logger.error(f"Error getting destination coordinates: {e}")
                st.error("حدث خطأ غير متوقع أثناء جلب معلومات البلد")
    
    if st.button("احسب المسارات"):
        if 'origin' in locals() and 'destination' in locals() and origin and destination:
            with st.spinner("جاري حساب المسارات..."):
                try:
                    # استخدام الإحداثيات من نتائج البحث
                    origin_city = next((city for city in st.session_state.origin_cities if city['name'] == origin), None)
                    destination_city = next((city for city in st.session_state.destination_cities if city['name'] == destination), None)
                    
                    if origin_city and destination_city:
                        origin_coords = {
                            "latitude": origin_city['coordinates']['latitude'],
                            "longitude": origin_city['coordinates']['longitude'],
                            "address": origin
                        }
                        
                        destination_coords = {
                            "latitude": destination_city['coordinates']['latitude'],
                            "longitude": destination_city['coordinates']['longitude'],
                            "address": destination
                        }
                        
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
                                        currency_symbol = st.session_state.origin_country_info.get('currency', {}).get('symbol', 'د.إ')
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
                        st.error("لم يتم العثور على معلومات المدن")
                except Exception as e:
                    logger.error(f"Error calculating routes: {e}")
                    st.error("حدث خطأ غير متوقع أثناء حساب المسارات")
        else:
            st.warning("الرجاء إدخال نقاط البداية والنهاية") 