import pandas as pd
import sqlite3

# connect to database
conn = sqlite3.connect("f1.db")

# helper function
def load_csv(file_name, table_name):
    df = pd.read_csv(file_name)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Loaded {table_name} successfully")

# load all tables
load_csv("drivers.csv", "drivers")
load_csv("constructors.csv", "constructors")
load_csv("circuits.csv", "circuits")
load_csv("races.csv", "races")
load_csv("results.csv", "results")
load_csv("qualifying.csv", "qualifying")
load_csv("pit_stops.csv", "pit_stops")

conn.close()

print("All data loaded into f1.db")
