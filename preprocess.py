
from matplotlib.pyplot import axis
import pandas as pd
from typing import List

class Preprocess():
    '''Preprocess the data
    Parameters
    -------------
    
    columns_to_drop: List
        columns to drop in the dataframe
    
    dropna_columns:list
        drop rows that is null in the columns in this list
    
    '''

    def __init__(self, columns_to_drop:List[str]=None, dropna_columns:List[str]=None):

        self.columns_to_drop = columns_to_drop
        self.dropna_columns = dropna_columns
    

    def drop_columns(self, df:pd.DataFrame):
        '''Drop unnecessary columns'''

        df.drop(self.columns_to_drop, axis=1, inplace=True)

        return df

    def drop_row(self, df:pd.DataFrame):
        '''Drop unnecessary columns'''

        df.dropna(axis=0, inplace=True)

        return df