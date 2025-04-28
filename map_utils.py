import folium
from streamlit_folium import folium_static
import streamlit as st
from folium import plugins
import json
import logging
from geocoding_utils import get_route_with_traffic

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_map(center_lat: float, center_lon: float, zoom: int = 13) -> folium.Map:
    """Create a new map centered at the specified coordinates"""
    return folium.Map(location=[center_lat, center_lon], zoom_start=zoom)

def add_marker(map_obj: folium.Map, lat: float, lon: float, popup: str = None, color: str = 'red') -> None:
    """Add a marker to the map"""
    folium.Marker(
        location=[lat, lon],
        popup=popup,
        icon=folium.Icon(color=color)
    ).add_to(map_obj)

def add_route_with_traffic(map_obj: folium.Map, start_coords: dict, end_coords: dict) -> None:
    """Add a route to the map with traffic visualization"""
    try:
        # Get route with traffic information
        route_info = get_route_with_traffic(start_coords, end_coords)
        if not route_info:
            logger.error("Failed to get route information")
            return

        # Add markers for start and end points
        add_marker(map_obj, start_coords['latitude'], start_coords['longitude'], "نقطة البداية", 'green')
        add_marker(map_obj, end_coords['latitude'], end_coords['longitude'], "نقطة النهاية", 'red')

        # Add route with traffic visualization
        if 'traffic' in route_info and 'segments' in route_info['traffic']:
            for segment in route_info['traffic']['segments']:
                # Determine color based on traffic level
                if segment['traffic_level'] == 'heavy':
                    color = 'red'
                elif segment['traffic_level'] == 'moderate':
                    color = 'orange'
                else:
                    color = 'blue'

                # Add the route segment with appropriate color
                folium.PolyLine(
                    locations=[
                        [segment['start']['lat'], segment['start']['lon']],
                        [segment['end']['lat'], segment['end']['lon']]
                    ],
                    color=color,
                    weight=5,
                    opacity=0.8,
                    popup=f"سرعة: {segment['speed']} كم/ساعة"
                ).add_to(map_obj)

        # Add traffic legend
        legend_html = '''
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
            <p><strong>مستويات الازدحام:</strong></p>
            <p><span style="color: blue;">●</span> ازدحام خفيف</p>
            <p><span style="color: orange;">●</span> ازدحام متوسط</p>
            <p><span style="color: red;">●</span> ازدحام شديد</p>
        </div>
        '''
        map_obj.get_root().html.add_child(folium.Element(legend_html))

    except Exception as e:
        logger.error(f"Error adding route with traffic: {e}")

def save_map(map_obj: folium.Map, filename: str) -> None:
    """Save the map to an HTML file"""
    map_obj.save(filename)

def display_map(m: folium.Map):
    """Display the map in Streamlit"""
    st.subheader("خريطة المسار")
    folium_static(m) 