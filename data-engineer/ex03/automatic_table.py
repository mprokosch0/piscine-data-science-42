import sqlalchemy
from sqlalchemy import types
import pandas as pd
import os
import csv
import io


def psql_copy(table: pd.io.sql.SQLTable, conn: sqlalchemy.engine.Connection, keys: list[str], data_iter) -> None:
    with conn.connection.cursor() as cur:
        buf = io.StringIO()
        csv.writer(buf).writerows(data_iter)
        buf.seek(0)

        table_name = f'"{table.name}"'
        cols = ", ".join(f'"{k}"' for k in keys)
        cur.copy_expert(f"COPY {table_name} ({cols}) FROM STDIN WITH CSV", buf)


def main():
    try:
        path = os.path.expanduser("~/goinfre/subject/customer/")
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        engine = sqlalchemy.create_engine("postgresql+psycopg2://mprokosc:mysecretpassword@localhost:5432/piscineds")
        sql_types = {
                        "event_time": types.DateTime(timezone=True),
                        "event_type": types.String(length=50),
                        "product_id": types.Integer(),
                        "price": types.Numeric(10, 2),
                        "user_id": types.BigInteger(),
                        "user_session": types.UUID()
                        }
        
        for file in files:
            name = file.split(".")[-2]
            cols = pd.read_csv(os.path.join(path, file), nrows=0)
            print("Creating table:", name, "...")
            cols.to_sql(name, engine, if_exists="replace", index=False, dtype=sql_types)
            print("Table created !")
            print("Filling", name, "table ...")
            fdata = pd.read_csv(os.path.join(path, file))
            fdata.to_sql(name, engine, if_exists="append", index=False, method=psql_copy)
            print("Table filled !")
    
    except (Exception, KeyboardInterrupt) as e:
        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()