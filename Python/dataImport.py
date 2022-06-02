import pandas as pd
from sodapy import Socrata
from sqlalchemy import create_engine
# Login information
client = Socrata(
    "data.kingcounty.gov",
    '6vKdIfeAzo3N19KoosZ6YawoQ',
    username='marcrng@outlook.com',
    password='KaiserKing0413$'
)
# Enpoint request for inspection data
results = client.get("f29f-zza5", limit='1000000')
# Convert the records into Pandas dataframe
results_df = pd.DataFrame.from_records(results)
# Connect to local Mysql database
my_conn = create_engine("mysql+mysqldb://marcrng:Kaisersql0413$@localhost/inspection_data")
# Export dataframe to mysql database
results_df.to_sql(con=my_conn, name='records', if_exists='append', index=False)
