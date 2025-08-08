import mysql.connector
from mysql.connector import Error

def vytvor_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="" # Upravte podle svého nastavení
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS spravce_ukolu_test")
        print("Testovací databáze byla vytvořena (nebo už existuje).")
    except Error as e:
        print("Chyba při vytváření testovací databáze:", e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

vytvor_db()