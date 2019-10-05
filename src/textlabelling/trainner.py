import dataclasses
from pathlib import Path
import random

import spacy
from spacy.lang.en import English
from spacy.util import minibatch, compounding
from spacy.gold import GoldParse
from spacy.scorer import Scorer


def save_model(nlp, model_dir=None):
    """

    :param model_dir:
    :param model:

    """
    try:
        if model_dir is not None:
            model_dir = Path(model_dir)
            if not model_dir.exists():
                model_dir.mkdir()
            nlp.to_disk(model_dir)
        else:
            model_dir = 'Ner_model'
            nlp.to_disk(model_dir)
        print("Saved model to", model_dir)
    except ValueError as e:
        return e

def evaluate(nlp: spacy.lang.en.English, TEST_DATA: list):
    '''
    Evaluate model on test data
    :param nlp:
    :param TEST_DATA:
    :return:
    '''
    try:
        if type(nlp) == spacy.lang.en.English and type(TEST_DATA) == list:
            scorer = Scorer()
            for input_, annot in TEST_DATA:
                doc_gold_text = nlp.make_doc(input_)
                gold = GoldParse(doc_gold_text, entities=annot)
                pred_value = nlp(input_)
                scorer.score(pred_value, gold)
            return scorer.scores
        else:
            raise ValueError('The argments is be spacy model and list')
    except ValueError as e:
        return e


class TrainNer:
    def __init__(self,TRAIN_DATA:list,
                 model: spacy.lang.en.English = None,
                 min_batch_size: float = 4.0,
                 max_batch_size: float = 32.0,
                 n_iter: int = 100):

        self.TRAIN_DATA=TRAIN_DATA
        self.model=model
        self.min_batch_size=min_batch_size
        self.max_batch_size=max_batch_size
        self.n_iter=n_iter

    def train_model(self, drop=0.5) -> spacy.lang.en.English:
        """
        Load the model, set up the pipeline and train the entity recognizer.
        :param drop:
        :return:
        """
        if self.model is not None:
            nlp = spacy.load(self.model)  # load existing spaCy model
            print("Loaded model '%s'" % self.model)
        else:
            nlp = spacy.blank("en")  # create blank Language class
            print("Created blank 'en' model")

        if "ner" not in nlp.pipe_names:
            ner = nlp.create_pipe("ner")
            nlp.add_pipe(ner, last=True)
        # otherwise, get it so we can add labels
        else:
            ner = nlp.get_pipe("ner")

        # add labels
        for _, annotations in self.TRAIN_DATA:
            for ent in annotations.get("entities"):
                ner.add_label(ent[2])

        # get names of other pipes to disable them during training
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
        with nlp.disable_pipes(*other_pipes):  # only train NER
            # reset and initialize the weights randomly – but only if we're
            # training a new model
            if self.model is None:
                optimizer = nlp.begin_training()
            else:
                optimizer = nlp.resume_training()

            for itn in range(self.n_iter):
                random.shuffle(self.TRAIN_DATA)
                losses = {}

                # batch up the examples using spaCy's minibatch
                batch_size = compounding(self.min_batch_size, self.max_batch_size, 1.001)
                batches = minibatch(self.TRAIN_DATA, size=batch_size)
                for batch in batches:
                    texts, annotations = zip(*batch)
                    nlp.update(
                        texts,  # batch of texts
                        annotations,  # batch of annotations
                        sgd=optimizer,
                        drop=drop,  # dropout - make it harder to memorise data
                        losses=losses,
                    )
                print("Losses", losses)

        return nlp, losses

    def test_model(self, TEST_DATA:list):
        """

        :param TEST_DATA:
        """
        model = self.train_model()
        # test the trained model
        for text, _ in TEST_DATA:
            doc = model(text)
            print("Classes", [(ent.text, ent.label_) for ent in doc.ents])
            print("")
