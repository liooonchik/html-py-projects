import sys
import random
import csv

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel
from PyQt5.QtCore import Qt, QTimer

rozmiar_okna = 30

class Organizm:
    def __init__(self):
        self.wiek = 0
        self.energia = 0

    def symbol(self):
        return '⬜'

    def generacja(self, x, y, Plansza):
        self.wiek += 1

    def znalezc_sasiadow(self, x, y, Plansza):
        sasiedzi = []
        for delta_x in range(-1, 2):
            for delta_y in range(-1, 2):
                if (delta_x == 0 and delta_y == 0):
                    continue
                nowy_x = x + delta_x
                nowy_y = y + delta_y
                if 0 <= nowy_x < rozmiar_okna and 0 <= nowy_y < rozmiar_okna:
                    sasiedzi.append((nowy_x, nowy_y, Plansza[nowy_x][nowy_y]))
        random.shuffle(sasiedzi)
        return sasiedzi
class Pustka(Organizm):
    def symbol(self):
        return "⬜"

class Roslina(Organizm):
    def __init__(self):
        Organizm.__init__(self)
        self.energia = 1
    def symbol(self):
        return "🥕"

    def generacja(self, x, y, Plansza):
        self.wiek += 1
        if self.energia < 10:
            self.energia += 1

        liczba_roslin = 0
        for wiersz in Plansza:
            for organizm in wiersz:
                if type(organizm) == Roslina:
                    liczba_roslin += 1

        max_roslin = (rozmiar_okna * rozmiar_okna) // 2

        if self.wiek >= 4 and liczba_roslin < max_roslin:
            for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
                if type(sasiad) == Pustka:
                    Plansza[nowy_x][nowy_y] = Roslina()
                    break

class Roslinozerca(Organizm):
    def __init__(self):
        Organizm.__init__(self)
        self.energia = 8
    def symbol(self):
        return "🐇"

    def generacja(self, x, y, Plansza):
        self.wiek += 1
        if self.energia <= 0:           #nie umiera kiedy niema energii, jeśli nie ma energii i pojawi się roślina, można ją zjeść
            for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
                if type(sasiad) == Roslina:
                    self.energia += 2
                    Plansza[nowy_x][nowy_y] = Pustka()
                    break
            if self.wiek > 15:
                Plansza[x][y] = Pustka()
                return
        self.energia -= 1
        ruch = False

        for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
            if type(sasiad) == Roslina:
                self.energia += 2
                Plansza[nowy_x][nowy_y] = self
                Plansza[x][y] = Pustka()
                ruch = True
                break

        if not ruch:
            for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
                if type(sasiad) == Pustka:
                    self.energia -= 1
                    Plansza[nowy_x][nowy_y] = self
                    Plansza[x][y] = Pustka()
                    break
        if self.wiek >= 4 and self.energia >= 4:
            for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
                if type(sasiad) == Roslinozerca and sasiad.wiek >= 4 and sasiad.energia >= 4:
                    for pustka_x, pustka_y, pustka in self.znalezc_sasiadow(x, y, Plansza):
                        if type(pustka) == Pustka:
                            Plansza[pustka_x][pustka_y] = Roslinozerca()
                            break
                    break
        if self.wiek > 15:
            Plansza[x][y] = Pustka()

class Miesozerca(Organizm):
    def __init__(self):
        Organizm.__init__(self)
        self.energia = 12
    def symbol(self):
        return "🐺"

    def generacja(self, x, y, Plansza):
        self.wiek += 1

        if self.energia <= 0:
            for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
                if type(sasiad) == Roslinozerca:
                    self.energia += 9
                    Plansza[nowy_x][nowy_y] = Pustka()
                    break
            if self.wiek > 25:
                Plansza[x][y] = Pustka()
                return
        self.energia -= 2
        ruch = False

        for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
            if type(sasiad) == Roslinozerca:
                self.energia += 9
                Plansza[nowy_x][nowy_y] = self
                Plansza[x][y] = Pustka()
                ruch = True
                break

        if not ruch:
            for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
                if type(sasiad) == Pustka:
                    self.energia -= 2
                    Plansza[nowy_x][nowy_y] = self
                    Plansza[x][y] = Pustka()
                    break
        if self.wiek >= 5 and self.energia >= 10:
            for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
                if type(sasiad) == Miesozerca and sasiad.wiek >= 5 and sasiad.energia >= 10:
                    for pustka_x, pustka_y, pustka in self.znalezc_sasiadow(x, y, Plansza):
                        if type(pustka) == Pustka:
                            Plansza[pustka_x][pustka_y] = Miesozerca()
                            break
        if self.wiek > 25:
            Plansza[x][y] = Pustka()


