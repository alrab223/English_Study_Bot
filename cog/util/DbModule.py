import mysql.connector as connector
import os
from dotenv import load_dotenv


class DbModule:
   def __init__(self):
      base_path = os.path.dirname(os.path.abspath(__file__))
      dotenv_path = os.path.join(base_path, '.env')
      load_dotenv(dotenv_path)

   def __db_connect(self):
      try:
         db = connector.connect(
             user=os.getenv('DB_USER'),
             passwd=os.getenv('DB_PASSWORD'),
             host=os.getenv('DB_HOST'),
             db=os.getenv('DB_DATABASE')
         )
         return db
      except Exception as e:
         print(e)
         raise

   def text_fix(self, query):
      query = query.replace("'", "''")
      query = query.replace("\\", "\\\\")  # 使えない文字を変換
      return query

   def insert(self, table: str, datas: dict):
      cnx = self.__db_connect()
      cur = cnx.cursor()
      parameters = []
      columns = list(datas.keys())
      values = list(datas.values())
      for parameter in values:
         if isinstance(parameter, str):
            parameter = self.text_fix(parameter)
            parameters.append(str('\'' + parameter + '\''))
         else:
            if parameter is None:
               parameters.append("NULL")
            else:
               parameters.append(str(parameter))
      new_columns = [f"%({x})s" for x in columns]
      new_columns = ", ".join(columns)
      parameters = ", ".join(parameters)
      sql = f"INSERT INTO {table} ({new_columns}) VALUES ({parameters})"
      try:
         cur.execute(sql)
         cnx.commit()
         return True
      except BaseException:
         cnx.rollback()
         raise

   def allinsert(self, table: str, values: list):
      cnx = self.__db_connect()
      cur = cnx.cursor()
      parameters = []
      for parameter in values:
         if isinstance(parameter, str):
            parameter = self.text_fix(parameter)
            parameters.append(str('\'' + parameter + '\''))
         else:
            if parameter is None:
               parameters.append("NULL")
            else:
               parameters.append(str(parameter))
      parameters = ", ".join(parameters)
      sql = f"INSERT INTO {table} VALUES ({parameters})"
      try:
         cur.execute(sql)
         cnx.commit()
         return True
      except BaseException:
         cnx.rollback()
         raise

   def insert_bulk(self, table: str, values: list):
      cnx = self.__db_connect()
      cur = cnx.cursor()
      bulk = []
      for value in values:
         parameters = []
         for parameter in value:
            if isinstance(parameter, str):
               parameter = self.text_fix(parameter)
               parameters.append(str('\'' + parameter + '\''))
            else:
               if parameter is None:
                  parameters.append("NULL")
               else:
                  parameters.append(str(parameter))
         parameters = ", ".join(parameters)
         sql = f"INSERT INTO {table} VALUES ({parameters})"
         bulk.append(sql)
      for sql in bulk:
         cur.execute(sql)
      try:
         cnx.commit()
      except BaseException:
         cnx.rollback()
         raise

   def select(self, sql: str):
      cnx = self.__db_connect()
      cur = cnx.cursor(dictionary=True)
      try:
         cur.execute(sql)
         response = cur.fetchall()
         cur.close()
      except BaseException:
         raise

      return response

   def parameter_fix(self, columns, values):
      parameters = []
      for parameter in values:
         if isinstance(parameter, str):
            parameter = self.text_fix(parameter)
            parameters.append(str('\'' + parameter + '\''))
         else:
            if parameter is None:
               parameters.append("NULL")
            else:
               parameters.append(str(parameter))
      set_values = []
      for i in range(len(columns)):
         set_values.append(f"{columns[i]}={parameters[i]}")
      return set_values

   # 条件式がイコールだけかつ、論理積の時
   def update(self, table: str, values: dict, where: dict):
      cnx = self.__db_connect()
      cur = cnx.cursor()
      columns = list(values.keys())
      values = list(values.values())
      set_values = self.parameter_fix(columns, values)
      set_values = ", ".join(set_values)
      sql = f"UPDATE {table} SET {set_values}"

      # 条件式があった場合
      if where is not None:
         columns = list(where.keys())
         values = list(where.values())
         set_values = self.parameter_fix(columns, values)
         set_values = "and ".join(set_values)
         sql += f" where {set_values}"

      try:
         cur.execute(sql)
         cnx.commit()
      except BaseException:
         cnx.rollback()
         raise

   # 条件式がイコールだけかつ、論理積の時
   def delete(self, table: str, where: dict = None):
      cnx = self.__db_connect()
      cur = cnx.cursor()

      # 条件式があった場合
      if where is not None:
         columns = list(where.keys())
         values = list(where.values())
         set_values = self.parameter_fix(columns, values)
         set_values = "and ".join(set_values)
         sql = f"DELETE FROM {table} where {set_values}"
      else:
         sql = f"DELETE FROM {table}"

      try:
         cur.execute(sql)
         cnx.commit()
      except BaseException:
         cnx.rollback()
         raise

   def custom_update(self, sql: str):
      cnx = self.__db_connect()
      cur = cnx.cursor()
      sql = self.text_fix(sql)
      try:
         cur.execute(sql)
         cnx.commit()
      except BaseException:
         cnx.rollback()
         raise

   def custom_delete(self, sql: str):
      cnx = self.__db_connect()
      cur = cnx.cursor()
      sql = self.text_fix(sql)
      try:
         cur.execute(sql)
         cnx.commit()
      except BaseException:
         cnx.rollback()
         raise
