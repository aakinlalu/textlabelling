import spacy
from spacy.lang.en import English
from spacy.util import minibatch, compounding
from spacy.util import decaying


class ExperimentParam:
    def __init__(self, TRAIN_DATA: list, max_batch_sizes: dict, model_type='ner',
                 dropout_start: float = 0.6, dropout_end: float = 0.2, interval: float = 1e-4):
        self.TRAIN_DATA = TRAIN_DATA
        self.max_batch_sizes = max_batch_sizes
        self.model_type = model_type
        self.dropout_start = dropout_start
        self.dropout_end = dropout_end
        self.interval = interval

    def get_batches(self):
        """
        max_batch_sizes =
        Initialize with batch size 1, and compound to a maximum determined by your data size and problem type.
         {"tagger": 32, "parser": 16, "ner": 16, "textcat": 64}
        """

        max_batch_size = self.max_batch_sizes[self.model_type]
        if len(self.TRAIN_DATA) < 1000:
            max_batch_size /= 2
        if len(self.TRAIN_DATA) < 500:
            max_batch_size /= 2
        batch_size = compounding(1, max_batch_size, 1.001)
        batches = minibatch(self.TRAIN_DATA, size=batch_size)
        return batches

    @property
    def determine_dropout(self):
        """
        For small datasets, it’s useful to set a high dropout rate at first, and decay it down towards a more reasonable value. This helps avoid the network immediately overfitting, while   still encouraging it to learn some of the more interesting things in your data.
        """
        dropout = decaying(self.dropout_start, self.dropout_end, self.interval)
        return dropout
