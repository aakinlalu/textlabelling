import pickle
from collections import Counter

from bokeh.io import push_notebook, show
from bokeh.models import HoverTool
from bokeh.plotting import figure


class NerStats:

    @staticmethod
    def save_labelled_data(file_name: str, data: list):
        '''
        Pickle or save labelled dataset
        -------
          print the name of the file to the console.
          :param file_name:
          :param data:
          :return:
        '''
        try:
            if type(file_name) == str and type(data) == list:
                with open(file_name, 'wb') as f:
                    pickle.dump(data, f)
                print(f'The TRAIN_DATA has been pickled as file: {file_name}')
            else:
                raise ValueError('Please ensure that two arguments are string and list')
        except ValueError as e:
            return e

    @staticmethod
    def load_labelled_data(file_name: str) -> list:
        '''
        load labelled data for use

        Parameters:
        ----------
        file_name:str
             pickle file

        Return
        ------
          list
        '''

        try:
            if file_name:
                with open(file_name, 'rb') as f:
                    labelled_data = pickle.load(f)
                return labelled_data
            else:
                raise ValueError('Ensure that the pickle file is provided')

        except ValueError as e:
            return e

    @staticmethod
    def data_distribution(TRAIN_DATA: list) -> dict:
        """

        :param TRAIN_DATA:
        :return:
        """
        entity_list = []
        for item in TRAIN_DATA:
            entity_value = item[1]['entities']
            if len(entity_value) > 0:
                for i in entity_value:
                    entity_list.append(i[2])
        data = dict(Counter(entity_list))
        return data

    @staticmethod
    def distribution_visualizer(data: dict, title: str = None, x_axis: str = None, y_axis: str = None):
        """

        :param data:
        :param title:
        :param x_axis:
        :param y_axis:
        """
        entities = list(data.keys())
        value = list(data.values())

        hover = HoverTool(
            tooltips=[
                ("Entities", "@entities"),
                ("Counts", "$value"),
            ]
        )

        p = figure(x_range=entities, plot_height=300, title=title, toolbar_location='above', tools=[hover])

        p.vbar(x=entities, top=value, width=0.9)

        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None

        t = show(p, notebook_handle=True)

        push_notebook(t)
