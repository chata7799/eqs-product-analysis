import sys
import pandas as pd
import matplotlib.pyplot as plt  # <-- For the chart
from utils import (
    clean_price, clean_category, clean_stock,
    fetch_external_data_bestbuy
)


def main(csv_path):
    # 1. Read CSV
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: File not found at path {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)

    data_quality_issues = []

    # 2. Check columns
    expected_cols = [
        "product_name", "our_price", "category",
        "current_stock", "restock_threshold",
        "expiration_date", "brand"
    ]
    missing_cols = [c for c in expected_cols if c not in df.columns]
    extra_cols = [c for c in df.columns if c not in expected_cols]

    if missing_cols:
        data_quality_issues.append(f"Missing columns: {missing_cols}")
    if extra_cols:
        data_quality_issues.append(f"Extra columns: {extra_cols}")

    # 3. Clean data
    if "our_price" in df.columns:
        df["our_price"] = df["our_price"].apply(clean_price)
    if "category" in df.columns:
        df["category"] = df["category"].apply(clean_category)
    if "current_stock" in df.columns:
        df["current_stock"] = df["current_stock"].apply(clean_stock)
    if "restock_threshold" in df.columns:
        df["restock_threshold"] = pd.to_numeric(df["restock_threshold"], errors="coerce")

    # Drop rows missing product_name or completely blank
    df.dropna(subset=["product_name"], how="any", inplace=True)

    # 4. Integrate with Best Buy API
    categories = df["category"].dropna().unique()
    bestbuy_prices = {}

    for cat in categories:
        avg_price = fetch_external_data_bestbuy(cat)
        bestbuy_prices[cat] = avg_price

    # Merge external prices into DataFrame
    df["bestbuy_market_price"] = df["category"].apply(lambda c: bestbuy_prices.get(c, None))

    # 5. Compare & classify
    df["price_diff"] = df["our_price"] - df["bestbuy_market_price"]

    def classify_diff(diff):
        if pd.isnull(diff):
            return "No Data"
        elif diff > 1.0:
            return "Overpriced"
        elif diff < -1.0:
            return "Underpriced"
        else:
            return "At Market"

    df["price_recommendation"] = df["price_diff"].apply(classify_diff)

    # 6. Generate a visualization
    visualize_data(df)

    # 7. Summaries
    cleaned_summary = df.describe(include="all").to_string()

    # 8. Output to report
    generate_report(df, data_quality_issues, bestbuy_prices, cleaned_summary)


def visualize_data(df):
    """
    Creates a simple bar chart of the price difference between
    our price and the Best Buy market price. Saves it to 'price_difference_chart.png'.
    """
    # Filter out rows without a valid difference
    chart_df = df.dropna(subset=["price_diff"]).copy()

    # Sort by difference so bars are in ascending order
    chart_df.sort_values("price_diff", inplace=True)

    # Create the figure
    plt.figure(figsize=(10, 6))

    # Bar chart with product names on x-axis, price_diff on y-axis
    plt.bar(chart_df["product_name"], chart_df["price_diff"], color="skyblue")

    # Add a horizontal line at 0
    plt.axhline(0, color="red", linewidth=1)

    plt.xlabel("Product Name")
    plt.ylabel("Price Difference (Our Price - Best Buy Price)")
    plt.title("Price Difference vs. Best Buy Market Price")

    # Rotate x-tick labels so they don't overlap
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig("price_difference_chart.png")
    plt.close()  # Close the figure to free memory


def generate_report(df, data_quality_issues, bestbuy_prices, cleaned_summary):
    with open("report.md", "w", encoding="utf-8") as f:
        # Data Quality
        f.write("# Data Quality Issues\n")
        if data_quality_issues:
            for issue in data_quality_issues:
                f.write(f"- {issue}\n")
        else:
            f.write("- No major data quality issues detected.\n")

        # Cleaned Data Summary
        f.write("\n## Cleaned Data Summary\n")
        f.write("```\n")
        f.write(cleaned_summary)
        f.write("\n```\n")

        # External Data
        f.write("\n## External Data Integration (Best Buy)\n")
        f.write("Approximate market prices from Best Buy for each category:\n\n")
        for cat, price in bestbuy_prices.items():
            f.write(f"- **{cat}**: ${price:.2f}\n")

        # Insights
        f.write("\n## Insights\n")
        overpriced_count = df[df["price_recommendation"] == "Overpriced"].shape[0]
        underpriced_count = df[df["price_recommendation"] == "Underpriced"].shape[0]
        at_market_count = df[df["price_recommendation"] == "At Market"].shape[0]

        f.write(f"- Overpriced items: {overpriced_count}\n")
        f.write(f"- Underpriced items: {underpriced_count}\n")
        f.write(f"- At Market: {at_market_count}\n")

        f.write("\n### Product-Level Recommendations\n")
        for idx, row in df.iterrows():
            f.write(f"- **{row['product_name']}** ({row['category']}): {row['price_recommendation']}\n")

        # Embed the saved chart
        f.write("\n## Visualization\n")
        f.write("Price difference bar chart:\n\n")
        f.write("![Price Difference Chart](price_difference_chart.png)\n\n")

        # Future Recommendations
        f.write("\n## Future Recommendations\n")
        f.write("- Investigate significant price gaps.\n")
        f.write("- Use more specific queries for better Best Buy matching.\n")
        f.write("- Expand visualizations (e.g., categories, time series).\n")

    print("Generated report.md and price_difference_chart.png")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analysis.py <path_to_csv>")
        sys.exit(1)

    csv_path = sys.argv[1]
    main(csv_path)
