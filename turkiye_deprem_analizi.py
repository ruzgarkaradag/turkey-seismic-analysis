import requests
import pandas as pd
import folium
from folium import Element


response = requests.get("https://api.orhanaydogdu.com.tr/deprem/kandilli/live")
data = response.json()

df = pd.DataFrame(data["result"])


df['lat'] = df['geojson'].apply(lambda x: x['coordinates'][1])
df['lng'] = df['geojson'].apply(lambda x: x['coordinates'][0])

df = df.drop(columns=['geojson', 'location_properties', 'rev'])

print(df[['title', 'lat', 'lng', 'mag']].head())

m = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles='CartoDB positron')

fg_earthquakes = folium.FeatureGroup(name="Canli Depremler")
fg_faylar = folium.FeatureGroup(name="Fay Hatlari (Tektonik)")


fay_url = "https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_boundaries.json"

folium.GeoJson(
    fay_url,
    name="Fay Hatlari",
    style_function=lambda x: {'color': 'orange', 'weight': 3} 
).add_to(fg_faylar)

for index, row in df.iterrows():
    
    
    if row['mag'] >= 4.0:
        renk = 'red'
        yaricap = 7
    elif row['mag'] >= 3.0:
        renk = 'orange'
        yaricap = 5
    else:
        renk = 'green'
        yaricap = 3

    
    folium.CircleMarker(
        location=[row['lat'], row['lng']], 
        radius=yaricap,
        color=renk,
        fill=True,
        fill_color=renk,
        fill_opacity=0.7,
        popup=f"{row['title']} ({row['mag']})"
    ).add_to(fg_earthquakes)


fg_faylar.add_to(m)
fg_earthquakes.add_to(m)


folium.LayerControl().add_to(m)



# --- 8. PROFESSIONAL SIGNATURE & ATTRIBUTION (Profesyonel İmza ve Kaynakça) ---
signature_html = '''
 <div style="position: fixed; 
     bottom: 30px; left: 30px; width: 350px; height: 160px; 
     z-index:9999; font-size:13px;
     background-color: white; opacity: 0.9; padding: 15px; 
     border-radius: 10px; border: 2px solid gray; box-shadow: 3px 3px 10px rgba(0,0,0,0.2);">
     
     <h4 style="margin-top:0;">Turkey Seismic Analysis</h4>
     
     <b>Developer:</b> Ruzgar Karadag<br>
     <hr style="margin: 5px 0;">
     
     <b>Live Data:</b> Kandilli Observatory (API)<br>
     <b>Fault Lines:</b> Hugo Ahlenius (Nordpil) & Peter Bird (2003)<br>
     <hr style="margin: 5px 0;">
     
     <i>Legend: <span style="color:green;">●</span> <3.0 | 
     <span style="color:orange;">●</span> >3.0 | 
     <span style="color:red;">●</span> >4.0</i>
 </div>
 '''

# Haritaya ekle
m.get_root().html.add_child(Element(signature_html))

# Kaydet
output_file = "turkiye_analiz_haritasi.html"
m.save(output_file)
