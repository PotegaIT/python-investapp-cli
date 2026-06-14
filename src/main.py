# Import functions for ETF database management and portfolio analysis
from etf_db import initialize_database, add_etf, edit_etf, delete_etf, update_data
from analyze import analyze_portfolio, show_rsi_for_portfolio, show_correlation_matrix, show_sma_for_portfolio
import os
from chart.app import show_chart
import pandas as pd
from datetime import datetime

# Main application loop - user menu
if __name__ == "__main__":
    # Initialize ETF database on first run
    initialize_database()
    # Clear screen before showing the menu
    os.system('clear')
    print("=" * 80)
    print("INVESTAPP - Welcome! - author: Greg Potega")
    while True:
        # Display main menu
        print("\n" + "=" * 80)
        print("--- PORTFOLIO MANAGEMENT ---")
        print("1. Add new instrument")
        print("2. Edit instrument")
        print("3. Delete instrument")
        print("4. Update prices and quantities")

        print("\n--- ANALYSIS AND REPORTS ---")
        print("5. Analyze (Purchase report)")
        print("6. Correlation matrix")
        print("7. SMA 50/200")

        print("\n--- CHARTS AND TECH ---")
        print("8. Technical analysis (StockStats)")
        print("9. Technical chart")

        print("\n0. Exit")

        print("-" * 80)
        # Get user choice
        choice = input("\nSelect an option: ")
        # Call appropriate function based on user choice
        if choice == '1':
            add_etf()
        elif choice == '2':
            edit_etf()
        elif choice == '3':
            delete_etf()
        elif choice == '4':
            update_data()
        elif choice == '5':
            analyze_portfolio()
        elif choice == '6':
            show_correlation_matrix()
        elif choice == '7':
            show_sma_for_portfolio()
        elif choice == '8':
            show_rsi_for_portfolio()
        elif choice == '9':
            df = pd.read_csv('moje_etf.csv')
            for idx, row in df.iterrows():
                print(f"{idx}. {row['Name']} ({row['Ticker']})")
            try:
                idx = int(input("Enter instrument number for chart: "))
                ticker = df.iloc[idx]['Ticker']
                # Default start date: one year back from today
                default_start = (datetime.now() - pd.DateOffset(years=1)).strftime("%Y-%m-%d")
                start_date = input(f"Enter start date (YYYY-MM-DD) [default {default_start}]: ")
                if not start_date:
                    start_date = default_start
                end_date = datetime.now().strftime("%Y-%m-%d")
                show_chart(ticker, start_date, end_date)
            except Exception as e:
                print("Error:", e)
        elif choice == '0':
            break  # End program
    os.system('clear')
