import sqlalchemy
from sqlalchemy import types
import pandas as pd


def main():
    try:
        path = "~/goinfre/subject/customer/data_2022_oct.csv"
        name = path.split(".")[-2].split("/")[-1]
        data = pd.read_csv(path)
        engine = sqlalchemy.create_engine("postgresql+psycopg2://mprokosc:mysecretpassword@localhost:5432/piscineds")
        sql_types = {
            "event_time": types.DateTime(timezone=True),
            "event_type": types.String(length=50),
            "product_id": types.Integer(),
            "price": types.Numeric(10, 2),
            "user_id": types.BigInteger(),
            "user_session": types.UUID()
            }
        
        data.to_sql(name, engine, if_exists="replace", index=False, dtype=sql_types)
    
    except (Exception, KeyboardInterrupt) as e:
        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()