import sqlite3


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


# dane testowe- usunąć po pierwszym uruchomieniu aplikacji
c.execute("INSERT INTO autorzy (imie, nazwisko) VALUES (?, ?)", ('Adam', 'Mickiewicz'))
c.execute("INSERT INTO ksiazki (tytul, rok_wydania, imie_autora, nazwisko_autora, status) VALUES (?, ?, ?, ?, ?)", ('Pan Tadeusz', 1834, 'Adam', 'Mickiewicz', 'niedostępna'))
c.execute("INSERT INTO wypozyczenia (tytul, nazwisko_autora, data_wypozyczenia, data_zwrotu) VALUES (?, ?, ?, ?)", ('Pan Tadeusz', 'Adam', '2022-06-01', '2022-06-15'))


conn.commit()

# menu główne
while True:
    print('''
        Witaj w Domowej Bibliotece!

        Wybierz jedną z opcji:
        1. Dodaj autora
        2. Dodaj książkę
        3. Wypożycz książkę
        4. Oddaj książkę
        5. Wyświetl listę autorów
        6. Wyświetl listę książek
        7. Wyświetl listę wypożyczeń
        8. Wyjdź z programu
    ''')

    
    wybor = input("Twój wybór: ")

    # dodanie autora
    if wybor == '1':
        imie = input("Podaj imię autora: ")
        nazwisko = input("Podaj nazwisko autora: ")
        c.execute("INSERT INTO autorzy (imie, nazwisko) VALUES (?, ?)", (imie, nazwisko))
        conn.commit()
        print("Dodano autora!")

    # dodanie książki
    elif wybor == '2':
        tytul = input("Podaj tytuł książki: ")
        rok_wydania = input("Podaj rok wydania książki: ")
        imie_autora = input("Podaj imię autora książki: ")
        nazwisko_autora = input("Podaj nazwisko autora książki: ")

        c.execute("SELECT id FROM autorzy WHERE imie = ? AND nazwisko = ?", (imie_autora, nazwisko_autora))
        autor = c.fetchone()

        if autor is None:
            c.execute("INSERT INTO autorzy (imie, nazwisko) VALUES (?, ?)", (imie_autora, nazwisko_autora))
            conn.commit()
            autor_id = c.lastrowid
            print("Dodano nowego autora!")
        else:
            autor_id = autor[0]      
        c.execute("INSERT INTO ksiazki (tytul, rok_wydania, imie_autora, nazwisko_autora, status) VALUES (?, ?, ?, ?, ?)", (tytul, rok_wydania, imie_autora, nazwisko_autora, 'dostępna'))
        conn.commit()
        print("Dodano książkę!")
        
    # wypożyczenie książki
    elif wybor == '3':
        tytul = input("Podaj tytuł książki do wypożyczenia: ")
        c.execute("SELECT * FROM ksiazki WHERE tytul=?", (tytul,))
        ksiazka = c.fetchone()
        if ksiazka:
            if ksiazka[5] == 'dostępna':
                c.execute("UPDATE ksiazki SET status='niedostępna' WHERE tytul=?", (tytul,))
                nazwisko_autora = ksiazka[4]
                data_wypozyczenia = input("Podaj datę wypożyczenia książki w formacie RRRR-MM-DD: ")
                data_zwrotu = input("Podaj datę zwrotu książki w formacie RRRR-MM-DD: ")
                c.execute("INSERT INTO wypozyczenia (tytul, nazwisko_autora, data_wypozyczenia, data_zwrotu) VALUES (?, ?, ?, ?)", (tytul, nazwisko_autora, data_wypozyczenia, data_zwrotu))
                conn.commit()
                print("Książka została wypożyczona!")
            else:
                print("Książka jest już wypożyczona.")
        else:
            print("Nie znaleziono książki o podanym tytule.")

    # oddanie książki
    elif wybor == '4':
        tytul = input("Podaj tytuł książki do oddania: ")
        c.execute("SELECT * FROM ksiazki WHERE tytul=?", (tytul,))
        ksiazka = c.fetchone()
        if ksiazka:
            c.execute("UPDATE ksiazki SET status='dostępna' WHERE tytul=?", (tytul,))
            c.execute("SELECT * FROM wypozyczenia WHERE tytul=? ORDER BY id DESC LIMIT 1", (tytul,))
            wypozyczenie = c.fetchone()
            if wypozyczenie:
                c.execute("DELETE FROM wypozyczenia WHERE id=?", (wypozyczenie[0],))
                conn.commit()
                print("Książka została oddana!")
            else:
                print("Nie znaleziono wypożyczenia dla podanego tytułu.")
        else:
            print("Nie znaleziono książki o podanym tytule.")

    # wyświetlenie listy autorów
    elif wybor == '5':
        c.execute("SELECT * FROM autorzy")
        autorzy = c.fetchall()
        print("Lista autorów:")
        for autor in autorzy:
            print("- {} {}".format(autor[1], autor[2]))

    # wyświetlenie listy książek
    elif wybor == '6':
        c.execute("SELECT * FROM ksiazki")
        ksiazki = c.fetchall()
        print("Lista książek:")
        for ksiazka in ksiazki:
            print("- {} ({}) - {}, {}, status: {}".format(ksiazka[1], ksiazka[2], ksiazka[3], ksiazka[4], ksiazka[5]))

    # wyświetlenie listy wypożyczeń
    elif wybor == '7':
        c.execute("SELECT * FROM wypozyczenia")
        wypozyczenia = c.fetchall()
        print("Lista wypożyczeń:")
        for wypozyczenie in wypozyczenia:
            print("- {} - od: {}, do: {}".format(wypozyczenie[0], wypozyczenie[3], wypozyczenie[4]))

    # wyjście z programu
    elif wybor == '8':
        print("Dziękujemy za korzystanie z Domowej Biblioteki!")
        break

    # nieznany wybór
    else:
        print("Nieznana opcja. Wybierz ponownie.")
