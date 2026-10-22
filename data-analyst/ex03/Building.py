import matplotlib.pyplot as plt
import matplotlib as mpl
import sqlalchemy
import numpy as np


def first_plot(conn: sqlalchemy.Connection):
    data = conn.execute(sqlalchemy.text("""SELECT 
                                                (floor(nombre_commandes / 10.0) * 10)::int AS debut_tranche,
                                                (floor(nombre_commandes / 10.0) * 10 + 10)::int AS fin_tranche,
                                                COUNT(*) AS nombre_clients
                                                FROM (
                                                
                                                    SELECT COUNT(*) AS nombre_commandes 
                                                    FROM customers 
                                                    WHERE event_type = 'purchase'
                                                    GROUP BY user_id
                                                ) c
                                            GROUP BY debut_tranche, fin_tranche
                                            ORDER BY debut_tranche;""")).fetchall()
    mpl.style.use('seaborn-v0_8')
    ax = plt.subplots()[1]
    xaxis = np.array([x[0] for x in data])
    yaxis = [x[2] for x in data]
    center = (xaxis[:-1] + xaxis[1:]) / 2
    ax.bar(center[0:5], yaxis[0:5], width=8, align="center", color="steelblue")
    ax.set_xlim(xaxis[0], xaxis[0:5][-1])
    ax.set_xticks(xaxis[0:6])
    ax.set_xlabel("frequency")
    ax.set_ylabel("customers")
    mpl.style.use('seaborn-v0_8')



def sec_plot(conn: sqlalchemy.Connection):
    data = conn.execute(sqlalchemy.text("""SELECT 
                                                (floor(total_price / 50.0) * 50)::int AS debut_tranche,
                                                (floor(total_price / 50.0) * 50 + 50)::int AS fin_tranche,
                                                COUNT(*) AS nombre_clients
                                            FROM (

                                                SELECT SUM(price) AS total_price 
                                                FROM customers 
                                            	WHERE event_type = 'purchase' AND price >= 0
                                                GROUP BY user_id
                                            )
                                            GROUP BY debut_tranche, fin_tranche
                                            ORDER BY debut_tranche;	""")).fetchall()
    mpl.style.use('seaborn-v0_8')
    ax = plt.subplots()[1]
    xaxis = np.array([x[0] for x in data])
    yaxis = [x[2] for x in data]
    ax.bar(xaxis[0:5], yaxis[0:5], width=48, align="center", color="steelblue")
    ax.set_xticks(xaxis[0:6])
    ax.set_xlabel("monetary value in ₳")
    ax.set_ylabel("customers")
    mpl.style.use('seaborn-v0_8')



def main():
    try:
        engine = sqlalchemy.create_engine("postgresql+psycopg2://mprokosc:mysecretpassword@localhost:5432/piscineds")
        with engine.connect() as conn:
            first_plot(conn)
            sec_plot(conn)
            plt.show()

    except (Exception, KeyboardInterrupt) as e:
        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()