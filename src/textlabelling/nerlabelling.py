import pandas as pd
from dataclasses import dataclass

import spacy
from spacy.lang.en import English


class Labelling:
    def __init__(self, text:str, nlp: spacy.lang.en.English=English()):
        """
        :param text:
        :param nlp:
        """
        self.text=text
        self.nlp=nlp

    def token_to_tuple(self) -> list:
        """
        text is tokenized. Each token is assigned start index and end index.
        Return list
        """
        doc = self.nlp(self.text)
        token_n_postion = [(token.idx, token.idx + len(token), token) for token in doc]
        result = [item for index, item in enumerate(token_n_postion)]
        return result

    def text_entities_construct(self) -> tuple:
        '''
        Prompt user to choose start index, end index and entiy class the token/feature belong to.
        Return tuple
        :return:
        '''
        k = True
        dic = {}
        data_list = []
        counter = 0
        while k:
            start_end = input('Enter start_idx, end_idx, entityName or click Enter for nothing to add:')
            if start_end == '':
                k = False
            else:
                data_list.append(start_end_ent(start_end))
                if len(data_list) > 0:
                    counter = 1
                else:
                    counter = 0
        dic['entities'] = data_list
        return (self.text, dic), counter


def start_end_ent(arg: str) -> tuple:
    """
    Simple ui for present start index, end index and token.
    Return tuple
    :return:
    :param arg:
    :return:
    """
    start, end, token = arg.split(',')
    return (int(start), int(end), token)
