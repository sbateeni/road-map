import streamlit as st
import os
from dotenv import load_dotenv
from vehicle_utils import get_vehicle_specs
from geocoding_utils import get_coordinates
from routing_utils import get_routes
from fuel_calculator import calculate_fuel_cost, extract_fuel_consumption

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
                st.success("تم جلب المواصفات بنجاح!")
                st.json(specs)
                
                # إدخال نقاط الرحلة
                st.header("نقاط الرحلة")
                origin = st.text_input("من")
                destination = st.text_input("إلى")
                
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
                                    fuel_consumption = extract_fuel_consumption(specs['specifications'])
                                    fuel_price = 2.18  # سعر اللتر (يمكن جلبها من API)
                                    
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
                                            st.metric("تكلفة الوقود", f"{fuel_cost['total_cost']} ريال")
                                        
                                        st.metric("كمية الوقود", f"{fuel_cost['fuel_amount']} لتر")
                            else:
                                st.error("لم يتم العثور على الإحداثيات للعناوين المدخلة")
                    else:
                        st.warning("الرجاء إدخال نقاط البداية والنهاية")
            else:
                st.error("حدث خطأ أثناء جلب المواصفات")
    else:
        st.warning("الرجاء إدخال جميع بيانات المركبة") 