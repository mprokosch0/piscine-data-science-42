import matplotlib.pyplot as plt
import matplotlib as mpl
import sqlalchemy
import numpy as np


def first_plot(prices: np.ndarray):
    mpl.style.use('seaborn-v0_8')
    ax = plt.subplots()[1]
    ax.boxplot(prices, orientation="horizontal", widths=10, patch_artist = True,
                boxprops=dict(facecolor="lightgreen", edgecolor='black'),
                flierprops=dict(marker='d', markersize=2, alpha=0.3))
    ax.set_yticks([])
    plt.xlabel("price")


def sec_plot(prices: np.ndarray):
    mpl.style.use('seaborn-v0_8')
    ax = plt.subplots()[1]
    ax.boxplot(prices,  patch_artist=True, orientation="horizontal",
                    boxprops=dict(facecolor="lightgreen", edgecolor='black'),
                    widths=10, showfliers=False)
    ax.set_yticks([])
    plt.xlabel("price")


def third_plot(conn: sqlalchemy.Connection):
    query = np.array(conn.execute(sqlalchemy.text("""SELECT
                                                    AVG(price)::float AS avg_cart_value
                                                    FROM customers
                                                    WHERE event_type = 'cart'
                                                    GROUP BY user_id
                                                    HAVING AVG(price) BETWEEN 26 AND 44
                                   """)).scalars().all())
    mpl.style.use('seaborn-v0_8')
    ax = plt.subplots()[1]
    ax.boxplot(query, orientation="horizontal", widths=10, patch_artist = True,
                boxprops=dict(facecolor="lightblue", edgecolor='black'),
                flierprops=dict(marker='D', markersize=2, alpha=0.3), whis=0.2)
    ax.set_yticks([])



def main():
    try:
        engine = sqlalchemy.create_engine("postgresql+psycopg2://mprokosc:mysecretpassword@localhost:5432/piscineds")
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind=engine)
        with engine.connect() as conn:
            stats = conn.execute(sqlalchemy.text("""SELECT COUNT(*), AVG(price), STDDEV(price), MIN(price),
                                                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY price),
                                                    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY price),
                                                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY price),
                                                    MAX(price)
                                                    FROM customers
                                                    WHERE event_type = 'purchase'""")).fetchall()

            prices = np.array(
                        conn.execute(sqlalchemy.text(
                            "SELECT price::float FROM customers WHERE event_type = 'purchase'"
                        )).scalars().all()
                    )
            largeur_max = max(len(f"{float(n):.6f}") for n in stats[0])
            print(f"count    {float(stats[0][0]):>{largeur_max}.6f}")
            print(f"mean    {float(stats[0][1]):>{largeur_max}.6f}")
            print(f"std    {float(stats[0][2]):>{largeur_max}.6f}")
            print(f"min    {float(stats[0][3]):>{largeur_max}.6f}")
            print(f"25%    {float(stats[0][4]):>{largeur_max}.6f}")
            print(f"50%    {float(stats[0][5]):>{largeur_max}.6f}")
            print(f"75%    {float(stats[0][6]):>{largeur_max}.6f}")
            print(f"max    {float(stats[0][7]):>{largeur_max}.6f}")
            
            first_plot(prices)
            sec_plot(prices)
            third_plot(conn)
            plt.show()

    except (Exception, KeyboardInterrupt) as e:
        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()