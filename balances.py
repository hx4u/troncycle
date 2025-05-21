import argparse

from tradeogre import TradeOgre  # Save your class as tradeogre_api.py



def main():

    parser = argparse.ArgumentParser(description="Check TradeOgre account balances")

    parser.add_argument("-k", "--keyfile", help="Path to API key file (key and secret on separate lines)", required=True)



    args = parser.parse_args()



    # Initialize TradeOgre and load API keys

    to = TradeOgre()

    to.load_key(args.keyfile)



    try:

        balances = to.balances()

    except Exception as e:

        print(f"[!] Failed to retrieve balances: {e}")

        return



    if not balances:

        print("[-] No balances found.")

        return



    print("[+] Balances:")
    for currency, info in balances.items():
        if currency == "success":
            continue
        if not isinstance(info, dict):
            continue
        total = info.get("balance", "0")
        available = info.get("available", "0")
        print(f"  {currency}: Total = {total}, Available = {available}")




if __name__ == "__main__":

    main()

