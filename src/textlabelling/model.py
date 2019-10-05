import pandas as pd
import csv
from dataclasses import dataclass
from typing import Generator

from pathlib import Path
import csv

import spacy
from spacy.lang.en import English
from spacy.util import minibatch, compounding
from spacy.util import decaying

from pyspark.sql.types import *
from pyspark.sql.functions import *


class Model:
    def __init__(self, model_dir: str):
        """
        :param model_dir:
        """
        self.model_dir = model_dir

    @property
    def load_model(self):
        """

        :return:
        """
        print("Loading from", self.model_dir)
        nlp = spacy.load(self.model_dir)
        return nlp

    def write_result_csv(self, DATA: list, filename: str) -> str:
        """

        :param DATA:
        :param filename:
        """
        nlp = self.load_model
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['text', 'intents', 'classes'])
            for text in DATA:
                intents = []
                labels = []
                doc = nlp(text)
                for ent in doc.ents:
                    intents.append(ent.text)
                    labels.append(ent.label_)
                    writer.writerow([text, intents, labels])
        print(f'{filename} has been created')

    def write_df_csv(self, df: pd.DataFrame, filename: str) -> str:
        """

        :param df:
        :param filename:
        """
        nlp = self.load_model
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['created_date', 'nps_vervatism', 'nps_score', 'intents', 'classes'])
            for index, row in df.iterrows():
                intents = []
                labels = []
                if type(row[1]) == str:
                    if len(row[1]) > 1:
                        doc = nlp(row[1])
                        for ent in doc.ents:
                            intents.append(ent.text)
                            labels.append(ent.label_)
                            writer.writerow([row[0], row[1], row[2], intents, labels])

    def write_to_redshift(self, df: pd.DataFrame):
        """

        :param df:
        :return:
        """
        nlp = self.load_model
        jdbcUrl = "jdbc:postgresql://*********"
        data = []
        for index, row in df.iterrows():
            if type(row[1]) == str:
                if len(row[1]) > 1:
                    doc = nlp(row[1])
                    for ent in doc.ents:
                        if len(ent.text) > 1:
                            row_list = [row[0].to_pydatetime().date(), row[1], row[2], row[3], ent.text, ent.label_]
                            data.append(row_list)
        try:
            if len(data) > 1:
                schema = StructType([
                    StructField('created_date', DateType(), True),
                    StructField('nps_verbatim', StringType(), True),
                    StructField('nps_score', IntegerType(), True),
                    StructField('feature_intents', StringType(), True),
                    StructField('feature_category', StringType(), True)
                ])

                df = spark.createDataFrame(data, schema=schema)

                df.write.format('jdbc') \
                    .mode('append') \
                    .option('url', jdbcUrl) \
                    .option('dbtable', 'public.nps_mobile_app') \
                    .save()
            else:
                raise Exception('There is no data to write to redshift')

        except Exception as e:
            return e

    def print_result_console(self, df: pd.DataFrame) -> str:
        """

        :param df:
        """
        nlp = self.load_model
        for index, row in df.iterrows():
            intents = []
            labels = []
            if type(row[1]) == str:
                if len(row[1]) > 1:
                    doc = nlp(row[1])
                    for ent in doc.ents:
                        intents.append(ent.text)
                        labels.append(ent.label_)
                        print(f'NPS_Score: {row[2]}')
                        print(f'NPS_verbatism:{row[1]}')
                        print('intent:', intents)
                        print('entities:', labels)
                        print('')
