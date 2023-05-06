from flask import Flask, render_template, request
import sqlite3
from werkzeug.exceptions import BadRequestKeyError


conn = sqlite3.connect('domowa_biblioteka.db')
c = conn.cursor()

# tabela autorów
c.execute('''CREATE TABLE IF NOT EXISTS autorzy
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             imie TEXT NOT NULL,
             nazwisko TEXT NOT NULL)''')

# tabela książek
c.execute('''CREATE TABLE IF NOT EXISTS ksiazki
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             tytul TEXT NOT NULL,
             rok_wydania INTEGER NOT NULL,
             imie_autora TEXT NOT NULL,
             nazwisko_autora TEXT NOT NULL,
             status TEXT DEFAULT 'dostępna',
             FOREIGN KEY (nazwisko_autora) REFERENCES autorzy(nazwisko))''')

# tabela wypożyczeń
c.execute('''CREATE TABLE IF NOT EXISTS wypozyczenia
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             tytul TEXT NOT NULL,
             nazwisko_autora TEXT NOT NULL,
             data_wypozyczenia TEXT,
             data_zwrotu TEXT,
             FOREIGN KEY (nazwisko_autora) REFERENCES autorzy(nazwisko),
             FOREIGN KEY (tytul) REFERENCES ksiazki(tytul))''')

"""
# dane testowe- do pierwszego uruchomienia aplikacji
c.execute("INSERT INTO autorzy (imie, nazwisko) VALUES (?, ?)", ('Adam', 'Mickiewicz'))
c.execute("INSERT INTO ksiazki (tytul, rok_wydania, imie_autora, nazwisko_autora, status) VALUES (?, ?, ?, ?, ?)", ('Pan Tadeusz', 1834, 'Adam', 'Mickiewicz', 'niedostępna'))
c.execute("INSERT INTO wypozyczenia (tytul, nazwisko_autora, data_wypozyczenia, data_zwrotu) VALUES (?, ?, ?, ?)", ('Pan Tadeusz', 'Adam', '2022-06-01', '2022-06-15'))
"""
conn.commit()


app = Flask(__name__)
    
@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/dodaj_autora', methods=['GET', 'POST'])
def dodaj_autora():
    if request.method == 'POST':
        imie = request.form['imie']
        nazwisko = request.form['nazwisko']
        conn = sqlite3.connect('domowa_biblioteka.db')
        c = conn.cursor()
        c.execute("INSERT INTO autorzy (imie, nazwisko) VALUES (?, ?)", (imie, nazwisko))
        conn.commit()
        conn.close()
        komunikat = f"Dodano autora  {imie} {nazwisko}"
        return render_template('dodaj_autora.html', komunikat=komunikat)
    else:
        return render_template('dodaj_autora.html')


@app.route('/dodaj_ksiazke', methods=['GET','POST'])
def dodaj_ksiazke():
    if request.method == 'POST':
        tytul = request.form['tytul']
        rok_wydania = request.form['rok_wydania']
        imie_autora = request.form['imie_autora']
        nazwisko_autora = request.form['nazwisko_autora']
        conn = sqlite3.connect('domowa_biblioteka.db')
        c = conn.cursor()
        c.execute("SELECT id FROM autorzy WHERE imie = ? AND nazwisko = ?", (imie_autora, nazwisko_autora))
        autor = c.fetchone()
        if autor is None:
            c.execute("INSERT INTO autorzy (imie, nazwisko) VALUES (?, ?)", (imie_autora, nazwisko_autora))
            conn.commit()
            autor_id = c.lastrowid
            komunikat_A= f"Dodano nowego autora - {imie_autora} {nazwisko_autora}"
        else:
            autor_id = autor[0]  
            komunikat_A= f"Autor - {imie_autora} {nazwisko_autora} znajduje się już w bazie danych"    
        c.execute("INSERT INTO ksiazki (tytul, rok_wydania, imie_autora, nazwisko_autora, status) VALUES (?, ?, ?, ?, ?)", (tytul, rok_wydania, imie_autora, nazwisko_autora, 'dostępna'))
        conn.commit()
        komunikat=f"Dodano książkę {tytul}"
        conn.close()
        return render_template('dodaj_ksiazke.html', komunikat=komunikat, komunikat_A=komunikat_A)
    else:
        return render_template('dodaj_ksiazke.html')
        
