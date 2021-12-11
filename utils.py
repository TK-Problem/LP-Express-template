import pandas as pd
import numpy as np


def calculate_order_props(df):
    """
    Calculates order's weight and volume based on the customer's provided values
    :param df:
    :return: pandas DataFrame
    """
    # download .csv files for weight and volume calculations
    df_dict = pd.read_csv('https://www.dropbox.com/s/d49sj2lqrxypewb/item_dict.csv?dl=1')
    df_dict = df_dict.set_index('Item Name')
    df_dict_v = pd.read_csv('https://www.dropbox.com/s/yzyaozknbsvjwzx/item_dict_variations.csv?dl=1')
    df_dict_v = df_dict_v.set_index(['Item Name', 'Variations'])

    """
    Helper functions to calculate weights and volumes
    """
    def get_dict_values(row, col_name='Item Weight'):
        if row['Item Name'] in df_dict.index:
            return df_dict.loc[row['Item Name'], col_name]
        else:
            return np.nan

    def get_variation_values(row, col_name='Item Weight'):
        if (row['Item Name'], row['Variations']) in df_dict_v.index:
            return df_dict_v.loc[(row['Item Name'], row['Variations']), col_name]
        else:
            return row[col_name]

    # calculate weights and volumes on provided values
    df['Item Weight'] = df.apply(lambda x: get_dict_values(x), axis=1)
    df['Item Volume'] = df.apply(lambda x: get_dict_values(x, 'Item Volume'), axis=1)
    df['Item Weight'] = df.apply(lambda x: get_variation_values(x), axis=1)
    df['Item Volume'] = df.apply(lambda x: get_variation_values(x, 'Item Volume'), axis=1)
    # multiply by Quantity
    df['Item Weight'] *= df['Quantity']
    df['Item Volume'] *= df['Quantity']

    return df
