import requests
import sys
import sqlite3
import datetime as dt
from haversine import haversine
import pandas as pd


def connect_db():
    conn = None
    try:
        conn = sqlite3.connect('./data/database.db', detect_types=sqlite3.PARSE_DECLTYPES)
    except sqlite3.Error as err:
        print(err)
    if conn:
        return conn


def add_collisions_to_db(cycle_data):
    conn = connect_db()
    cursor = conn.cursor()
    create_table_sql = '''
        CREATE TABLE IF NOT EXISTS bike_stations(
         id INTEGER PRIMARY KEY,
         latitude DOUBLE,
         longitude DOUBLE
        )
        '''
    cursor.execute(create_table_sql)
    conn.commit()

    for c in cycle_data:
        try:
            insert_cycle_data_sql = f'''
                INSERT OR IGNORE INTO collisions(
                                       collision_id, 
                                       crash_datetime, 
                                       latitude, 
                                       longitude, 
                                       cyclist_injured, 
                                       cyclist_killed,
                                       borough)
                    VALUES('{c['collision_id']}', 
                           '{c['crash_datetime']}', 
                           '{c['latitude']}', 
                           '{c['longitude']}',
                           '{c['number_of_cyclist_injured']}',
                           '{c['number_of_cyclist_killed']}',
                           '{c['borough']}')
                '''
            cursor.execute(insert_cycle_data_sql)
        except KeyError:
            continue  # don't include data points that don't have locations

    conn.commit()
    conn.close()


def get_close_collisions(station_lat, station_lon, cycle_data):
    close_distance = 200  # distance in meters
    num_close = 0
    for c in cycle_data:
        try:
            distance = haversine((station_lon, station_lat), (float(c['longitude']), float(c['latitude'])))
            if distance < close_distance / 1000:
                num_close += 1
        except KeyError:
            continue  # don't include data points that don't have locations
    return num_close


def add_collision_data_to_stations(cycle_data):
    conn = connect_db()
    cursor = conn.cursor()
    df_stations = pd.read_sql_query('SELECT * FROM bike_stations', conn)
    df_stations['close_collisions'] = df_stations.apply(
        lambda r: get_close_collisions(r['latitude'], r['longitude'], cycle_data), axis=1)

    for _, station in df_stations.iterrows():
        update_sql = f"""
            UPDATE bike_stations SET
                close_collisions = {station['close_collisions']}
                WHERE id = {station['id']}
        """
        cursor.execute(update_sql)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    boroughs = ['BRONX', 'QUEENS', 'STATEN ISLAND', 'BROOKLYN', 'MANHATTAN']
    borough = sys.argv[1].upper() if sys.argv[1].upper() in boroughs else 'MANHATTAN'
    app_token = sys.argv[2]
    print('Getting data from api')
    url = 'https://data.cityofnewyork.us/resource/h9gi-nx95.json?' + \
          f'$$app_token={app_token}' + \
          f'$where=borough="{borough}" AND' + \
          '(number_of_cyclist_injured>0 OR number_of_cyclist_killed>0) AND' + \
          '(crash_date between "2019-06-01T12:00:00" and "2019-09-01T12:00:00")'

    req = requests.get(url)
    cycle_data = eval(req.text)

    for c in cycle_data:
        time = c['crash_date'].split('T')[0] + 'T' + c['crash_time']
        time_of_crash = dt.datetime.strptime(time, '%Y-%m-%dT%H:%M')
        c['crash_datetime'] = time_of_crash

    add_collisions_to_db(cycle_data)
    add_collision_data_to_stations(cycle_data)
    print('Collision data saved to data/database.db')
