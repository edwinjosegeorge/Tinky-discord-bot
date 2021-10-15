import os
import difflib
import psycopg2
import urllib.parse as urlparse
from dotenv import load_dotenv
from memberProp import DiscordMember


class DataBunker:
    def __init__(self):
        self.loadURL()

    def loadURL(self):
        load_dotenv()
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        self.dbname = url.path[1:]
        self.user = url.username
        self.password = url.password
        self.host = url.hostname
        self.port = url.port

    def search(self, table: str, param: dict, op="AND") -> bool:
        # searches DB for key->value in table, if found return True, else False
        op = " "+str(op).strip()+" "
        conn = None
        status = False
        for key in param:
            param[key] = str(param[key]).upper().strip()
        try:
            self.loadURL()
            conn = psycopg2.connect(dbname=self.dbname, user=self.user,
                                    password=self.password, host=self.host,
                                    port=self.port)
            cursor = conn.cursor()

            query = f"SELECT * FROM {table} WHERE "
            query += op.join([f"{k}='{param[k]}'" for k in param])

            cursor.execute(query)
            status = cursor.rowcount > 0
            cursor.close()
        except Exception as error:
            print(f'database {table} search error', error)
        finally:
            if conn is not None:
                conn.close()
                # print(f'database search on {table} is', status)
            return status

    def add(self, table: str, param: dict) -> bool:
        # add new record record return true on success
        conn = None
        status = False
        for key in param:
            param[key] = str(param[key]).upper().strip()
        try:
            self.loadURL()
            conn = psycopg2.connect(dbname=self.dbname, user=self.user,
                                    password=self.password, host=self.host,
                                    port=self.port)
            cursor = conn.cursor()

            query = f"INSERT INTO {table} ("
            query += ", ".join([str(k) for k in param]) + ") VALUES ( "
            query += ", ".join(["'"+param[k]+"'" for k in param]) + ")"

            cursor.execute(query)
            conn.commit()
            status = cursor.rowcount > 0
            cursor.close()
        except Exception as error:
            print(f'database {table} add error ', error)
        finally:
            if conn is not None:
                conn.close()
                # print(f'database add on {table} is', status)
            return status

    def update(self, table: str, oldparam: dict, newparam: dict) -> bool:
        # update existing record return true on success
        conn = None
        status = False
        for key in newparam:
            newparam[key] = str(newparam[key]).upper().strip()
        for key in oldparam:
            oldparam[key] = str(oldparam[key]).upper().strip()
        try:
            self.loadURL()
            conn = psycopg2.connect(dbname=self.dbname, user=self.user,
                                    password=self.password, host=self.host,
                                    port=self.port)
            cursor = conn.cursor()

            query = f"UPDATE {table} SET "
            query += ", ".join([f"{k}='{newparam[k]}'" for k in newparam])
            query += " WHERE "
            query += " AND ".join([f"{k}='{oldparam[k]}'" for k in oldparam])

            cursor.execute(query)
            conn.commit()
            status = cursor.rowcount > 0
            cursor.close()
        except Exception as error:
            print(f'database {table} update error', error)
        finally:
            if conn is not None:
                conn.close()
                # print(f'database update on {table} is', status)
            return status

    def remove(self, table: str, param: dict, op="AND") -> bool:
        # searches DB for key->value in table, if found return True, else False
        op = " "+str(op).strip()+" "
        conn = None
        status = False
        for key in param:
            param[key] = str(param[key]).upper().strip()
        try:
            self.loadURL()
            conn = psycopg2.connect(dbname=self.dbname, user=self.user,
                                    password=self.password, host=self.host,
                                    port=self.port)
            cursor = conn.cursor()

            query = f"DELETE FROM {table} WHERE "
            query += op.join([f"{k}='{param[k]}'" for k in param])

            cursor.execute(query)
            conn.commit()
            status = cursor.rowcount > 0
            cursor.close()
        except Exception as error:
            print(f'database {table} delete error', error)
        finally:
            if conn is not None:
                conn.close()
                # print(f'database delete on {table} is', status)
            return status

    def check_gcekian(self, Dmember: DiscordMember) -> bool:
        # Checks if the member is a GCEKian or not. Look and maps GCEK_list
        # if match found, update name and return True, else False
        if not(isinstance(Dmember, DiscordMember)):
            print("In compatable types")
            return False
        conn = None
        status = False
        try:
            self.loadURL()
            conn = psycopg2.connect(dbname=self.dbname, user=self.user,
                                    password=self.password, host=self.host,
                                    port=self.port)
            cursor = conn.cursor()

            query = "SELECT name,branch,year FROM gcek_list "
            query += f"WHERE admn='{Dmember.admn.upper()}'"

            cursor.execute(query)

            record = cursor.fetchall()
            if cursor.rowcount != 1:
                cursor.close()
                return False

            name = str(record[0][0]).upper().strip()
            branch = str(record[0][1]).upper().strip()
            year = str(record[0][2]).upper().strip()

            if branch == Dmember.branch and year == Dmember.year:
                # comparing name
                seq = difflib.SequenceMatcher(None, name,
                                              Dmember.name.strip().upper())
                status = float(seq.ratio()) > 0.8
                if status:
                    Dmember.name = name.title()
            cursor.close()
        except Exception as error:
            print('check_gcekian error', error)
        finally:
            if conn is not None:
                conn.close()
                # print('check_gcekian status is ', status)
            return status
