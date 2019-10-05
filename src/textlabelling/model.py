from pathlib import Path
import re

import psycopg2

import spacy
import pandas as pd

from spacy.tokenizer import Tokenizer
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import English, LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
from nltk.stem import  SnowballStemmer

from src.textlabelling.Dbconnect import Connect


stammer = SnowballStemmer('english')
nlp = English()
tokenizer = Tokenizer(nlp.vocab)
lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

def apply_stem(sent):
    try:
        return " ".join([stammer.stem(str(word)) for word in tokenizer(sent) if len(word)>1])
    
    except Exception as e:
        return e

def apply_lemmas(sent):
    try:
        return " ".join([lemmatizer(lemmatizer(str(word), "NOUN")[0],"VERB")[0] for word in tokenizer(sent) if len(str(word))>1])
    
    except Exception as e:
        return e
   


class Model(Connect):

    def __init__(self, output_dir: str, template, config_path, db_system):
        self.output_dir = output_dir
        super().__init__(template, config_path, db_system)

    def load_model(self):
        print("Loading from", self.output_dir)
        nlp = spacy.load(self.output_dir)
        return nlp

    
    
    def model_to_data(self):
        try:
            nlp = self.load_model()
            df = super().dbconnector()
            data = []
            for index, row in df.iterrows():
                if len(row[2]) > 2 and type(row[2]) == str:
                    doc = nlp(row[2].lower())
                    for ent in doc.ents:
                        if len(ent.text) > 2:
                            row_list = (row[0], row[1], row[3], apply_lemmas(ent.text), ent.label_)
                            #print(row_list)
                            data.append(row_list)
            return data
        except Exception as e:
            print(e)
                            
                            
    
    def insert_to_redshift(self):
        """ insert multiple vendors into the vendors table  """
        sql = "INSERT INTO public.nps_mobile_app(created_date, reference_ticket,nps_score,feature_intents,feature_category) VALUES(%s,%s,%s,%s,%s)"
        #conn =super().generate_connect()
        #conn = psycopg2.connect(dbname=dbname, host=host, port=int(port), user=user, password=password)
        #data = self.model_to_data()
        try:
            data = self.model_to_data()
            conn =super().generate_connect()
            # create a new cursor
            cur = conn.cursor()
            # execute the INSERT statement
            cur.executemany(sql,data)
            # commit the changes to the database
            conn.commit()
            # close communication with the database
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()   

        

