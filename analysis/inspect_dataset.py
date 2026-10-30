"""
Detailed dataset inspection and exploratory analysis for SmartCOD AI.
Analyzes raw data, identifies anomalies, duplicates, inconsistencies, and risk factors.
"""

import json
import pandas as pd
import numpy as np
import re

def analyze_raw_dataset(csv_path="data/orders_sample.csv"):
    df = pd.read_csv(csv_path)
    print(f"Total raw records: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # 1. Status normalization & distribution
    print("\n--- Raw final_status counts ---")
    print(df['final_status'].value_counts(dropna=False))
    
    df['status_clean'] = df['final_status'].astype(str).str.strip().str.upper()
    print("\n--- Cleaned final_status counts ---")
    print(df['status_clean'].value_counts(dropna=False))
    
    # 2. Missing values
    print("\n--- Missing values per column ---")
    null_counts = df.isnull().sum()
    print(null_counts[null_counts > 0])
    
    # Check for empty strings in object columns
    empty_str_counts = {}
    for col in df.select_dtypes(include='object').columns:
        empties = (df[col].astype(str).str.strip() == '').sum()
        if empties > 0:
            empty_str_counts[col] = int(empties)
    print(f"\nEmpty string counts: {empty_str_counts}")
    
    # 3. Duplicate Order IDs
    order_id_counts = df['order_id'].value_counts()
    dup_ids = order_id_counts[order_id_counts > 1]
    print(f"\nUnique order IDs: {df['order_id'].nunique()}")
    print(f"Duplicate order IDs count: {len(dup_ids)} (total rows with duplicate IDs: {dup_ids.sum()})")
    print("Sample duplicate order IDs:")
    print(dup_ids.head(10))
    
    # Inspect duplicate rows
    sample_dups = df[df['order_id'].isin(dup_ids.head(5).index)].sort_values('order_id')
    print("\nDetailed view of duplicate order IDs:")
    print(sample_dups[['order_id', 'order_datetime', 'customer_name', 'phone', 'order_value', 'status_clean']])
    
    # Check if duplicate order IDs have conflicting data or identical data
    conflicting_dups = []
    identical_dups = []
    for oid in dup_ids.index:
        sub = df[df['order_id'] == oid]
        # check if all columns except possibly index are identical
        sub_no_idx = sub.drop(columns=['status_clean'])
        if len(sub_no_idx.drop_duplicates()) == 1:
            identical_dups.append(oid)
        else:
            conflicting_dups.append(oid)
    print(f"\nIdentical duplicate rows: {len(identical_dups)}, Conflicting duplicate rows: {len(conflicting_dups)}")
    if conflicting_dups:
        print("Conflicting sample:", conflicting_dups[:5])
        print(df[df['order_id'].isin(conflicting_dups[:3])][['order_id', 'order_datetime', 'customer_name', 'final_status']])

    # 4. Check KT150xxx series IDs
    kt15_orders = df[df['order_id'].str.startswith('KT15', na=False)]
    print(f"\nKT15xxxx series count: {len(kt15_orders)}")
    print(kt15_orders.head(5)[['order_id', 'order_datetime', 'customer_name', 'phone']])
    
    # Check if phone numbers in KT15xxxx match earlier KT10xxxx
    kt10_phones = set(df[df['order_id'].str.startswith('KT10', na=False)]['phone'].dropna())
    kt15_phones = set(kt15_orders['phone'].dropna())
    overlap_phones = kt10_phones.intersection(kt15_phones)
    print(f"KT15xxxx phones overlapping with KT10xxxx phones: {len(overlap_phones)} out of {len(kt15_phones)}")

    # 5. Suspicious Customer Names
    test_names = ["test", "test order", "qwerty", "asdf", "xyz", "xyz xyz", "abc", "na"]
    df['name_lower'] = df['customer_name'].astype(str).str.strip().str.lower()
    suspicious_mask = df['name_lower'].isin(test_names) | (df['name_lower'].str.len() <= 2)
    print(f"\nSuspicious names count: {suspicious_mask.sum()}")
    print("Breakdown of suspicious names:")
    print(df[suspicious_mask]['name_lower'].value_counts())
    
    # RTO rate on suspicious names
    susp_df = df[suspicious_mask & (df['status_clean'].isin(['DELIVERED', 'RTO']))]
    susp_rto_rate = (susp_df['status_clean'] == 'RTO').mean()
    print(f"RTO rate for suspicious names: {susp_rto_rate:.2%} ({len(susp_df)} completed orders)")

    # 6. Address Quality Analysis
    # Short addresses, placeholder addresses
    df['addr_str'] = df['address'].astype(str).str.strip()
    df['addr_len'] = df['addr_str'].str.len()
    
    placeholder_addrs = ["xyz", "call me", "home", ".", "near station", "delhi", "mumbai", "hyderabad", "patna", "sagar", "darbhanga", "guwahati", "chennai"]
    df['is_placeholder_addr'] = df['addr_str'].str.lower().isin(placeholder_addrs) | (df['addr_len'] < 10)
    print(f"\nPlaceholder/short address count: {df['is_placeholder_addr'].sum()}")
    
    addr_df = df[df['status_clean'].isin(['DELIVERED', 'RTO'])]
    short_addr_rto = (addr_df[addr_df['is_placeholder_addr']]['status_clean'] == 'RTO').mean()
    normal_addr_rto = (addr_df[~addr_df['is_placeholder_addr']]['status_clean'] == 'RTO').mean()
    print(f"RTO rate for placeholder/very short address: {short_addr_rto:.2%} (vs {normal_addr_rto:.2%} for detailed address)")

    # 7. Customer Prior Orders & Prior RTO
    print("\n--- Prior Orders & RTO Matrix ---")
    print("Prior Orders Distribution:")
    print(df['customer_prior_orders'].value_counts().sort_index())
    
    # First-time vs repeat
    df['is_first_time'] = df['customer_prior_orders'] == 0
    completed = df[df['status_clean'].isin(['DELIVERED', 'RTO'])].copy()
    first_time_rto = (completed[completed['is_first_time']]['status_clean'] == 'RTO').mean()
    repeat_rto = (completed[~completed['is_first_time']]['status_clean'] == 'RTO').mean()
    print(f"\nFirst-time customer RTO rate: {first_time_rto:.2%} ({completed['is_first_time'].sum()} orders)")
    print(f"Repeat customer RTO rate: {repeat_rto:.2%} ({(~completed['is_first_time']).sum()} orders)")
    
    # Prior RTO effect on repeat customers
    repeat_custs = completed[~completed['is_first_time']]
    repeat_with_rto = (repeat_custs[repeat_custs['customer_prior_rto'] > 0]['status_clean'] == 'RTO').mean()
    repeat_no_rto = (repeat_custs[repeat_custs['customer_prior_rto'] == 0]['status_clean'] == 'RTO').mean()
    print(f"Repeat customers with prior RTO history: {repeat_with_rto:.2%} ({len(repeat_custs[repeat_custs['customer_prior_rto'] > 0])} orders)")
    print(f"Repeat customers with CLEAN prior history: {repeat_no_rto:.2%} ({len(repeat_custs[repeat_custs['customer_prior_rto'] == 0])} orders)")

    # 8. Courier RTO Rates
    print("\n--- Courier Performance ---")
    courier_summary = completed.groupby('courier').agg(
        orders=('order_id', 'count'),
        rto_count=('status_clean', lambda s: (s == 'RTO').sum()),
        rto_rate=('status_clean', lambda s: (s == 'RTO').mean())
    ).sort_values('orders', ascending=False)
    print(courier_summary)

    # 9. UTM Source (Acquisition Channel)
    print("\n--- Acquisition Source Analysis ---")
    utm_summary = completed.groupby('utm_source').agg(
        orders=('order_id', 'count'),
        rto_count=('status_clean', lambda s: (s == 'RTO').sum()),
        rto_rate=('status_clean', lambda s: (s == 'RTO').mean())
    ).sort_values('orders', ascending=False)
    print(utm_summary)

    # 10. Order Value Bins
    completed['value_bin'] = pd.cut(
        completed['order_value'],
        bins=[-1, 499, 999, 1499, 2499, 10000],
        labels=['<= ₹499', '₹500-₹999', '₹1000-₹1499', '₹1500-₹2499', '₹2500+']
    )
    print("\n--- Order Value Tier Analysis ---")
    val_summary = completed.groupby('value_bin', observed=False).agg(
        orders=('order_id', 'count'),
        rto_count=('status_clean', lambda s: (s == 'RTO').sum()),
        rto_rate=('status_clean', lambda s: (s == 'RTO').mean())
    )
    print(val_summary)

    # 11. State / City analysis
    print("\n--- Top Cities Performance ---")
    city_summary = completed.groupby('city').agg(
        orders=('order_id', 'count'),
        rto_rate=('status_clean', lambda s: (s == 'RTO').mean())
    ).sort_values('orders', ascending=False)
    print(city_summary.head(15))

    # 12. In-transit record inspection
    in_transit = df[df['status_clean'] == 'IN_TRANSIT']
    print("\n--- In-Transit Records ---")
    print(in_transit[['order_id', 'order_datetime', 'customer_name', 'phone', 'city', 'state', 'order_value']])

if __name__ == '__main__':
    analyze_raw_dataset()
