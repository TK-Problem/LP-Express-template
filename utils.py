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


def find_parcels(df):
    """

    :param df: pandas DataFrame, Etsy order list
    :return:
    """
    # take only items with known weights and volumes
    df = df.loc[~df['Item Weight'].isna() & ~df['Item Volume'].isna()].copy()

    # get shipment info
    col_names = ['Sale Date', 'Ship Address2', 'Ship State', 'Ship Zipcode', 'Ship Country']
    df_ship = df.set_index(['Ship Name', 'Ship City', 'Ship Address1'])[col_names].fillna('')
    # keep newest data entries
    df_ship = df_ship.drop_duplicates(keep='first')

    # create new DataFrame for parcels
    col_names_1 = ['Ship Name', 'Ship City', 'Ship Address1']
    col_names_2 = ['Item Weight', 'Item Volume', 'Price']
    df_parcels = df.groupby(col_names_1)[col_names_2].sum()

    # add address info
    df_parcels = df_ship.join(df_parcels).reset_index()

    # add state to city column
    _ = df_parcels.loc[df_parcels['Ship State'] != '', 'Ship City'] + ', '
    _ += df_parcels.loc[df_parcels['Ship State'] != '', 'Ship State']
    df_parcels.loc[df_parcels['Ship State'] != '', 'Ship City'] = _.values

    # add dummy column for parcels type
    df_parcels['Siuntinio tipas'] = ''
    df_parcels['Pirmenybinis'] = 0
    df_parcels['Pristatymo pastabos'] = ''

    # rename columns
    df_parcels = df_parcels.rename(columns={'Ship Name': 'Gavėjas',
                                            'Ship Country': 'Šalis',
                                            'Ship City': 'Miestas',
                                            'Sale Date': 'Pardavimo data',
                                            'Ship Zipcode': 'Pašto kodas',
                                            'Ship Address1': 'Adreso eilutė 1',
                                            'Ship Address2': 'Adreso eilutė 2',
                                            'Price': 'Siuntinio vertė',
                                            'Item Weight': 'Siuntinio svoris',
                                            'Item Volume': 'Siuntinio tūris'})

    # rearrange column order
    df_parcels = df_parcels[['Pardavimo data', 'Siuntinio vertė',
                             'Siuntinio tipas', 'Siuntinio svoris', 'Siuntinio tūris',
                             'Pirmenybinis',
                             'Gavėjas', 'Šalis', 'Miestas', 'Adreso eilutė 1', 'Adreso eilutė 2',
                             'Pašto kodas', 'Pristatymo pastabos']]

    return df_parcels
