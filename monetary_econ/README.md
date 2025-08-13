# ECB Key Interest Rates Visualization Generator

This Python script fetches the latest ECB key interest rates and reference rates from the ECB Statistical Data Warehouse and generates an interactive visualization using Plotly.

## Requirements

- Python 3.6+
- Required packages: `ecbdata`, `pandas`, `plotly`

Install the required packages using:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with default parameters:

```bash
python generate_visualization.py
```

This will generate the visualization at `static/html/ecb_rates.html` with data starting from January 1999.

### Optional Arguments

- `--start-date`: Start date in YYYY-MM format (default: 1999-01)
- `--output`: Output HTML file path (default: static/html/ecb_rates.html)

Example with custom parameters:

```bash
python generate_visualization.py --start-date 2010-01 --output custom_output.html
```

## Integration with Hugo Website

To update the visualization on your website:

1. Run the script to generate a new HTML file
2. The HTML file will include the latest rates data
3. Commit and deploy your website

For automatic updates, consider setting up a GitHub Action or a cron job that:
1. Runs the script periodically
2. Commits and pushes any changes to your repository

## Data Source

All data is fetched directly from the ECB Statistical Data Warehouse using the following series keys:

- MRO (Fixed Rate): FM.D.U2.EUR.4F.KR.MRR_FR.LEV
- MRO (Variable Rate): FM.D.U2.EUR.4F.KR.MRR_MBR.LEV
- DFR: FM.D.U2.EUR.4F.KR.DFR.LEV
- MLF: FM.D.U2.EUR.4F.KR.MLFR.LEV
- EONIA: EON.D.EONIA_TO.RATE
- €STR: EST.B.EU000A2X2A25.WT 