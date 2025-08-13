#!/usr/bin/env python3
"""
ECB Key Interest Rates Visualization Generator
This script fetches ECB key interest rates and reference rates data
and generates an interactive visualization using Plotly.
"""

from ecbdata import ecbdata
import pandas as pd
import plotly.graph_objects as go
import os
import argparse
from datetime import datetime

# Series keys for ECB rates
SERIES_KEYS = {
    'MRO (Fixed Rate)': 'FM.D.U2.EUR.4F.KR.MRR_FR.LEV',    # Main Refinancing Operations Rate (Fixed Rate)
    'MRO (Variable Rate)': 'FM.D.U2.EUR.4F.KR.MRR_MBR.LEV',  # Main Refinancing Operations Rate (Variable Rate)
    'DFR': 'FM.D.U2.EUR.4F.KR.DFR.LEV',       # Deposit Facility Rate
    'MLF': 'FM.D.U2.EUR.4F.KR.MLFR.LEV',      # Marginal Lending Facility Rate
    'EONIA': 'EON.D.EONIA_TO.RATE',           # EONIA Rate (discontinued)
    '€STR': 'EST.B.EU000A2X2A25.WT'           # Euro Short-Term Rate
}

def fetch_ecb_rates(start_date='1999-01'):
    """
    Fetches ECB key interest rates and reference rates at daily frequency.
    Combines MRO Fixed and Variable Rates into a single 'MRO' series.
    
    Args:
        start_date (str): Start date in YYYY-MM format
        
    Returns:
        pandas.DataFrame: DataFrame with rates data
    """
    rates_data = {}
    
    # Fetch each rate series
    for rate_name, series_key in SERIES_KEYS.items():
        try:
            df = ecbdata.get_series(series_key, start=start_date)
            # Convert TIME_PERIOD to datetime and set as index (if present)
            if 'TIME_PERIOD' in df.columns:
                df['TIME_PERIOD'] = pd.to_datetime(df['TIME_PERIOD'])
                df = df.set_index('TIME_PERIOD')
            else:
                df.index = pd.to_datetime(df.index)
            rates_data[rate_name] = df['OBS_VALUE']
        except Exception as e:
            print(f"Error fetching {rate_name}: {e}")
    
    # Combine all rates into a single DataFrame
    combined_rates = pd.DataFrame(rates_data)
    
    # Combine the two MRO series (Fixed & Variable) by taking their mean
    if 'MRO (Fixed Rate)' in combined_rates.columns and 'MRO (Variable Rate)' in combined_rates.columns:
        combined_rates['MRO'] = combined_rates[['MRO (Fixed Rate)', 'MRO (Variable Rate)']].mean(axis=1)
        combined_rates.drop(columns=['MRO (Fixed Rate)', 'MRO (Variable Rate)'], inplace=True)
    
    return combined_rates

def create_interactive_plot(rates_df=None, output_path='static/html/ecb_rates.html'):
    """
    Creates an interactive plot of the ECB rates and saves it as HTML.
    
    Args:
        rates_df (pandas.DataFrame, optional): DataFrame with rates data
        output_path (str): Path where to save the HTML file
    """
    # If no data provided, fetch from ECB
    if rates_df is None:
        try:
            rates_df = fetch_ecb_rates()
        except Exception as e:
            print(f"Error fetching ECB rates: {e}")
            return
    
    fig = go.Figure()
    
    # Plot policy rates with solid lines
    policy_rates = ['MRO', 'DFR', 'MLF']
    for rate in policy_rates:
        if rate in rates_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=rates_df.index,
                    y=rates_df[rate],
                    name=rate,
                    line=dict(width=2),
                    hovertemplate="%{x|%Y-%m-%d}<br>" +
                                f"{rate}: %{{y:.3f}}%<br>" +
                                "<extra></extra>"
                )
            )
    
    # Plot reference rates with dashed lines
    reference_rates = {'€STR': 'rgba(240,128,128,0.8)', 'EONIA': 'rgba(176,196,222,0.8)'}
    for rate, color in reference_rates.items():
        if rate in rates_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=rates_df.index,
                    y=rates_df[rate],
                    name=rate,
                    line=dict(width=2, dash='dash', color=color),
                    hovertemplate="%{x|%Y-%m-%d}<br>" +
                                f"{rate}: %{{y:.3f}}%<br>" +
                                "<extra></extra>"
                )
            )
    
    # Update layout
    fig.update_layout(
        title='ECB Key Interest Rates and Reference Rates',
        xaxis_title='Date',
        yaxis_title='Rate (%)',
        hovermode='x unified',
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # Get the latest rates and last available values
    latest_rates = rates_df.iloc[-1]
    
    # For €STR and EONIA, get last available (non-NaN) observations and their dates
    estr_series = rates_df['€STR'].dropna() if '€STR' in rates_df.columns else pd.Series()
    eonia_series = rates_df['EONIA'].dropna() if 'EONIA' in rates_df.columns else pd.Series()
    
    # Create info section
    rates_info = "<div style='font-family: Arial, sans-serif; padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 20px;'>"
    rates_info += "<h3>Latest Available Rates:</h3>"
    rates_info += "<ul>"
    
    # Add policy rates
    for rate_name in ['MRO', 'DFR', 'MLF']:
        if rate_name in latest_rates.index:
            value = latest_rates.get(rate_name, None)
            if pd.notna(value):
                rates_info += f"<li><strong>{rate_name}:</strong> {value:.3f}%</li>"
    
    # Add €STR and EONIA information
    if not estr_series.empty:
        last_estr = estr_series.iloc[-1]
        last_estr_date = estr_series.index[-1]
        rates_info += f"<li><strong>€STR:</strong> {last_estr:.3f}% (as of {last_estr_date.strftime('%Y-%m-%d')})</li>"
        
    if not eonia_series.empty:
        last_eonia = eonia_series.iloc[-1]
        last_eonia_date = eonia_series.index[-1]
        rates_info += f"<li><strong>EONIA:</strong> {last_eonia:.3f}% (discontinued on {last_eonia_date.strftime('%Y-%m-%d')})</li>"
    
    rates_info += "</ul>"
    
    # Add last updated timestamp
    rates_info += f"<p><em>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>"
    rates_info += "</div>"
    
    # Save both the info and the figure to an HTML file
    html_content = rates_info + fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write the HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"ECB rates visualization has been saved to {output_path}")
    return output_path

def main():
    """Main function to parse arguments and generate the visualization."""
    parser = argparse.ArgumentParser(description='Generate ECB rates visualization')
    parser.add_argument('--start-date', type=str, default='1999-01',
                      help='Start date in YYYY-MM format (default: 1999-01)')
    parser.add_argument('--output', type=str, default='static/html/ecb_rates.html',
                      help='Output HTML file path (default: static/html/ecb_rates.html)')
    
    args = parser.parse_args()
    
    try:
        rates = fetch_ecb_rates(start_date=args.start_date)
        create_interactive_plot(rates, output_path=args.output)
    except Exception as e:
        print(f"Error generating visualization: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 