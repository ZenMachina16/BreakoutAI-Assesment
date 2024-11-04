import requests
import pandas as pd

ACCESS_TOKEN = "Your Token"  # Replace with your actual access token
BASE_URL = "https://api.upstox.com/v2/option/chain"

def get_option_chain():
    """Fetches options chain data, processes specific fields, and saves to CSV."""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }
    params = {
        "instrument_key": "NSE_EQ|INE465A01025",  
        "expiry_date": "2024-11-28"               
    }

    print(f"Requesting data from {BASE_URL} with params: {params}") 

    try:
        response = requests.get(BASE_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            options_data = data.get("data", [])
            results = []
            
            for option in options_data:
                strike_price = option.get("strike_price")
                instrument_name = option.get("underlying_key")

                if "call_options" in option:
                    call_data = option["call_options"]["market_data"]
                    lot_size = call_data.get("oi", 0)  

                    if lot_size > 0: 
                        results.append({
                            "instrument_name": instrument_name,
                            "strike_price": strike_price,
                            "side": "CE",
                            "bid/ask": call_data.get("ask_price"),
                            "lot_size": lot_size
                        })

                if "put_options" in option:
                    put_data = option["put_options"]["market_data"]
                    lot_size = put_data.get("oi", 0)  

                    if lot_size > 0: 
                        results.append({
                            "instrument_name": instrument_name,
                            "strike_price": strike_price,
                            "side": "PE",
                            "bid/ask": put_data.get("bid_price"),
                            "lot_size": lot_size
                        })

            df = pd.DataFrame(results)
            df.to_csv("options_data.csv", index=False)
            print("Options data saved to options_data.csv")
            return df
        else:
            print("Failed to retrieve data:", data)
            return pd.DataFrame()
    except requests.RequestException as e:
        print(f"API request error: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    df = get_option_chain()
    print(df)
