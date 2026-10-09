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


def remove_dupl(engine: sqlalchemy.Engine):
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
    remove_dupl(engine)


def main():
    try:
        engine = sqlalchemy.create_engine("postgresql+psycopg2://mprokosc:mysecretpassword@localhost:5432/piscineds")
        import_item(engine)
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
    
    except (Exception, KeyboardInterrupt) as e:
            print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()