import matplotlib.pyplot as plt
import matplotlib as mpl
import sqlalchemy
import datetime as dt


def fist_plot(conn: sqlalchemy.Connection):
    table = conn.execute(sqlalchemy.text("""SELECT count(*), DATE_TRUNC('day', event_time) AS month
                                            FROM customers
                                            WHERE event_type = 'purchase'
                                            GROUP BY month
                                            ORDER BY month""")).fetchall()
    date = [y for x, y in table]
    num = [x for x, y in table]
    mpl.style.use('seaborn-v0_8')
    ax = plt.subplots()[1]
    ax.plot(date, num)
    ax.set_xlim(date[0], date[-1])
    ax.set_xticks(date[::35])
    ax.set_ylabel("Number of customers")
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%b'))
    ax.grid(True)


def sec_plot(conn: sqlalchemy.Connection):
    table = conn.execute(sqlalchemy.text("""SELECT SUM(price), DATE_TRUNC('month', event_time) AS month
                                            FROM customers
                                            WHERE event_type = 'purchase'
                                            GROUP BY month
                                            ORDER BY month""")).fetchall()
    date = [y for x, y in table]
    prices = [x for x, y in table]
    mpl.style.use('seaborn-v0_8')
    ax = plt.subplots()[1]
    ax.bar(date, prices, width=25, align='center')
    ax.set_xlim(date[0] - dt.timedelta(days=20), date[-1] + dt.timedelta(days=20))
    ax.set_ylabel("Total sales in million of ₳")
    ax.set_xlabel("month")
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%b'))


def third_plot(conn: sqlalchemy.Connection):
    table = conn.execute(sqlalchemy.text("""SELECT AVG(moy) as moy, day AS day
                                            FROM (
                                                SELECT SUM(price) AS moy, user_id, DATE_TRUNC('day', event_time) AS day
                                                FROM customers
                                                WHERE event_type = 'purchase'
                                                GROUP BY user_id, day
                                                ORDER BY day)
                                            GROUP BY day""")).fetchall()
    date = [y for x, y in table]
    average = [x for x, y in table]
    mpl.style.use('seaborn-v0_8')
    ax = plt.subplots()[1]
    ax.fill_between(date, average)
    ax.set_xlim(date[0], date[-1])
    ax.set_ylim(0, max(average) + 5)
    ax.set_xticks(date[::35])
    ax.set_ylabel("Average spend/customer in ₳")
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%b'))


def main():
    try:
        engine = sqlalchemy.create_engine("postgresql+psycopg2://mprokosc:mysecretpassword@localhost:5432/piscineds")
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=engine)
        with engine.connect() as conn:
            fist_plot(conn)
            sec_plot(conn)
            third_plot(conn)
            plt.show()
    except (Exception, KeyboardInterrupt) as e:
        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()