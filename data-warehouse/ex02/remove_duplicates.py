import sqlalchemy
import pandas as pd

def main():
    try:
        engine = sqlalchemy.create_engine("postgresql+psycopg2://mprokosc:mysecretpassword@localhost:5432/piscineds")
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
    
    except (Exception, KeyboardInterrupt) as e:
            print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()