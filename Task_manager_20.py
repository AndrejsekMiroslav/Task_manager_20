import mysql.connector
from mysql.connector import Error
from datetime import datetime

def connect_to_database():
    """
    Připojení k databázi.
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Upravte podle svého nastavení
            database="spravce_ukolu"  # Pro vyvtoření databáze spustit vytvoreni_db.py
        )

        if conn.is_connected():
            print("Připojení k databázi je úspěšné!")
            db_info = conn.get_server_info()
            print(f"MySQL verze: {db_info}")
            return conn
    except mysql.connector.Error as e:
        print(f"Chyba při připojení: {e}")
        return None

def vytvoreni_tabulky(conn):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ukoly (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nazev VARCHAR(255) NOT NULL CHECK (TRIM(nazev) <> ''),
        popis TEXT NOT NULL CHECK (TRIM(popis) <> ''),
        stav ENUM('Nezahájeno', 'Probíhá', 'Hotovo') DEFAULT 'Nezahájeno',
        datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

def pridat_ukol(conn):
    nazev = input("Zadejte název úkolu: ").strip()
    if not nazev:
        print("Název nemůže být prázdný.")
        return

    popis = input("Zadejte popis úkolu: ").strip()
    if not popis:
        print("Popis nemůže být prázdný.")
        return

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ukoly (nazev, popis)
        VALUES (%s, %s)
    """, (nazev, popis))
    conn.commit()
    print("Úkol byl přidán.")

def zobrazit_ukoly(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nazev, popis, stav, datum_vytvoreni
        FROM ukoly
        WHERE stav IN ('Nezahájeno', 'Probíhá')
    """)
    ukoly = cursor.fetchall()
    if not ukoly:
        print("Žádné úkoly k zobrazení.")
    else:
        for ukol in ukoly:
            print(f"{ukol[0]}. {ukol[1]} – {ukol[2]} | Stav: {ukol[3]} | Vytvořeno: {ukol[4]}")

def aktualizovat_ukol(conn):
    zobrazit_ukoly(conn)
    try:
        id_ukolu = int(input("Zadejte ID úkolu ke změně stavu: "))
        novy_stav = input("Zadejte nový stav (Probíhá / Hotovo): ").strip()
        if novy_stav not in ["Probíhá", "Hotovo"]:
            print("Neplatný stav.")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ukoly WHERE id = %s", (id_ukolu,))
        if not cursor.fetchone():
            print("Úkol s tímto ID neexistuje.")
            return

        cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, id_ukolu))
        conn.commit()
        print("Stav úkolu byl aktualizován.")
    except ValueError:
        print("Neplatné ID.")

def odstranit_ukol(conn):
    zobrazit_ukoly(conn)
    try:
        id_ukolu = int(input("Zadejte ID úkolu k odstranění: "))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ukoly WHERE id = %s", (id_ukolu,))
        if not cursor.fetchone():
            print("Úkol s tímto ID neexistuje.")
            return
        cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
        conn.commit()
        print("Úkol byl odstraněn.")
    except ValueError:
        print("Neplatné ID.")

def hlavni_menu(conn):
    while True:
        print("\n--- Hlavní menu ---")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Konec")

        volba = input("Vyberte možnost (1–5): ")
        if volba == "1":
            pridat_ukol(conn)
        elif volba == "2":
            zobrazit_ukoly(conn)
        elif volba == "3":
            aktualizovat_ukol(conn)
        elif volba == "4":
            odstranit_ukol(conn)
        elif volba == "5":
            print("Program ukončen.")
            break
        else:
            print("Neplatná volba. Zkuste to znovu.")

if __name__ == "__main__":
    conn = connect_to_database()
    if conn:
        vytvoreni_tabulky(conn)
        hlavni_menu(conn)
        conn.close()