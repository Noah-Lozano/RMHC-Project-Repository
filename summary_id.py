import pandas as pd
import re
import datetime
import matplotlib.pyplot as plt
import numpy as np

list_of_files = ["2018-2025.csv"]

for i in list_of_files:
    df = pd.read_csv("RMHC_" + i)
    df

    # Remove duplicates based on Entity # (donor ID) and keep only Donor Name, not Name
    donor_summary = df.groupby(['Entity #', 'Donor Name', 'Address']).agg(total_amount=('Gift Value', 'sum')).reset_index()
    donor_summary['total_amount'] = donor_summary['total_amount'].round(2)

    ########################  Record Types

    # method for record types
    record_types = df.groupby('Donor Name')['Record Type'].unique().reset_index()
    record_types['Record Types'] = record_types['Record Type'].apply(lambda x: ', '.join(sorted(x)) if isinstance(x, (list, np.ndarray)) else str(x))
    record_types = record_types.drop(columns=['Record Type'])
    donor_summary = donor_summary.merge(record_types, on='Donor Name', how='left')


    ########################  Years active

    # method for years active 
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year

    years_active = df.groupby('Donor Name')['Year'].nunique().reset_index()
    years_active.columns = ['Donor Name', 'Active Years Sum']

    donor_summary = donor_summary.merge(years_active, on='Donor Name', how='left')

    active_years = df.groupby('Donor Name')['Year'].unique().reset_index()

    # Clean up the years to remove duplicates, NaN values, and extra formatting
    active_years['Active Years'] = active_years['Year'].apply(lambda x: 
        ', '.join(map(str, sorted([year for year in x if pd.notna(year) and year != ''])))
    )
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
        original_address = str(row['Address'])
        # Find all zip codes in the address
        zip_codes = re.findall(r'(?<!\d)\d{5}(?!\d)', original_address)
        if zip_codes:
            donor_summary.at[index, 'Address'] = zip_codes[-1]
        # Keep original address if no zip code found (don't set to empty)
    
    # Debug: Check for any non-5-digit values before cleaning
    print("Before cleaning - zip codes with less than 5 digits:")
    short_zips = donor_summary[donor_summary['Address'].str.len() < 5]['Address'].unique()
    print(short_zips)
    
    # Replace zip codes with less than 5 characters with empty values
    donor_summary['Address'] = donor_summary['Address'].apply(lambda x: '' if len(str(x)) < 5 else x)
    
    # Additional validation: ensure only 5-digit zip codes remain
    donor_summary['Address'] = donor_summary['Address'].apply(lambda x: '' if not re.match(r'^\d{5}$', str(x)) else x)
    
    # Debug: Check after cleaning
    print("After cleaning - remaining zip codes:")
    remaining_zips = donor_summary[donor_summary['Address'] != '']['Address'].unique()
    print(remaining_zips)

    ########################  Events participated in

    # Count how many events each entity has participated in
    event_counts = df[df["Event"].notna()].groupby("Entity #")["Event"].count().reset_index()
    event_counts.rename(columns={"Event": "Events Engaged"}, inplace=True)

    # Merge 'Events Engaged' into donor_summary
    donor_summary = donor_summary.merge(event_counts, on="Entity #", how="left")
    donor_summary["Events Engaged"] = donor_summary["Events Engaged"].fillna(0).astype(int)

    ########################  Events List

    # method for events list
    events_list = df[df["Event"].notna()].groupby('Donor Name')['Event'].unique().reset_index()
    events_list['Events List'] = events_list['Event'].apply(lambda x: 
        ', '.join(sorted([event for event in x if pd.notna(event) and str(event).strip() != '']))
    )
    events_list = events_list.drop(columns=['Event'])
    donor_summary = donor_summary.merge(events_list, on='Donor Name', how='left')

    ########################  Campaign Count

    # Count how many campaigns each entity has participated in
    campaign_counts = df[df["Campaign"].notna()].groupby("Entity #")["Campaign"].count().reset_index()
    campaign_counts.rename(columns={"Campaign": "Campaigns Engaged"}, inplace=True)

    # Merge 'Campaigns Engaged' into donor_summary
    donor_summary = donor_summary.merge(campaign_counts, on="Entity #", how="left")
    donor_summary["Campaigns Engaged"] = donor_summary["Campaigns Engaged"].fillna(0).astype(int)

    ########################  Campaign List

    # method for campaign list
    campaign_list = df[df["Campaign"].notna()].groupby('Donor Name')['Campaign'].unique().reset_index()
    campaign_list['Campaign List'] = campaign_list['Campaign'].apply(lambda x: 
        ', '.join(sorted([campaign for campaign in x if pd.notna(campaign) and str(campaign).strip() != '']))
    )
    campaign_list = campaign_list.drop(columns=['Campaign'])
    donor_summary = donor_summary.merge(campaign_list, on='Donor Name', how='left')


    ########################  Donor Last Donation Date

    # Get the most recent donation date for each donor
    last_donation_dates = df.groupby('Donor Name')['Date'].max().reset_index()
    last_donation_dates.columns = ['Donor Name', 'Last Donation Date']
    current_date = datetime.datetime(2025, 6, 30, 0, 0, 0)
    last_donation_dates['Last Donation Date'] = pd.to_datetime(last_donation_dates['Last Donation Date'], errors='coerce')
    last_donation_dates['Days Since Last Donation'] = (current_date - last_donation_dates['Last Donation Date']).dt.days
    donor_summary = donor_summary.merge(last_donation_dates[['Donor Name', 'Days Since Last Donation']], on='Donor Name', how='left')

    ########################  Remove any remaining duplicates based on Entity #

    # Remove duplicates based on Entity # (donor ID) - keep the first occurrence
    donor_summary = donor_summary.drop_duplicates(subset=['Entity #'], keep='first')


    # Fix the filename creation
    filename = f"donor_summary_{i.replace('.csv', '')}.csv"
    donor_summary = donor_summary.sort_values('total_amount', ascending=False)
    
    # Final validation right before saving CSV - only replace values less than 5 characters
    donor_summary['Address'] = donor_summary['Address'].apply(lambda x: '' if len(str(x)) < 5 else x)
    
    ########################  Clean up list columns - remove trailing commas and whitespace
    
    # Function to clean up list columns
    def clean_list_column(value):
        if pd.isna(value) or value == '':
            return ''
        # Remove trailing commas and whitespace
        cleaned = str(value).rstrip(', ').rstrip(',').strip()
        return cleaned
    
    # Clean up all list columns
    list_columns = ['Active Years', 'Events List', 'Campaign List']
    for col in list_columns:
        if col in donor_summary.columns:
            donor_summary[col] = donor_summary[col].apply(clean_list_column)
    
    # Debug: Check what's actually being saved
    print("Final validation - checking what will be saved to CSV:")
    zip_lengths = donor_summary['Address'].str.len().value_counts().sort_index()
    print("Zip code lengths in final data:")
    print(zip_lengths)
    
    donor_summary.to_csv(filename, index=False)

