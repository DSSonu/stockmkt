import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def calculate_rsi(data, window):
    delta = data['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Streamlit app configuration
st.title("Stock Price Analysis")

# Ticker input
ticker = st.text_input("Enter Stock Ticker", "AAPL")

# Date range selection
today = datetime.today()
default_start_date = today - timedelta(days=365)
start_date = st.date_input("Start Date", default_start_date)
end_date = st.date_input("End Date", today)

# Fetch stock data
if ticker:
    st.write(f"### Stock Analysis for {ticker.upper()}")

    # Download data from Yahoo Finance
    data = yf.download(ticker, start=start_date, end=end_date)

    if not data.empty:
        # Candlestick chart for the last 30 days
        st.subheader("Candlestick Chart with SMA")

        last_30_days = data[-30:]
        fig = go.Figure()

        # Add candlestick chart
        fig.add_trace(go.Candlestick(
            x=last_30_days.index,
            open=last_30_days['Open'],
            high=last_30_days['High'],
            low=last_30_days['Low'],
            close=last_30_days['Close'],
            name="Candlestick"
        ))

        # Add SMA lines
        data['SMA50'] = data['Close'].rolling(window=50).mean()
        data['SMA100'] = data['Close'].rolling(window=100).mean()

        fig.add_trace(go.Scatter(
            x=data[-30:].index, y=data['SMA50'][-30:], mode='lines', name='SMA 50',
            line=dict(color='blue')
        ))

        fig.add_trace(go.Scatter(
            x=data[-30:].index, y=data['SMA100'][-30:], mode='lines', name='SMA 100',
            line=dict(color='red')
        ))

        fig.update_layout(title="Candlestick Chart with SMA",
                          xaxis_title="Date",
                          yaxis_title="Price",
                          xaxis_rangeslider_visible=False)

        st.plotly_chart(fig)

        # Table for average return and standard deviation of return
        st.subheader("Performance Metrics for Last 90 Days")

        last_90_days = data[-90:]
        last_90_days['Return'] = last_90_days['Close'].pct_change()
        avg_return = last_90_days['Return'].mean() * 100  # Convert to percentage
        std_dev_return = last_90_days['Return'].std() * 100  # Convert to percentage

        metrics_table = pd.DataFrame({
            "Metric": ["Average Return", "Standard Deviation of Return"],
            "Value": [f"{avg_return:.2f}%", f"{std_dev_return:.2f}%"]
        })

        st.table(metrics_table)

        # RSI chart
        st.subheader("Relative Strength Index (RSI)")

        data['RSI'] = calculate_rsi(data, window=14)
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(
            x=data.index, y=data['RSI'], mode='lines', name='RSI',
            line=dict(color='green')
        ))
        rsi_fig.add_hline(y=70, line=dict(color='red', dash='dash'), name='Overbought')
        rsi_fig.add_hline(y=30, line=dict(color='blue', dash='dash'), name='Oversold')
        rsi_fig.update_layout(title="RSI Chart",
                              xaxis_title="Date",
                              yaxis_title="RSI",
                              yaxis_range=[0, 100])

        st.plotly_chart(rsi_fig)
    else:
        st.warning("No data found for the provided ticker and date range.")
else:
    st.info("Please enter a stock ticker to begin.")
