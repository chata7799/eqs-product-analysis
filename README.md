# Pricing & Market Condition Tracker

## Project Overview
This repository provides a Pricing & Market Condition Tracker to help small business owners compare their product prices with market prices. It:

- Reads product data from a CSV file (`products.csv`)
- Cleans and normalizes data (fixing price formats, category names, etc.)
- Integrates with the Best Buy Product API to fetch market prices
- Generates insights about pricing competitiveness
- Produces visualizations and a detailed report

## Installation Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<yourusername>/eqs-product-analysis.git
cd eqs-product-analysis
```

### 2. Install Dependencies: 
Make sure you have Python 3.8+ installed, then run:

```bash
pip install -r requirements.txt
```

The main libraries used are:

* pandas for data manipulation
* requests for API calls
* matplotlib for visualization
* python-dotenv for environment variable management
### 3. Set Up Environment Variables:

Obtain a Best Buy Developer API key.
Create a file called .env (or set an environment variable) with your key:
```bash
BESTBUY_API_KEY=YOUR_BESTBUY_API_KEY_HERE
```
An example .env.example might look like this:
```bash
BESTBUY_API_KEY=ABC123XYZ
```
Note: Do not commit your real API key to a public repository.

## Running the Application
From the repository root, run:

```bash
python src/analysis.py data/products.csv
```
# Analysis Script Outline

`analysis.py` will be responsible for:
1. **Reading and Cleaning the CSV Data**  
   - Parse the input CSV file to remove errors and inconsistencies.
   - Handle missing or malformed data entries.
   - Output a cleaned dataset for further processing.

2. **Fetching Approximate Market Prices from the Best Buy API**  
   - Determine the product category from the cleaned data.
   - Use the Best Buy API to retrieve average market prices for those categories.
   - Store these average prices for comparison with your product data.

3. **Generating a Comparative Chart**  
   - Create a chart (`price_comparison.png`) comparing your product prices to the Best Buy average.
   - Illustrate which products are priced above or below the market average.

4. **Producing a Detailed Report**  
   - The script outputs a `report.md` file containing:
     - **Data Quality Issues** encountered and their fixes.
     - **Cleaned Data Summary** to give an overview of the final dataset.
     - **External Data Integration Results** showing how data from Best Buy was incorporated.
     - **Business Insights** such as how many products are overpriced vs. underpriced.
     - **Recommendations** for pricing strategies or further analysis.

## Viewing the Report

After running `analysis.py`, you can open or preview `report.md` in any Markdown viewer (including GitHub). The generated report will have the embedded chart (`price_comparison.png`), allowing you to visualize the comparative pricing at a glance.

# External Data Source

## Best Buy Developer API

We use the **Best Buy Product API** to retrieve a list of items matching the keyword (taken from the product’s category).

**Endpoint Example:**

```css
https://api.bestbuy.com/v1/products((search={keyword}))?apiKey=<YOUR_KEY>&format=json
```

From these product listings, we calculate an average `salePrice` as a rough “market price.”

# Insights & Calculations

## Price Difference

\[
\text{price_diff} = \text{our_price} - \text{bestbuy_market_price}
\]

We measure how far our price diverges from the approximate Best Buy price.

---

## Overpriced / Underpriced / At Market

- **Overpriced:** If `price_diff > 1.0`
- **Underpriced:** If `price_diff < -1.0`
- **At Market:** Otherwise (within a ±\$1.00 band)

---

## Visualization

We generate **price_comparison.png**, a bar chart with two bars per product:
1. **Our Price**
2. **Best Buy Average Price**

---

## Report

Summarizes key data quality issues, the average prices fetched from Best Buy, how many products fall into each pricing category, and recommendations for future action.

---

# Limitations

## API Rate Limits

Best Buy’s developer API may have rate limits. For large datasets or many repeated calls, you might hit daily quotas.

## Category Matching

We pass the product’s category as a simple keyword to Best Buy. If categories are vague (e.g., “Beverages”), we may get irrelevant products.  
For more accuracy, refine the query using product names or sub-categories.

## Data Quality

The CSV data includes various formatting issues (e.g., `$12.99`, blank rows, “out of stock” strings). We handle most of these, but there could be edge cases.

## Approximate Market Price

The Best Buy average `salePrice` may not perfectly reflect true competitor or commodity prices, especially for specialty items or when data is sparse.

## Static Snapshot

The tool runs on the CSV data and current Best Buy API data. For continuous monitoring, you’d need to schedule or re-run the script regularly.

