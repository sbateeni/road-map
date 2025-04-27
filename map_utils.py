import folium
from streamlit_folium import folium_static
import streamlit as st

def create_map(origin_coords: dict, destination_coords: dict, routes: list) -> folium.Map:
    """Create an interactive map with routes"""
    # إنشاء خريطة مركزية
    m = folium.Map(
        location=[origin_coords['latitude'], origin_coords['longitude']],
        zoom_start=10
    )
    
    # إضافة علامات للنقاط
    folium.Marker(
        [origin_coords['latitude'], origin_coords['longitude']],
        popup=origin_coords['address'],
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(m)
    
    folium.Marker(
        [destination_coords['latitude'], destination_coords['longitude']],
        popup=destination_coords['address'],
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # إضافة المسارات
    colors = ['blue', 'purple', 'orange', 'darkred', 'lightred']
    for i, route in enumerate(routes):
        folium.PolyLine(
            route['geometry'],
            color=colors[i % len(colors)],
            weight=5,
            opacity=0.8,
            popup=f"المسار {i+1}: {route['distance']} كم"
        ).add_to(m)
    
    return m

def display_map(m: folium.Map):
    """Display the map in Streamlit"""
    st.subheader("خريطة المسار")
    folium_static(m) 