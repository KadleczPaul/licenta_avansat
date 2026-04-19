import mysql.connector
from mysql.connector import Error
from config import Config  # Importăm clasa Config pentru a accesa setările


class Database:


    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        try:
            self.conn = mysql.connector.connect(**Config.DB_CONFIG)

            self.cursor = self.conn.cursor(dictionary=True)
            return self.cursor
        except Error as e:
            print(f"CRITICAL: Database connection failed: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.conn:
            return

        try:
            if exc_type:
                self.conn.rollback()
                print(f"Transaction rolled back. Error: {exc_val}")
            else:
                self.conn.commit()
        finally:
            self.cursor.close()
            self.conn.close()


def check_db_connection():
    try:
        connection = mysql.connector.connect(**Config.DB_CONFIG)
        if connection.is_connected():
            print("--- [DATABASE] Connection Status: OK ---")
            connection.close()
            return True
    except Error as e:
        print(f"--- [DATABASE] Connection Status: FAILED ({e}) ---")
        return False


if __name__ == "__main__":
    check_db_connection()