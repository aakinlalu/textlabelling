
class DataPrep:
    def __init__(self, filename: str, split_percent: float = 0.3):
        self.filename = filename
        self.split_percent = split_percent

    def split_data(self) -> list:
        '''
        Split data into training and test set
        '''
        with open(self.filename, 'r', encoding='utf-8') as f:
            data = f.read().splitlines()
            data = [item for item in data[1:]]
            n_test = int(len(data) - (len(data) * self.split_percent))
            test = data[n_test:]
            train = data[:n_test]
        return train, test

    @staticmethod
    def text_generator(data: list) -> str:
        '''
        Generate text for labelling
        '''
        data = (item for item in data[1:] if len(item) > 1)
        for item in data:
            yield item
