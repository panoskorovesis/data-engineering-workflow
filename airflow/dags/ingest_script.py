import os
from time import time

import pandas as pd
from sqlalchemy import create_engine

from airflow.hooks.base_hook import BaseHook

import pip
import pkg_resources

def install_packages():
       
    installed_packages = pkg_resources.working_set
    installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
    for i in installed_packages])

    required_packages = ['psycopg2', 'pyarrow', 'pandas', 'sqlalchemy']

    for package in required_packages:
        if package not in installed_packages_list:
            pip.main(['install', package])

def ingest_callable(table_name, csv_file, execution_date, color):

    print('Will install packages')

    install_packages()

    print('Packages installed')
    print(table_name, csv_file, execution_date)

    #the connection will be done by importing the created connection
    airflow_conn = BaseHook.get_connection('pg_connection')

    engine = create_engine(f'{airflow_conn.conn_type}://{airflow_conn.login}:{airflow_conn.password}@{airflow_conn.host}/{airflow_conn.schema}')
    engine.connect()

    print('connection established successfully, inserting data...')

    csv_name = csv_file.split('/')[-1].split('.')[0] + '.csv'

    t_start = time()
    
    df_tmp = pd.read_parquet(csv_file, engine='pyarrow')
    df_tmp.to_csv('/opt/airflow/' + csv_name)

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=50000)
    df = next(df_iter)

    if color == 'yellow':
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    else:
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    df.to_sql(name=table_name, con=engine, if_exists='append')

    t_end = time()
    print('inserted the first chunk, took %.3f seconds' % (t_end - t_start))

    while True: 
        t_start = time()

        try:
            df = next(df_iter)
        except StopIteration:
            print("completed")
            break

        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

        df.to_sql(name=table_name, con=engine, if_exists='append')

        t_end = time()

        print('inserted another chunk, took %.3f seconds' % (t_end - t_start))
