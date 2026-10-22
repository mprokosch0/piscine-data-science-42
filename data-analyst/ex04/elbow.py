import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import sqlalchemy
import numpy as np

def main():
    try:
        engine = sqlalchemy.create_engine("postgresql+psycopg2://mprokosc:mysecretpassword@localhost:5432/piscineds")
        with engine.connect() as conn:
            data = conn.execute(sqlalchemy.text("""select user_id, COUNT(*) as purchases
                                                FROM customers
                                                Where event_type = 'purchase'
                                                GROUP BY user_id
                                                ORDER BY purchases DESC;""")).fetchall()

            X = np.array([row[1] for row in data]).reshape(-1, 1)
            ks = range(1, 11)
            wss = []
            for k in ks:
                kmeans = KMeans(n_clusters=k, n_init=10).fit(X)
                wss.append(kmeans.inertia_)

            mpl.style.use('seaborn-v0_8')
            plt.plot(ks, wss)
            plt.xlabel("Number of clusters")
            plt.ticklabel_format(style='plain', axis='y')
            plt.title("The Elbow Method")
            plt.show()

    except (Exception, KeyboardInterrupt) as e:
        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()