import streamlit as st
import pandas as pd
import numpy as np
import requests

# Function to fetch data from Financial Modelling Prep
def fetch_data(tickers, api_key):
    prices = {}
    dates = None
    for ticker in tickers:
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={api_key}"
        response = requests.get(url)
        data = response.json()
        
        if dates is None:
            # Reverse the list of dates to have the oldest date first
            dates = [day['date'] for day in data['historical'][::-1]]
        
        # Reverse the list of closing prices to match the reversed dates
        prices[ticker] = [day['close'] for day in data['historical'][::-1]]
    
    # Create a DataFrame with dates as the index
    prices_df = pd.DataFrame(prices, index=dates)
    prices_df.index.name = 'Date'
    # Convert the index to datetime
    prices_df.index = pd.to_datetime(prices_df.index)
    prices_df = prices_df.resample('M').last()
    
    # It's not necessary to reverse the DataFrame here since we've already inverted the lists
    return prices_df


# Function to calculate marginal contributions
def calculate_marginal_contributions(allocation, returns):


    # Calculate the covariance matrix of the returns
    cov_matrix = returns.cov()

    # Calculate the portfolio standard deviation
    weights = allocation / allocation.sum()
    # make the index of the weights match the index of the covariance matrix    
    weights.index = cov_matrix.index

    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    portfolio_std_dev = np.sqrt(portfolio_variance)
    print(cov_matrix)
    print(portfolio_std_dev)

    # Calculate the MCTR for each asset
    mctr = {}
    for i in returns.columns:
        asset_covariances = cov_matrix[i]
 
        asset_mctr = (weights * asset_covariances).sum() / portfolio_std_dev

        mctr[i] = asset_mctr
    return pd.Series(mctr), portfolio_std_dev, weights


# Main app
def main():
    st.title("Portfolio Analysis Tool")

    api_key = st.sidebar.text_input("API Key")
    uploaded_file = st.sidebar.file_uploader("Upload your portfolio file", type=['xlsx'])

    if uploaded_file is not None:
        portfolio_df = pd.read_excel(uploaded_file)
    else:
        # Dummy portfolio with 20 stocks
        tickers = stocks = [
    "CRM",  # Technology Services
    "PODD", # Health Technology
    "NVDA", # Electronic Technology
    "AMZN", # Retail Trade
    "DIS",  # Consumer Services
    "WELL", # Finance
    "TSN",  # Consumer Non-Durables
    "PWR",  # Industrial Services
    "DUK",  # Utilities
    "SPGI", # Commercial Services
    "TSLA", # Consumer Durables
    "ECL",  # Process Industries
    "AOS",  # Producer Manufacturing
    "LUV",  # Transportation
    "IQV",  # Health Services
    "CAH",  # Distribution Services
    "VMC",  # Non-Energy Minerals
    "CVX",  # Energy Minerals
    "VZ",   # Communication Services
    "TLT"   # Real Estate
]

        portfolio_df = pd.DataFrame({
            'Ticker': tickers,
            'Allocation': np.random.random(20)
        })
        portfolio_df['Allocation'] /= portfolio_df['Allocation'].sum()  # Normalize allocations

    if api_key:
        st.write("Fetching data...")
        ticker_list = portfolio_df['Ticker'].tolist()
        data = fetch_data(ticker_list, api_key)
        st.write("Data fetched successfully")

        # Calculate returns
        returns = data.pct_change().dropna()
  
        # Calculate marginal contributions
        marginal_risks, portfolio_std_dev, weights = calculate_marginal_contributions(portfolio_df['Allocation'], returns)

        # Display results
        #st.subheader("Marginal Contributions to Return")
        #st.write(marginal_returns)

        st.subheader("Marginal Contributions to Risk")
        st.write(marginal_risks)
        st.write("Note: The sum of the marginal contributions to risk should be equal to the portfolio's standard deviation.")
        st.write("The sum of the marginal contributions to risk is:", (weights* marginal_risks).sum())
        st.write("The portfolio's standard deviation is:", portfolio_std_dev)
    else:
        st.write("Please enter your API key to fetch data.")

if __name__ == "__main__":
    main()