class Wszystkozerca(Organizm):
    def __init__(self):
        Organizm.__init__(self)
        self.energia = 10
    def symbol(self):
        return "🐻"

    def generacja(self, x, y, Plansza):
        self.wiek += 1

        if self.energia <= 0:
            for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
                if type(sasiad) == Roslina:
                    self.energia += 3
                    Plansza[nowy_x][nowy_y] = Pustka()
                elif type(sasiad) == Miesozerca:
                    self.energia += 7
                    Plansza[nowy_x][nowy_y] = Pustka()
                    break
            if self.wiek > 30:
                Plansza[x][y] = Pustka()
                return
        self.energia -= 1
        ruch = False

        for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
            if type(sasiad) == Roslina:
                self.energia += 3
                Plansza[nowy_x][nowy_y] = self
                Plansza[x][y] = Pustka()
                ruch = True
                break
            elif type(sasiad) == Miesozerca:
                self.energia += 7
                Plansza[nowy_x][nowy_y] = self
                Plansza[x][y] = Pustka()
                ruch = True
                break

        if not ruch:
            for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
                if type(sasiad) == Pustka:
                    self.energia -= 1
                    Plansza[nowy_x][nowy_y] = self
                    Plansza[x][y] = Pustka()
                    break
        if self.wiek >= 5 and self.energia >= 8:
            for nowy_x, nowy_y, sasiad in self.znalezc_sasiadow(x, y, Plansza):
                if type(sasiad) == Wszystkozerca and sasiad.wiek >= 5 and sasiad.energia >= 8:
                    for pustka_x, pustka_y, pustka in self.znalezc_sasiadow(x, y, Plansza):
                        if type(pustka) == Pustka:
                            Plansza[pustka_x][pustka_y] = Wszystkozerca()
                            break
        if self.wiek > 30:
            Plansza[x][y] = Pustka()

class FabrykaKomorek:
    @staticmethod
    def utworz_komorke(type):
        if type == "Roslina":
            return  Roslina()
        elif type == "Roslinozerca":
            return  Roslinozerca()
        elif type == "Miesozerca":
            return Miesozerca()
        elif type == "Wszystkozerca":
            return Wszystkozerca()
        else:
            return Pustka()

class Obserwator:
    def aktualizuj(self, plansza):
        pass

class GUIWidok(Obserwator):
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.layout = QGridLayout(self.window)
        self.generacja_label = QLabel("Generacja: 0", self.window)
        self.generacja_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.generacja_label, 0, 0, 1, rozmiar_okna)
        self.labels = [[QLabel("⬜") for _ in range(rozmiar_okna)] for _ in range(rozmiar_okna)]
        for y in range(rozmiar_okna):
            for x in range(rozmiar_okna):
                self.layout.addWidget(self.labels[y][x], y + 1, x)
        self.window.setLayout(self.layout)
        self.window.setWindowTitle("Ekosystem")
        self.window.show()

    def aktualizuj(self, plansza, numer_generacji = 0):
        self.generacja_label.setText(f"Generacja: {numer_generacji}")
        for y in range(rozmiar_okna):
            for x in range(rozmiar_okna):
                self.labels[y][x].setText(plansza[y][x].symbol())


