import pandas as pd
import sqlalchemy
from pathlib import Path


def main():
    try:
        path = Path("~/goinfre/customers.csv").expanduser()
        name = path.stem
        engine = sqlalchemy.create_engine("postgresql+psycopg2://mprokosc:mysecretpassword@localhost:5432/piscineds")
        sql_types = {
                    "event_time": sqlalchemy.types.DateTime(timezone=True),
                    "event_type": sqlalchemy.types.String(length=50),
                    "product_id": sqlalchemy.types.Integer(),
                    "price": sqlalchemy.types.Numeric(10, 2),
                    "user_id": sqlalchemy.types.BigInteger(),
                    "user_session": sqlalchemy.types.UUID(),
                    "category_code": sqlalchemy.types.Text()
                }
        print("Creating table:", name, "...")
        sample = pd.read_csv(path, nrows=100_000)
        sample.head(0).to_sql(name, engine, index=False, if_exists="replace", dtype=sql_types)

        print("Filling table:", name, "...")
        raw = engine.raw_connection()
        try:
            with raw.cursor() as cur, open(path, encoding="utf-8") as f:
                cur.copy_expert(f'COPY "{name}" FROM STDIN WITH CSV HEADER', f)
            raw.commit()
        except BaseException:
            raw.rollback()
            raise
        finally:
            raw.close()

        print("Table done !")
    except (Exception, KeyboardInterrupt) as e:
        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()