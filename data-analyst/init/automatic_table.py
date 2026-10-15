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


def join_tables(engine: sqlalchemy.Engine):
    with engine.connect() as connection:
        print("Joining tables ...")
        connection.execute(sqlalchemy.text(
                """CREATE TABLE customers AS
                SELECT * FROM data_2022_oct
                UNION ALL
                SELECT * FROM data_2022_nov
                UNION ALL
                SELECT * FROM data_2022_dec
                UNION ALL
                SELECT * FROM data_2023_jan
                UNION ALL
                SELECT * FROM data_2023_feb"""))
        connection.commit()
        print("Tables joined !")


def rm_dupl(engine: sqlalchemy.Engine):
    with engine.connect() as connection:
        print("Deleting duplicates ...")
        connection.execute(sqlalchemy.text(
            """DELETE FROM customers
                WHERE ctid IN (
                    SELECT ctid
                    FROM (
                        SELECT ctid,
                            event_time - LAG(event_time) OVER (
                                PARTITION BY event_type, product_id, price, user_id, user_session
                                ORDER BY event_time
                            ) AS ecart
                        FROM customers
                    ) dupl
                    WHERE ecart <= INTERVAL '1 second'
                )"""))
        connection.commit()
        print("Duplicates deleted !")


def remove_item_dupl(engine: sqlalchemy.Engine):
    with engine.connect() as connection:
        print("Deleting duplicates ...")
        connection.execute(sqlalchemy.text(
            """CREATE TABLE clean_item AS
                SELECT *
                FROM (
                SELECT *,
                        ROW_NUMBER() OVER (
                        PARTITION BY product_id
                        ORDER BY (CASE WHEN category_id   IS NOT NULL THEN 1 ELSE 0 END
                                + CASE WHEN category_code IS NOT NULL THEN 1 ELSE 0 END
                                + CASE WHEN brand         IS NOT NULL THEN 1 ELSE 0 END) DESC,
                                    category_id
                        ) AS rn
                FROM item
                ) t
                WHERE rn = 1;
                """))
        connection.execute(sqlalchemy.text("""ALTER TABLE clean_item DROP COLUMN rn"""))
        connection.execute(sqlalchemy.text("""DROP TABLE item"""))
        connection.execute(sqlalchemy.text("""ALTER TABLE clean_item RENAME TO item"""))
        connection.commit()
        print("Duplicates deleted !")


def import_item(engine: sqlalchemy.Engine):
    path = "~/goinfre/subject/item/item.csv"
    name = path.split(".")[-2].split("/")[-1]
    data = pd.read_csv(path)
    print("Creating and filling table:", name, "...")
    data.to_sql(name, engine, index=False, if_exists="replace", method=psql_copy)
    print("Table done !")
    remove_item_dupl(engine)


def fuse_tables(engine: sqlalchemy.Engine):
    with engine.connect() as connection:
        print("Fusing customers and items ...")
        connection.execute(sqlalchemy.text(
            """CREATE TABLE tmp_fused AS
                SELECT c.event_time, c.event_type, c.product_id,
                        i.category_id, i.category_code, i.brand,
                        c.price, c.user_id, c.user_session
            FROM customers c LEFT JOIN item i ON c.product_id = i.product_id;"""))
        connection.execute(sqlalchemy.text("""DROP TABLE customers"""))
        connection.execute(sqlalchemy.text("""ALTER TABLE tmp_fused RENAME TO customers"""))
        connection.commit()
        print("Tables fused !")


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
        join_tables(engine)
        rm_dupl(engine)
        import_item(engine)
        fuse_tables(engine)
    
    except (Exception, KeyboardInterrupt) as e:
        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()