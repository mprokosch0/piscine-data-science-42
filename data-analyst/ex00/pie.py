import matplotlib.pyplot as plt
import sqlalchemy


def main():
    try:
        engine = sqlalchemy.create_engine("postgresql+psycopg2://mprokosc:mysecretpassword@localhost:5432/piscineds")
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=engine)
        table = metadata.tables["customers"]
        with engine.connect() as conn:
            table = conn.execute(sqlalchemy.text("""SELECT event_type, count(*)
                                                    FROM customers group by event_type
                                                    ORDER BY count desc""")).fetchall()
            nums = [y for x, y in table]
            names = [x for x, y in table]
            plt.pie(nums, labels=names, autopct='%1.1f%%',)
            plt.show()
    except Exception as e:
        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()