class Symulacja:
    def __init__(self, plansza, widok):
        self.plansza = plansza
        self.widok = widok
        self.generacja = 0
        self.startowe_ilosci = {
            "Roslina": 1,
            "Roslinozerca": 20,
            "Miesozerca": 10,
            "Wszystkozerca": 3
        }

        self.csv_file_path = 'dane.csv'
        with open(self.csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Generacja", "Roslina", "Roslinozerca", "Miesozerca", "Wszystkozerca"])

        self.timer = None
    def czas_trwania(self, timer):
        self.timer = timer

    def aktualizuj(self):
        if self.generacja >= 300:
            if self.timer:
                self.timer.stop()
            print("Symulacja zakończona po 300 generacjach")
            return

        kierunek = [(x, y) for y in range(rozmiar_okna) for x in range(rozmiar_okna)]
        random.shuffle(kierunek)
        for x, y in kierunek:
            self.plansza[y][x].generacja(y, x, self.plansza)
        self.generacja += 1
        self.widok.aktualizuj(self.plansza, self.generacja)
        self.dodaj_brakujace_klasy()

        ilosc_roslin = 0
        ilosc_roslinozercow = 0
        ilosc_miesozercow = 0
        ilosc_wszystkozercow = 0

        for y in range(rozmiar_okna):
            for x in range(rozmiar_okna):
                organizm = self.plansza[y][x]
                if type(organizm) == Roslina:
                    ilosc_roslin += 1
                if type(organizm) == Roslinozerca:
                    ilosc_roslinozercow += 1
                if type(organizm) == Miesozerca:
                    ilosc_miesozercow += 1
                if type(organizm) == Wszystkozerca:
                    ilosc_wszystkozercow += 1


        with open(self.csv_file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.generacja, ilosc_roslin, ilosc_roslinozercow, ilosc_miesozercow, ilosc_wszystkozercow])

        generacje = []
        rosliny = []
        roslinozercy = []
        miesozercy = []
        wszystkozercy = []

        with open(self.csv_file_path, mode= 'r') as file:
            czytacz = csv.DictReader(file)
            for wiersz in czytacz:
                generacje.append(int(wiersz['Generacja']))
                rosliny.append(int(wiersz['Roslina']))
                roslinozercy.append(int(wiersz['Roslinozerca']))
                miesozercy.append(int(wiersz['Miesozerca']))
                wszystkozercy.append(int(wiersz['Wszystkozerca']))

        #wykres_liniowy:
        plt.plot(generacje, rosliny, label='Rosliny')
        plt.plot(generacje, roslinozercy, label='Roslinozercy')
        plt.plot(generacje, miesozercy, label='Miesozercy')
        plt.plot(generacje, wszystkozercy, label='Wszystkozercy')

        plt.title('Wykres liniowy populacji organizmów')
        plt.xlabel('Generacja')
        plt.ylabel('Liczba organizmow')
        plt.legend()
        plt.tight_layout()
        plt.savefig('wykres_liniowy.png', dpi=300)
        plt.close()

        #wykres_kołowy:
        wartosci = [ilosc_roslin, ilosc_roslinozercow, ilosc_miesozercow, ilosc_wszystkozercow]
        labels = ['Rosliny', 'Roslinozercy', 'Miesozercy', 'Wszystkozercy']

        plt.figure(figsize=(8, 6))
        plt.pie(wartosci, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        plt.title('Wykres kołowy populacji organizmów')
        plt.tight_layout()
        plt.savefig('wykres_kolowy.png', dpi=300)
        plt.close()

    def dodaj_brakujace_klasy(self):
        klasy = {"Roslina": False, "Roslinozerca": False, "Miesozerca": False, "Wszystkozerca": False}

        for y in range(rozmiar_okna):
            for x in range(rozmiar_okna):
                objekt = self.plansza[y][x]
                if type(objekt) == Roslina:
                    klasy["Roslina"] = True
                elif type(objekt) == Roslinozerca:
                    klasy["Roslinozerca"] = True
                elif type(objekt) == Miesozerca:
                    klasy["Miesozerca"] = True
                elif type(objekt) == Wszystkozerca:
                    klasy["Wszystkozerca"] = True

        for klasa, obecny in klasy.items():
            if not obecny:
                wolne_pola = [(x, y) for y in range(rozmiar_okna) for x in range(rozmiar_okna)
                          if type(self.plansza[y][x]) == Pustka]
                ilosc_do_dodania = self.startowe_ilosci[klasa]
                for _ in range(ilosc_do_dodania):
                    if wolne_pola:
                        x, y = random.choice(wolne_pola)
                        wolne_pola.remove((x, y))
                        self.plansza[y][x] = FabrykaKomorek.utworz_komorke(klasa)



plansza = [[Pustka() for _ in range(rozmiar_okna)] for _ in range(rozmiar_okna)]
wolne_pola = [(x, y) for y in range(rozmiar_okna) for x in range(rozmiar_okna)]
random.shuffle(wolne_pola)

def dodaj_obekty(type, liczba):
    for _ in range(liczba):
        if wolne_pola:
            x, y = random.choice(wolne_pola)
            wolne_pola.remove((x, y))
            plansza[y][x] = FabrykaKomorek.utworz_komorke(type)

dodaj_obekty("Roslina", 1)
dodaj_obekty("Roslinozerca",20)
dodaj_obekty("Miesozerca", 10)
dodaj_obekty("Wszystkozerca", 3)


widok = GUIWidok()
symulacja = Symulacja(plansza, widok)
timer = QTimer()
symulacja.czas_trwania(timer)
timer.timeout.connect(lambda: symulacja.aktualizuj())
symulacja.aktualizuj()
timer.start(300)
widok.window.setGeometry(100, 100, 500, 500)
sys.exit(widok.app.exec_())
