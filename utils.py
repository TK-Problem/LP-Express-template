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

    # read abreviation dictonary
    df_abbr = pd.read_csv('https://www.dropbox.com/s/aatrd2bed5d6bon/abbr_dict.csv?dl=1')
    df_abbr_items = df_abbr[['Item Name', 'Abbr_1']].copy()
    df_abbr_variations = df_abbr[['Variations', 'Abbr_2']].copy()
    # add nothing label
    df_abbr_variations = df_abbr_variations.append(pd.DataFrame([['Nothing', '']],
                                                                columns=['Variations', 'Abbr_2']), ignore_index=True)
    # fill nan as empty strings
    df_abbr_variations = df_abbr_variations.dropna(subset=['Variations']).fillna('')
    # add dash before abbreviation
    df_abbr_variations.Abbr_2 = df_abbr_variations.Abbr_2.apply(lambda x: '-' + x if x != '' else x)

    # delete unnecessary data
    del df_abbr

    # add abbreviations
    df = pd.merge(df, df_abbr_items, on=['Item Name'], how='left')
    df = pd.merge(df, df_abbr_variations, on=['Variations'], how='left')
    # merge abbreviations
    df['Abbr'] = df.Abbr_1 + df.Abbr_2
    df.drop(['Abbr_1', 'Abbr_2'], axis=1, inplace=True)

    # delete unnecessary data
    del df_abbr_items, df_abbr_variations

    return df


def find_parcels(df):
    """
    This function aggregates orders into parcels.
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
    agg_dict = {'Item Weight': 'sum', 'Item Volume': 'sum', 'Price': 'sum', 'Abbr': '_'.join}
    df_parcels = df[~df.Abbr.isna()].groupby(col_names_1).agg(agg_dict)

    # add address info
    df_parcels = df_ship.join(df_parcels).reset_index()

    # add state to city column
    _ = df_parcels.loc[df_parcels['Ship State'] != '', 'Ship City'] + ', '
    _ += df_parcels.loc[df_parcels['Ship State'] != '', 'Ship State']
    df_parcels.loc[df_parcels['Ship State'] != '', 'Ship City'] = _.values

    # add dummy column for parcels type
    df_parcels['Siuntinio tipas'] = ''
    df_parcels['Pirmenybinis'] = 0

    country_dict = {'France': 'Pranc??zija', 'United States': 'Jungtin??s Amerikos Valstijos',
                    'Australia': 'Australija', 'KR': 'Piet?? Kor??ja',
                    'United Kingdom': 'Did??ioji Britanija', 'Germany': 'Vokietija', 'SE': '??vedija', 'RU': 'Rusija',
                    'NL': 'Olandija (Nyderlandai)', 'Austria': 'Austrija', 'HR': 'Kroatija', 'BE': 'Belgija',
                    'Canada': 'Kanada', 'PL': 'Lenkija', 'Denmark': 'Danija', 'IL': 'Izraelis', 'PT': 'Portugalija',
                    'GR': 'Graikija', 'IS': 'Islandija', 'FI': 'Suomija', 'SK': 'Slovakija', 'RO': 'Rumunija',
                    'SI': 'Slov??nija', 'Norway': 'Norvegija', 'JP': 'Japonija', 'ES': 'Ispanija', 'HU': 'Vengrija',
                    'CH': '??veicarija', 'LT': 'Lietuva', 'Italy': 'Italija', 'SG': 'Singap??ras', 'TW': 'Taivanas',
                    'IE': 'Airija', 'NZ': 'Naujoji Zelandija', 'EE': 'Estija', 'ID': 'Indonezija', 'HK': 'Honkongas',
                    'CZ': '??ekija', 'RS': 'Serbija', 'BG': 'Bulgarija', 'TH': 'Tailandas', 'MY': 'Malaizija',
                    'LU': 'Liukuksemburgas'
                    }

    # rename columns
    df_parcels = df_parcels.rename(columns={'Ship Name': 'Gav??jas',
                                            'Ship Country': '??alis',
                                            'Ship City': 'Miestas',
                                            'Sale Date': 'Pardavimo data',
                                            'Ship Zipcode': 'Pa??to kodas',
                                            'Ship Address1': 'Adreso eilut?? 1',
                                            'Ship Address2': 'Adreso eilut?? 2',
                                            'Price': 'Siuntinio vert??',
                                            'Item Weight': 'Siuntinio svoris',
                                            'Item Volume': 'Siuntinio t??ris',
                                            'Abbr': 'Pristatymo pastabos'})

    # generate email
    df_parcels['Pristatymo pastabos'] += '_@a.com'

    # rename countries
    df_parcels['??alis'] = df_parcels['??alis'].replace(country_dict)

    # assign package type
    cond_1 = df_parcels['Siuntinio svoris'] <= 500
    cond_2 = df_parcels['Siuntinio t??ris'] < 60
    df_parcels.loc[cond_1 & cond_2, 'Siuntinio tipas'] = 'S'
    df_parcels.loc[~(cond_1 & cond_2), 'Siuntinio tipas'] = 'M'

    # pirmenybinis
    cond_1 = df_parcels['Siuntinio vert??'] >= 70
    df_parcels.loc[cond_1, 'Pirmenybinis'] = 1

    # rearrange column order
    df_parcels = df_parcels[['Pardavimo data', 'Siuntinio vert??',
                             'Siuntinio tipas', 'Siuntinio svoris', 'Siuntinio t??ris',
                             'Pirmenybinis',
                             'Gav??jas', '??alis', 'Miestas', 'Adreso eilut?? 1', 'Adreso eilut?? 2',
                             'Pa??to kodas', 'Pristatymo pastabos']]

    return df_parcels
