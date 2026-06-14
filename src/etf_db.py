import pandas as pd
import os

DATA_FILE = 'my_etf.csv'

def initialize_database():
    if not os.path.exists(DATA_FILE):
        initial_data = [
            {'Ticker': 'CSPX.L', 'Name': 'S&P 500 (Acc)', 'Target_%': 0.30, 'Units': 10, 'Currency': 'USD', 'Last_Price': 734.64},
            {'Ticker': 'NQSE.DE', 'Name': 'Nasdaq 100', 'Target_%': 0.05, 'Units': 100, 'Currency': 'EUR', 'Last_Price': 16.83},
            {'Ticker': 'IUSN.DE', 'Name': 'World Small Cap', 'Target_%': 0.15, 'Units': 461, 'Currency': 'EUR', 'Last_Price': 9.08},
            {'Ticker': 'VHVG.DE', 'Name': 'Developed World', 'Target_%': 0.25, 'Units': 48, 'Currency': 'USD', 'Last_Price': 133.96},
            {'Ticker': 'EIMI.L', 'Name': 'Emerging Markets', 'Target_%': 0.15, 'Units': 102, 'Currency': 'USD', 'Last_Price': 44.40},
            {'Ticker': 'AGGG.L', 'Name': 'Global Bonds (Dist)', 'Target_%': 0.10, 'Units': 477, 'Currency': 'USD', 'Last_Price': 4.44}
        ]
        pd.DataFrame(initial_data).to_csv(DATA_FILE, index=False)

def add_etf():
    df = pd.read_csv(DATA_FILE)
    print("\n--- ADD NEW ETF ---")
    ticker = input("Enter ticker: ")
    name = input("Enter name: ")
    target_inp = input("Enter target % (e.g., 0.05 or 5): ").replace(',', '.')
    val = float(target_inp)
    if val > 1:
        val = val / 100
    target = val

    units = float(input("Enter number of units: ").replace(',', '.'))
    currency = input("Enter currency (USD/EUR): ").upper()
    price = float(input(f"Enter current price in {currency}: ").replace(',', '.'))
    new_row = {'Ticker': ticker, 'Name': name, 'Target_%': target, 'Units': units, 'Currency': currency, 'Last_Price': price}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    print("\n" + "=" * 100)
    print("\nADDED SUCCESSFULLY!")
    from pl.analyze import check_balance
    check_balance(df)

def edit_etf():
    df = pd.read_csv(DATA_FILE)
    if df.empty:
        return
    print("\n--- EDIT ETF PARAMETERS ---")
    for idx, row in df.iterrows():
        print(f"{idx}. {row['Name']} (Target: {row['Target_%'] * 100:.2f}%)")
    try:
        selection = int(input("\nSelect item number to edit: "))
        print("Press Enter to keep current value.")
        n_name = input(f"Name [{df.at[selection, 'Name']}]: ")
        if n_name:
            df.at[selection, 'Name'] = n_name
        n_target = input(f"Target % [{df.at[selection, 'Target_%'] * 100:.2f}%]: ")
        if n_target:
            val = float(n_target.replace(',', '.'))
            if val > 1:
                val = val / 100
            df.at[selection, 'Target_%'] = val
        n_ticker = input(f"Ticker [{df.at[selection, 'Ticker']}]: ")
        if n_ticker:
            df.at[selection, 'Ticker'] = n_ticker
        n_curr = input(f"Currency [{df.at[selection, 'Currency']}]: ")
        if n_curr:
            df.at[selection, 'Currency'] = n_curr.upper()
        df.to_csv(DATA_FILE, index=False)
        print("\n" + "=" * 100)
        print("\nCHANGES SAVED!")
        from pl.analyze import check_balance
        check_balance(df)
    except:
        print("\n" + "=" * 100)
        print("Edit error.")

def delete_etf():
    df = pd.read_csv(DATA_FILE)
    if df.empty:
        return
    print("\n--- DELETE ETF ---")
    for idx, row in df.iterrows():
        print(f"{idx}. {row['Name']}")
    try:
        selection = int(input("Enter number to delete: "))
        if selection < 0 or selection >= len(df):
            print("Invalid number.")
            return
        etf_name = df.iloc[selection]['Name']
        etf_ticker = df.iloc[selection]['Ticker']
        confirm = input(f"Are you sure you want to delete ETF '{etf_name}' ({etf_ticker})? [y/N]: ").strip().lower()
        if confirm == 'y':
            df = df.drop(df.index[selection])
            df.to_csv(DATA_FILE, index=False)
            print("\n" + "=" * 100)
            print("\nETF DELETED!")
            from pl.analyze import check_balance
            check_balance(df)
        else:
            print("Deletion canceled.")
    except:
        print("Error.")

def update_data():
    df = pd.read_csv(DATA_FILE)
    if df.empty:
        print("No ETFs found in the database.")
        return

    print("\n1. Update all instruments")
    print("2. Update selected instrument")
    selection = input("Select option: ")

    if selection == '1':
        for i, row in df.iterrows():
            print(f"\n>>> {row['Name']}")
            u_inp = input(f"    Units [{row['Units']}]: ")
            if u_inp:
                df.at[i, 'Units'] = float(u_inp.replace(',', '.'))
            p_inp = input(f"    Price ({row['Currency']}) [{row['Last_Price']}]: ")
            if p_inp:
                df.at[i, 'Last_Price'] = float(p_inp.replace(',', '.'))
        df.to_csv(DATA_FILE, index=False)
        print("\n" + "=" * 100)
        print("\nALL INSTRUMENTS UPDATED.")
    elif selection == '2':
        for idx, row in df.iterrows():
            print(f"{idx}. {row['Name']} ({row['Ticker']})")
        try:
            idx = int(input("Enter instrument number to update: "))
            if idx < 0 or idx >= len(df):
                print("Invalid number.")
                return
            print(f"\n>>> {df.at[idx, 'Name']}")
            u_inp = input(f"    Units [{df.at[idx, 'Units']}]: ")
            if u_inp:
                df.at[idx, 'Units'] = float(u_inp.replace(',', '.'))
            p_inp = input(f"    Price ({df.at[idx, 'Currency']}) [{df.at[idx, 'Last_Price']}]: ")
            if p_inp:
                df.at[idx, 'Last_Price'] = float(p_inp.replace(',', '.'))
            df.to_csv(DATA_FILE, index=False)
            print("\n" + "=" * 100)
            print("\nSELECTED INSTRUMENT UPDATED.")
        except Exception as e:
            print("\n" + "=" * 100)
            print("\nUPDATE ERROR.", e)
    else:
        print("\n" + "=" * 100)
        print("\nINVALID CHOICE.")