@app.route('/wypozycz_ksiazke', methods=['GET', 'POST'])
def wypozycz_ksiazke():
    if request.method == 'POST':
        tytul = request.form['tytul']
        conn = sqlite3.connect('domowa_biblioteka.db')
        c = conn.cursor()
        c.execute("SELECT * FROM ksiazki WHERE tytul=?", (tytul,))
        ksiazka = c.fetchone()
        if ksiazka:
            if ksiazka[5] == 'dostępna':
                c.execute("UPDATE ksiazki SET status='niedostępna' WHERE tytul=?", (tytul,))
                nazwisko_autora = ksiazka[4]
                data_wypozyczenia = request.form['data_wypozyczenia']
                data_zwrotu = request.form['data_zwrotu']
                c.execute("INSERT INTO wypozyczenia (tytul, nazwisko_autora, data_wypozyczenia, data_zwrotu) VALUES (?, ?, ?, ?)", (tytul, nazwisko_autora, data_wypozyczenia, data_zwrotu))
                conn.commit()
                komunikat= f"Książka {tytul} została wypożyczona!"
            else:
                komunikat= f"Książka {tytul} jest już wypożyczona."
        else:
            komunikat= f"Nie znaleziono książki {tytul}"
        conn.close()
        return render_template('wypozycz_ksiazke.html', komunikat=komunikat)
    else:
        return render_template('wypozycz_ksiazke.html')

@app.route('/oddaj_ksiazke', methods=['GET','POST'])
def oddaj_ksiazke():
    if request.method == 'POST':
        tytul = request.form['tytul']
        conn = sqlite3.connect('domowa_biblioteka.db')
        c = conn.cursor()
        c.execute("SELECT * FROM ksiazki WHERE tytul=?", (tytul,))
        ksiazka = c.fetchone()
        if ksiazka:
            c.execute("UPDATE ksiazki SET status='dostępna' WHERE tytul=?", (tytul,))
            c.execute("SELECT * FROM wypozyczenia WHERE tytul=? ORDER BY id DESC LIMIT 1", (tytul,))
            wypozyczenie = c.fetchone()
            if wypozyczenie:
                c.execute("DELETE FROM wypozyczenia WHERE id=?", (wypozyczenie[0],))
                conn.commit()
                komunikat =f"Książka {tytul} została oddana!"
            else:
                komunikat=f"Nie znaleziono wypożyczenia {tytul}"
        else:
            komunikat=f"Nie znaleziono książki {tytul}"
        conn.close()
        return render_template('oddaj_ksiazke.html', komunikat=komunikat)
    else:
        return render_template('oddaj_ksiazke.html')
    
@app.route('/autorzy', methods=['GET'])
def autorzy():
    conn = sqlite3.connect('domowa_biblioteka.db')
    c = conn.cursor()
    c.execute("SELECT * FROM autorzy")
    autorzy = c.fetchall()
    conn.close()
    return render_template('autorzy.html', autorzy=autorzy)

@app.route('/wypozyczenia', methods=['GET'])
def wypozyczenia():
    conn = sqlite3.connect('domowa_biblioteka.db')
    c = conn.cursor()
    c.execute("SELECT * FROM wypozyczenia")
    wypozyczenia = c.fetchall()
    conn.close()
    return render_template('wypozyczenia.html', wypozyczenia=wypozyczenia)

@app.route('/ksiazki', methods=['GET'])
def ksiazki():
    conn = sqlite3.connect('domowa_biblioteka.db')
    c = conn.cursor()
    c.execute("SELECT * FROM ksiazki")
    ksiazki = c.fetchall()
    conn.close()
    return render_template('ksiazki.html', ksiazki=ksiazki)

if __name__ == '__main__':
    app.run(debug=True)

