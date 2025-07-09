import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QLabel
from PyQt5.QtCore import Qt, QTimer

class Plansza:
    _instancja = None
    SZEROKOSC = 20
    WYSOKOSC = 20

    def __new__(cls, szerokosc=10, wysokosc=10):
        if cls._instancja is None:
            cls._instancja = super(Plansza, cls).__new__(cls)
            cls._instancja.szerokosc = szerokosc
            cls._instancja.wysokosc = wysokosc
            cls._instancja.komorki = [[FabrykaKomorek.utworz_komorke("martwa") for _ in range(szerokosc)] for _ in range(wysokosc)]
        return cls._instancja

    def ustaw_komorke(self, x, y, komorka):
        if 0 <= x < self.szerokosc and 0 <= y < self.wysokosc:
            self.komorki[y][x] = komorka

    def pobierz_komorke(self, x, y):
        if 0 <= x < self.szerokosc and 0 <= y < self.wysokosc:
            return self.komorki[y][x]
        else:
            return FabrykaKomorek.utworz_komorke("martwa")

class Komorka:
    def __init__(self, zywa=False):
        self.zywa = zywa

    def zmien_stan(self, stan):
        self.zywa = stan

class ZywaKomorka(Komorka):
    def __init__(self):
        super().__init__(True)

class MartwaKomorka(Komorka):
    def __init__(self):
        super().__init__(False)

class FabrykaKomorek:
    @staticmethod
    def utworz_komorke(typ):
        if typ == "zywa":
            return  ZywaKomorka()
        else:
            return  MartwaKomorka()

class Obserwator:
    def aktualizuj(self, plansza):
        pass

class GUIWidok(Obserwator):
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.layout = QVBoxLayout(self.window)
        self.label = QLabel("Gra w Życie", self.window)
        self.layout.addWidget(self.label)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self.window)
        self.layout.addWidget(self.view)
        self.window.setLayout(self.layout)
        self.window.setWindowTitle("Gra w Życie")
        self.window.show()

    def aktualizuj(self, plansza):
        self.scene.clear()
        szerokosc = 20
        wysokosc = 20
        for y in range(plansza.wysokosc):
            for x in range(plansza.szerokosc):
                komorka = plansza.pobierz_komorke(x, y)
                if komorka.zywa:
                    params = QGraphicsRectItem(x * szerokosc, y * wysokosc, szerokosc, wysokosc)
                    params.setBrush(Qt.blue)
                    self.scene.addItem(params)
                else:
                    params = QGraphicsRectItem(x * szerokosc, y * wysokosc, szerokosc, wysokosc)
                    params.setBrush(Qt.white)
                    self.scene.addItem(params)

class Symulacja:
    def __init__(self, plansza, obserwator):
        self.plansza = plansza
        self.obserwator = obserwator

    def policz_sasiadow(self, x, y):
        return sum(
            self.plansza.pobierz_komorke(x+ delta_x, y + delta_y).zywa
            for delta_x in range(-1, 2)
            for delta_y in range(-1, 2)
            if not (delta_x == 0 and delta_y == 0)
        )

    def aktualizuj(self):
        nowe_stany = []
        for y in range(self.plansza.wysokosc):
            wiersz = []
            for x in range(self.plansza.szerokosc):
                komorka = self.plansza.pobierz_komorke(x, y)
                sasiedzi = self.policz_sasiadow(x, y)
                if komorka.zywa:
                    if sasiedzi < 2 or sasiedzi > 3:
                        wiersz.append(False)  # umiera
                    else:
                        wiersz.append(True)  # żyje
                else:
                    if sasiedzi == 3:
                        wiersz.append(True)  # rodzi się
                    else:
                        wiersz.append(False)  # martwa
            nowe_stany.append(wiersz)

        for y in range(self.plansza.wysokosc):
            for x in range(self.plansza.szerokosc):
                self.plansza.komorki[y][x].zmien_stan(nowe_stany[y][x])
        self.obserwator.aktualizuj(self.plansza)

if __name__ == "__main__":
    plansza = Plansza(Plansza.SZEROKOSC, Plansza.WYSOKOSC)

    for x in range(plansza.szerokosc):
        for y in range(plansza.wysokosc):
            if random.random() < 0.5:
                plansza.ustaw_komorke(x,y,FabrykaKomorek.utworz_komorke("zywa"))

    widok = GUIWidok()
    symulacja = Symulacja(plansza, widok)
    timer = QTimer()
    timer.timeout.connect(lambda: symulacja.aktualizuj())
    symulacja.aktualizuj()
    timer.start(100)
    widok.window.setGeometry(100, 100, 500, 500)
    sys.exit(widok.app.exec_())