import sqlalchemy
import pandas as pd
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
        path = "~/goinfre/subject/item/item.csv"
        name = path.split(".")[-2].split("/")[-1]
        data = pd.read_csv(path)
        engine = sqlalchemy.create_engine("postgresql+psycopg2://mprokosc:mysecretpassword@localhost:5432/piscineds")
        print("Creating and filling table:", name, "...")
        data.to_sql(name, engine, index=False, if_exists="replace", method=psql_copy)
        print("Table done !")
    
    except (Exception, KeyboardInterrupt) as e:
            print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()