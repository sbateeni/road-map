import streamlit as st
import os
from dotenv import load_dotenv
from vehicle_utils import get_vehicle_specs
from geocoding_utils import get_coordinates
from routing_utils import get_routes
from fuel_calculator import calculate_fuel_cost, extract_fuel_consumption, convert_currency

# تحميل المتغيرات البيئية
load_dotenv()

# تكوين الصفحة
st.set_page_config(page_title="حاسبة تكلفة الرحلة", page_icon="🚗")

# العنوان
st.title("حاسبة تكلفة الرحلة 🚗")

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
    else:
        st.warning("الرجاء إدخال جميع بيانات المركبة")

# عرض حقول إدخال العناوين إذا كانت المواصفات متوفرة
if st.session_state.specs:
    st.header("نقاط الرحلة")
    origin = st.text_input("من")
    destination = st.text_input("إلى")
    
    # عرض معلومات البلد إذا تم إدخال العنوان
    if origin:
        with st.spinner("جاري جلب معلومات البلد..."):
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
                    st.metric("سعر الوقود (محلي)", f"{origin_coords['country_info']['fuel_price']['local']} {origin_coords['country_info']['currency']['symbol']}")
                    st.metric("سعر الوقود (دولار)", f"{origin_coords['country_info']['fuel_price']['usd']} $")
    
    if destination:
        with st.spinner("جاري جلب معلومات البلد..."):
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
                    st.metric("سعر الوقود (محلي)", f"{destination_coords['country_info']['fuel_price']['local']} {destination_coords['country_info']['currency']['symbol']}")
                    st.metric("سعر الوقود (دولار)", f"{destination_coords['country_info']['fuel_price']['usd']} $")
    
    if st.button("احسب المسارات"):
        if origin and destination:
            with st.spinner("جاري حساب المسارات..."):
                # تحويل العناوين إلى إحداثيات
                origin_coords = get_coordinates(origin)
                destination_coords = get_coordinates(destination)
                
                if origin_coords and destination_coords:
                    # الحصول على المسارات
                    routes = get_routes(
                        origin_coords,
                        destination_coords,
                        os.getenv("OPENROUTE_API_KEY")
                    )
                    
                    if routes:
                        # استخراج معدل استهلاك الوقود
                        fuel_consumption = extract_fuel_consumption(st.session_state.specs['specifications'])
                        
                        # استخدام سعر الوقود من البلد الأصلي
                        fuel_price = 2.18  # سعر افتراضي
                        if st.session_state.origin_country_info and 'fuel_price' in st.session_state.origin_country_info:
                            fuel_price = st.session_state.origin_country_info['fuel_price']['local']
                        
                        # عرض النتائج
                        st.header("نتائج الرحلة")
                        
                        for i, route in enumerate(routes, 1):
                            st.subheader(f"المسار {i}")
                            
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
                                st.metric("تكلفة الوقود", f"{fuel_cost['total_cost']} {st.session_state.origin_country_info['currency']['symbol'] if st.session_state.origin_country_info else 'ريال'}")
                            
                            st.metric("كمية الوقود", f"{fuel_cost['fuel_amount']} لتر")
                            st.metric("نوع الوقود", fuel_type)
                            
                            # إذا كان البلد الهدف مختلف، عرض التكلفة بالعملة المحلية للبلد الهدف
                            if st.session_state.destination_country_info and st.session_state.origin_country_info:
                                if st.session_state.destination_country_info['currency']['code'] != st.session_state.origin_country_info['currency']['code']:
                                    converted_cost = convert_currency(
                                        fuel_cost['total_cost'],
                                        st.session_state.origin_country_info['currency']['code'],
                                        st.session_state.destination_country_info['currency']['code']
                                    )
                                    st.metric(
                                        f"تكلفة الوقود ({st.session_state.destination_country_info['country']})",
                                        f"{round(converted_cost, 2)} {st.session_state.destination_country_info['currency']['symbol']}"
                                    )
                    else:
                        st.error("لم يتم العثور على المسارات")
                else:
                    st.error("لم يتم العثور على الإحداثيات للعناوين المدخلة")
        else:
            st.warning("الرجاء إدخال نقاط البداية والنهاية") 