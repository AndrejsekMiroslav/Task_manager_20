import pytest
import mysql.connector
from datetime import datetime
from Task_manager_20 import vytvoreni_tabulky

# === POMOCNÉ FUNKCE ===

def pripoj_test_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",                    # Upravte podle svého nastavení
        database="spravce_ukolu_test"   # Pro vyvtoření databáze spustit vytvoreni_db.py
    )

def vycistit_tabulku(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly")
    conn.commit()

# === FIXTURA: připojení k DB a vyčištění ===

@pytest.fixture
def db_conn():
    conn = pripoj_test_db()
    vytvoreni_tabulky(conn)
    vycistit_tabulku(conn)
    yield conn
    vycistit_tabulku(conn)
    conn.close()

# === TESTY: PRIDANI UKOLU ===

def test_pridat_ukol_pozitivni(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
        INSERT INTO ukoly (nazev, popis)
        VALUES (%s, %s)
    """, ("Testovací úkol", "Popis úkolu"))
    db_conn.commit()

    cursor.execute("SELECT * FROM ukoly WHERE nazev = %s", ("Testovací úkol",))
    vysledek = cursor.fetchone()
    assert vysledek is not None
    assert vysledek[1] == "Testovací úkol"
    cursor.close()

def test_pridat_ukol_negativni(db_conn):
    cursor = db_conn.cursor()
    with pytest.raises(mysql.connector.errors.DatabaseError):
        cursor.execute("""
            INSERT INTO ukoly (nazev, popis)
            VALUES (%s, %s)
        """, ("", ""))  # Neplatné vstupy
        db_conn.commit()
    cursor.close()    

# === TESTY: AKTUALIZACE UKOLU ===

def test_aktualizovat_ukol_pozitivni(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", ("Ukol", "Popis"))
    db_conn.commit()

    cursor.execute("SELECT id FROM ukoly WHERE nazev = %s", ("Ukol",))
    ukol_id = cursor.fetchone()[0]

    cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", ("Hotovo", ukol_id))
    db_conn.commit()

    cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (ukol_id,))
    novy_stav = cursor.fetchone()[0]
    assert novy_stav == "Hotovo"
    cursor.close()

def test_aktualizovat_ukol_negativni(db_conn):
    cursor = db_conn.cursor()
    neexistujici_id = 9999
    cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", ("Hotovo", neexistujici_id))
    db_conn.commit()

    cursor.execute("SELECT * FROM ukoly WHERE id = %s", (neexistujici_id,))
    vysledek = cursor.fetchone()
    assert vysledek is None
    cursor.close()

# === TESTY: ODEBRANI UKOLU ===

def test_odstranit_ukol_pozitivni(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", ("Smazat", "Popis"))
    db_conn.commit()

    cursor.execute("SELECT id FROM ukoly WHERE nazev = %s", ("Smazat",))
    ukol_id = cursor.fetchone()[0]

    cursor.execute("DELETE FROM ukoly WHERE id = %s", (ukol_id,))
    db_conn.commit()

    cursor.execute("SELECT * FROM ukoly WHERE id = %s", (ukol_id,))
    vysledek = cursor.fetchone()
    assert vysledek is None
    cursor.close()

def test_odstranit_ukol_negativni(db_conn):
    cursor = db_conn.cursor()
    neexistujici_id = 9999

    cursor.execute("DELETE FROM ukoly WHERE id = %s", (neexistujici_id,))
    db_conn.commit()

    # Ověření, že se nic nestalo (žádná chyba, ale také nic nezmizelo)
    cursor.execute("SELECT * FROM ukoly")
    vsechny_ukoly = cursor.fetchall()
    assert isinstance(vsechny_ukoly, list)
    cursor.close()