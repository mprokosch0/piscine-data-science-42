import sqlalchemy
import pandas as pd

def main():
    try:
        engine = sqlalchemy.create_engine("postgresql+psycopg2://mprokosc:mysecretpassword@localhost:5432/piscineds")
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
    
    except (Exception, KeyboardInterrupt) as e:
            print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()