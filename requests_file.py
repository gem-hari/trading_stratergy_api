import requests


def send_request_to_api():
    url = "http://127.0.0.1:5000/trading_stratergy/"

    payload = {
        "training_period": ["2024-10-01", "2024-09-30"],
        "testing_period": ["2024-10-31", "2024-11-15"]
    }

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            with open("output_periods.xlsx", "wb") as f:
                f.write(response.content)
            print("Excel file successfully downloaded as 'output_periods.xlsx'.")
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    send_request_to_api()
