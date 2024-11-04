import pandas as pd
import requests

ACCESS_TOKEN = "Your Token"
MARGIN_API_URL = "https://api.upstox.com/v2/charges/margin"

def calculate_margin_and_premium(df):
    results = []
    for _, row in df.iterrows():
        try:
            bid_ask = row.get("bid/ask", 0)
            lot_size = row.get("lot_size", 0)
            side = row.get("side", "UNKNOWN")

            if bid_ask <= 0 or lot_size <= 0:
                print(f"Invalid bid/ask ({bid_ask}) or lot size ({lot_size}) for row: {row}")
                premium = 0
            else:
                premium = bid_ask * lot_size

            margin_data = {
                "instruments": [
                    {
                        "instrument_key": row["instrument_name"], 
                        "quantity": lot_size,
                        "transaction_type": "SELL" if side == "CE" else "BUY",
                        "product": "I"
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            response = requests.post(MARGIN_API_URL, headers=headers, json=margin_data)
            if response.status_code == 200:
                margin_info = response.json().get("data", {}).get("margins", [{}])[0]
                total_margin = margin_info.get("total_margin", 0)
            else:
                print(f"Failed to retrieve margin data: {response.status_code}, {response.text}")
                total_margin = 0

            results.append({
                "instrument_name": row["instrument_name"],
                "strike_price": row["strike_price"],
                "side": side,
                "premium": premium,
                "total_margin": total_margin
            })
        except KeyError as e:
            print(f"Error processing row: {e}")

    return pd.DataFrame(results)

def main():
    options_data = pd.read_csv("options_data.csv")
    
    result_data = calculate_margin_and_premium(options_data)
    
    result_data.to_csv("Margin_Premium_Results.csv", index=False)
    print("Margin and premium data saved to Margin_Premium_Results.csv")

if __name__ == "__main__":
    main()
