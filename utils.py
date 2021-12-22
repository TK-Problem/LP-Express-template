import pandas as pd


def calculate_order_props(df):
    """
    Calculates order's weight and volume based on the customer's provided values
    :param df:
    :return: pandas DataFrame
    """
    # download .csv files for weight and volume calculations
    df_dict = pd.read_csv('https://www.dropbox.com/s/q98agbm62snreqy/item_dict_variations%20v2.csv?dl=1')
    df_dict.fillna('Nothing', inplace=True)

    # fill missing data for variations
    df.Variations = df.Variations.fillna('Nothing')

    # calculate weight
    df = pd.merge(df, df_dict, on=['Item Name', 'Variations'], how='left')

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
