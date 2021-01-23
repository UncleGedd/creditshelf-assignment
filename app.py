from flask import Flask, render_template
import pandas as pd
import sqlite3
from folium import FeatureGroup, LayerControl, TileLayer, Map, Marker, Icon, CircleMarker
from folium.plugins import MarkerCluster


app = Flask(__name__)


def connect_db():
    conn = None
    try:
        conn = sqlite3.connect('./data/database.db', detect_types=sqlite3.PARSE_DECLTYPES)
    except sqlite3.Error as err:
        print(err)
    if conn:
        return conn


def get_color(num_collisions, quartiles):
    if num_collisions <= quartiles[1]:
        return 'green'
    elif quartiles[1] < num_collisions < quartiles[2]:
        return '#f59b42'
    else:
        return 'red'


def create_map(df_collisions, df_stations, boroughs):
    geo_map = Map(location=[40.74527, -73.988573], tiles=None, zoom_start=12, control_scale=True)
    close_distance = 200  # meters

    # collisions
    TileLayer('Stamen Terrain', name='Collision Data').add_to(geo_map)
    for borough in boroughs:
        feature_group = FeatureGroup(name=borough.capitalize())
        marker_cluster = MarkerCluster().add_to(feature_group)
        df_collisions[df_collisions['borough'] == borough].apply(
            lambda r: Marker(
                location=[r['latitude'], r['longitude']],
                tooltip=f"{r['cyclist_injured'] + r['cyclist_killed']} cyclists injured/killed",
                icon=Icon(color='darkblue', icon='exclamation-circle', prefix='fa')).add_to(marker_cluster),
            axis=1)
        feature_group.add_to(geo_map)

    # bike stations
    quartiles = df_stations['close_collisions'].quantile([0.25, 0.5, 0.75]).tolist()
    feature_group = FeatureGroup(name='Bike Stations')
    df_stations.apply(lambda r: CircleMarker(
        location=(r['latitude'], r['longitude']),
        radius=2,
        color=get_color(r['close_collisions'], quartiles),
        tooltip=f"Bike Station {int(r['id'])}:  {int(r['close_collisions'])} collisions within {close_distance}m",
        fill=True).add_to(feature_group), axis=1)
    feature_group.add_to(geo_map)

    LayerControl(collapsed=False).add_to(geo_map)
    geo_map.save('templates/map.html')


@app.route('/')
def index():
    conn = connect_db()
    if conn:
        df_collisions = pd.read_sql_query('SELECT * FROM collisions', conn)
        df_stations = pd.read_sql_query('SELECT * FROM bike_stations', conn)
        boroughs = pd.read_sql_query('SELECT DISTINCT borough FROM collisions', conn).iloc[:, 0].tolist()
        conn.close()

        create_map(df_collisions, df_stations, boroughs)
        return render_template('index.html')
    else:
        return "database connection error"


if __name__ == '__main__':
    app.run(debug=True)
