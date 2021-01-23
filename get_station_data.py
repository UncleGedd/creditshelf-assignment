import pandas as pd
import sqlite3


def connect_db():
    conn = None
    try:
        conn = sqlite3.connect('./data/database.db', detect_types=sqlite3.PARSE_DECLTYPES)
    except sqlite3.Error as err:
        print(err)
    if conn:
        return conn


files = [
    '201901-citibike-tripdata.csv',
    '201902-citibike-tripdata.csv',
    '201903-citibike-tripdata.csv',
    '201904-citibike-tripdata.csv',
    '201905-citibike-tripdata.csv',
    '201906-citibike-tripdata.csv',
    '201907-citibike-tripdata.csv',
    '201908-citibike-tripdata.csv',
    '201909-citibike-tripdata.csv',
    '201910-citibike-tripdata.csv',
    '201911-citibike-tripdata.csv',
    '201912-citibike-tripdata.csv',
]

if __name__ == '__main__':
    # read in data from files
    print('Reading data from files')
    base = './data/'
    cols = ['start station latitude',
            'start station longitude',
            'end station latitude',
            'end station longitude',
            'start station id',
            'end station id']
    df_monthly = (pd.read_csv(base + f, usecols=cols) for f in files)
    df_year = pd.concat(df_monthly, ignore_index=True)

    # get all unique bike stations by id
    print('Processing data')
    df_start = df_year.iloc[:, :3]
    df_end = df_year.iloc[:, 3:]
    df_start.columns = df_end.columns = ['id', 'latitude', 'longitude']
    df_stations = pd.concat([df_start, df_end]).drop_duplicates().reset_index(drop=True)
    df_stations = df_stations.groupby('id').agg(lambda i: i.iloc[0]).reset_index()
    df_stations['id'] = df_stations['id'].astype(int)

    # send bike station to an external db
    conn = connect_db()
    cursor = conn.cursor()
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS collisions(
     collision_id INTEGER PRIMARY KEY,
     crash_datetime DATETIME,
     latitude DOUBLE,
     longitude DOUBLE,
     cyclist_injured INTEGER,
     cyclist_killed INTEGER,
     borough VARCHAR(255)
    )
    '''
    cursor.execute(create_table_sql)
    conn.commit()
    df_stations['close_collisions'] = 0
    df_stations.to_sql('bike_stations', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()
    print('Data saved to data/database.db')
