import pandas as pd
import re
import datetime
import matplotlib.pyplot as plt

list_of_files = ["Inkind.csv", "Companies.csv", "Households.csv"]

for i in list_of_files:
    df = pd.read_csv("RMHC_" + i)
    donor_summary = df.groupby(['Entity #', 'Name', 'Donor Name', 'Address']).agg(total_amount=('Gift Value', 'sum')).reset_index()
    donor_summary['total_amount'] = donor_summary['total_amount'].round(2)

    ########################  Gift Source

    # method for online and exceed donations
    gift_source = df[['Entity #', 'Gift Source']].copy()
    gift_source['Gift Source'] = gift_source['Gift Source'].astype(str).str.strip().str.lower()
    gift_source = gift_source[gift_source['Gift Source'] != '']

    online_count = gift_source['Gift Source'].str.contains('online', na = False)
    exceed_count = gift_source['Gift Source'].str.contains('exceed', na = False)

    online_total = gift_source[online_count].groupby('Entity #').size()
    exceed_total = gift_source[exceed_count].groupby('Entity #').size()

    donor_summary['Online Donations'] = donor_summary['Entity #'].map(online_total).fillna(0).astype(int)
    donor_summary['Exceed Donations'] = donor_summary['Entity #'].map(exceed_total).fillna(0).astype(int)

    ########################  Years active

    # method for years active 
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year

    years_active = df.groupby('Donor Name')['Year'].nunique().reset_index()
    years_active.columns = ['Donor Name', 'Years Active']

    donor_summary = donor_summary.merge(years_active, on='Donor Name', how='left')

    active_years = df.groupby('Donor Name')['Year'].unique().reset_index()

    active_years['Active Years'] = active_years['Year'].apply(lambda x: ', '.join(map(str, sorted(x))))
    active_years = active_years.drop(columns=['Year'])
    donor_summary = donor_summary.merge(active_years, on='Donor Name', how='left')


    ########################     Fund code types

    funds = df[['Entity #', 'Fund']].copy()
    funds['Fund'] = funds['Fund'].astype(str).str.strip().str.upper()
    genop_bool = funds['Fund'] == 'GENOP'
    capca_bool = funds['Fund'] == 'CAPCA'
    dash_bool  = funds['Fund'] == '-----'


    # Count per Entity #
    genop_count = funds[genop_bool].groupby('Entity #').size()
    capca_count = funds[capca_bool].groupby('Entity #').size()
    dash_count  = funds[dash_bool].groupby('Entity #').size()


    # Add to donor_summary with .map()
    donor_summary['GENOP'] = donor_summary['Entity #'].map(genop_count).fillna(0).astype(int)
    donor_summary['CAPCA'] = donor_summary['Entity #'].map(capca_count).fillna(0).astype(int)
    donor_summary['-----'] = donor_summary['Entity #'].map(dash_count).fillna(0).astype(int)

    ########################  Times donated


    # method for times donated
    counts = df['Entity #'].value_counts()
    donor_summary['Times Donated'] = donor_summary['Entity #'].map(counts)


    ########################  Zip codes


    # method to extract zip codes from address
    for index, row in donor_summary.iterrows():
        # Find all zip codes in the address
        zip_codes = re.findall(r'(?<!\d)\d{5}(?!\d)', str(row['Address']))
        if zip_codes:
            donor_summary.at[index, 'Address'] = zip_codes[-1]
        else:
            donor_summary.at[index, 'Address'] = ''

    ########################  Events participated in

    # Count how many events each entity has participated in
    event_counts = df[df["Event"].notna()].groupby("Entity #")["Event"].count().reset_index()
    event_counts.rename(columns={"Event": "Events Engaged"}, inplace=True)


    # Merge 'Events Engaged' into donor_summary
    donor_summary = donor_summary.merge(event_counts, on="Entity #", how="left")
    donor_summary["Events Engaged"] = donor_summary["Events Engaged"].fillna(0).astype(int)

    ########################  Donor Churn Rate

    # Get the most recent donation date for each donor
    last_donation_dates = df.groupby('Donor Name')['Date'].max().reset_index()
    last_donation_dates.columns = ['Donor Name', 'Last Donation Date']
    current_date = datetime.datetime(2025, 6, 30, 0, 0, 0)
    last_donation_dates['Last Donation Date'] = pd.to_datetime(last_donation_dates['Last Donation Date'], errors='coerce')
    last_donation_dates['Days Since Last Donation'] = (current_date - last_donation_dates['Last Donation Date']).dt.days
    donor_summary = donor_summary.merge(last_donation_dates[['Donor Name', 'Days Since Last Donation']], on='Donor Name', how='left')


    ########################  

    print(donor_summary.dtypes)

    #churn_rate = 

    # Fix the filename creation
    filename = f"donor_summary_{i.replace('.csv', '')}.csv"
    donor_summary = donor_summary.sort_values('total_amount', ascending=False)
    donor_summary.to_csv(filename, index=False)

