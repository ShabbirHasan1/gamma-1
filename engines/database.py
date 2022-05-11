#%%
from sqlalchemy import create_engine
import psycopg2
import yfinance as yf
import pandas as pd

# %%

PASSWORD = "freakyn00b"
engine = create_engine(f'postgresql://postgres:{PASSWORD}@localhost/tickdata')
tick_path = 'data/tick'
scrips_path = 'data/scrips'

# %%
scrip = "RELIANCE.NS"
ticker = yf.Ticker(scrip)
data = ticker.history(period="max")
data = data.reset_index()
data['symbol'] = scrip
data['date'] = data['Date'].map(lambda x: x.strftime('%d-%m-%Y'))
data.drop(['Date'], inplace=True, axis=1)

#%%
data.to_sql('daily_prices', engine, if_exists='replace', index=False)

query = """ALTER TABLE daily_prices
            ADD PRIMARY KEY (Date, symbol);"""
engine.execute(query)
# %%
