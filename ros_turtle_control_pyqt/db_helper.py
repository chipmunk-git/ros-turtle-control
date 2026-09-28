import pymysql


DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="1234",
    database="rosdb",
    charset="utf8"
)


class DB:

    def __init__(self, **config):
        self.config = config

    def connect(self):
        return pymysql.connect(**self.config)

    # 거북이 위치 저장
    def insert_pose(self, x, y, theta):
        sql = "INSERT INTO turtlepos (x, y, theta) VALUES (%s, %s, %s)"

        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (x, y, theta))

                conn.commit()
                return True

            except Exception:
                conn.rollback()
                return False
