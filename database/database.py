import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Database:
    def __new__(cls, user, password, host, port, dbname):
        if not hasattr(cls, 'instance'):
            cls.user = user
            cls.password = password
            cls.host = host
            cls.port = port
            cls.dbname = dbname
            cls.init(cls)
            cls.instance = super(Database, cls).__new__(cls)
        return cls.instance

    def init(self):
        try:
            self.db = psycopg2.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                dbname=self.dbname
            )
            self.db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        except psycopg2.OperationalError as err:
            print('\n/*/', err)
            if err.args[0] == 2003:
                print('Неверный формат host')
            elif err.args[0] == 1045:
                print('Неверное имя пользователя или пароль')
            elif err.args[0] == 1049:
                print('Не найдена база данных')
                self.db = psycopg2.connect(
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port,
                )
                self.db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                print("Создание базы даных...")
                try:
                    self.cursor = self.db.cursor()
                    self.cursor.execute("CREATE DATABASE " + self.dbname)
                    print("База данных создана. Перезапустите сервер.")
                except psycopg2.Error as error:
                    if error.pgcode == "42P04":
                        print("База данных уже существует")
                    else:
                        print('\n/*/', "Ошибка при создании базы данных:")
                        print('\n/*/', error)
                    return
                finally:
                    self.cursor.close()
            else:
                print('Неизвестная ошибка при подключении к БД')
            exit()
            return

        try:
            with open('database/init.sql') as initFile:
                initText = initFile.read()
            cur = self.db.cursor()
            cur.execute(initText)
            cur.close()
            print("Таблицы созданы")
        except psycopg2.Error as error:
            print('\n/*/', "Ошибка при создании таблиц:")
            print('\n/*/', error)
            return


    def execute(self, request: str, values: list[any] = [], toLists: bool = False, manyResults: bool = False) -> dict or (list, list):
        try:
            cur = self.db.cursor()
            cur.execute(request, values)
        except psycopg2.ProgrammingError as err:
            if err.args[0] == 1146:
                print('Таблицы не существует')
            elif err.args[0] == 1064:
                print('Неверный синтаксис запроса')
            print('\n/*/', request, '\n/*/', values, '\n/*/', err)
            raise err
        except psycopg2.OperationalError as err:
            if err.args[0] == 1054:
                print('Столбец не найден')
            print('\n/*/', request, '\n/*/', values, '\n/*/', err)
            raise err
        except psycopg2.Error as err:
            print('\n/*/', request, '\n/*/', values, '\n/*/', err)
            raise err

        try:
            # print(request)
            response = cur.fetchall().copy()
            description = cur.description
            cur.close()
            # print(response)
            if not toLists and not manyResults:
                if len(response) == 0:  # Ничего не нашлось
                    return {}

                response = dict(map(lambda key, val: (key[0], val), description, response[0]))
                return response

            columns = [desc[0] for desc in cur.description]
            if not manyResults:
                return response, columns
            # каждому элементу дописываем название его столбца
            res = []
            for row in response:
                dic = {}
                for i in range(len(row)):
                    dic[columns[i]] = row[i]
                res += [dic]
            return res
        except psycopg2.ProgrammingError as err:
            print('\n/*/', request, '\n/*/', values, '\n/*/', err)
            if not toLists:
                return {}
            return [], []
