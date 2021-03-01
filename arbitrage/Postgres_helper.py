import psycopg2
import logging
import dbconfig


class PostgresHelper:
    """
    PostgresHelper
    """
    _connect = None
    _cur = None

    def __init__(self):
        """
        Construnctor for PostgresHelper
        """
        self.init()

    def init(self):
        """
        init database connection
        :param dbconfig:
        :return: True/False
        """
        try:
            self._connect = psycopg2.connect(database=dbconfig.DATABASE,
                                        user=dbconfig.username,
                                        password=dbconfig.pwd,
                                        host=dbconfig.HOST,
                                        port=dbconfig.PORT)
            # create table
            self._cur = self._connect.cursor()
            logging.info(" Connected to Postgres database [ {db} ]...")
            return True
        except Exception as e:
            logging.error(" Connect Postgres exception : \n{e}\n")
            return False

    def get_conn(self):
        if self._connect:
            return self._connect
        else:
            self.init()
            return self._connect

    def close_conn(self):
        if self._connect:
            self._connect.close()
            logging.info(" Postgres database [ {db} ] connection closed....")

    def insert(self, sql):
        self._cur.execute(sql)
        self._connect.commit()

