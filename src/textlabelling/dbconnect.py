import configparser
import sys
import os
import re
import pandas as pd

import psycopg2

from ua_parser import user_agent_parser


class Connect:
    '''
    Class Connect takes attrubute (sql query) and has two functions
    '''
    def __init__(self, template, config_path, which_database):
        self.template = template
        self.config_path = config_path
        self.which_database = which_database
    
    @property
    def read_config(self):
        try:
            if os.path.exists(self.config_path):
                parser = configparser.ConfigParser()
            else:
                print("Config not found! Exiting!")
                sys.exit(1)
            parser.read(self.config_path)
            host = parser.get(self.which_database, 'host')
            user =parser.get(self.which_database,'user')
            password=parser.get(self.which_database,'password')
            dbname=parser.get(self.which_database,'dbname')
            port=parser.get(self.which_database,'port')
            
            #conn = psycopg2.connect(dbname=dbname, host=host, port=int(port), user=user, password=password)
            #print(f'Successfully connected to the database on host: {host}')
            return  host, user, password, dbname, port #conn
            
        
        except OSError as e:
            return f'Exception Error: {e}'
        
    
    def generate_connect(self):
        host, user, password, dbname, port = self.read_config
        try: 
            if dbname=='prd_insights':
                conn = psycopg2.connect(dbname=dbname, host=host, port=int(port), user=user, password=password)
                #return "postgresql://{host}:{port}/{dbname}?user={user}&password={password}".format(user=user, password=password, host=host, dbname=dbname, port=port)
                print(f'Successfully connected to the database on host: {host}')
                return conn
            else:
                raise ValueError('Please check your config file')
        except ValueError as e:
            return e
        
        
            
    def dbconnector(self, column_to_parse:str=None):
        '''
        Parameters:
        -----------
        column_to_parse: object
        '''
        host, user, password, dbname, port = self.read_config
        
        conn = psycopg2.connect(dbname=dbname, host=host, port=int(port), user=user, password=password)
        print(f'Successfully connected to the database on host: {host}')
        
        try:
            if column_to_parse is not None:
                df = pd.read_sql(self.template, con=conn, parse_dates=[column_to_parse])
                
            df = pd.read_sql(self.template, con=conn)
            return df
                
            
        except psycopg2.DatabaseError as e:
            print(f'database error: {e}')
            return f'database error: {e}'
               
        except Exception as e:
            print(f'database error: {e}')
            return f'Other exception error: {e}'
        
        
    
    
