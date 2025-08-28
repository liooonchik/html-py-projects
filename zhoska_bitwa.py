import pygame
import random

rozmiar_komorki = 25
rozmiar_okna_x = 50
rozmiar_okna_y = 30
szerokosc = rozmiar_komorki * rozmiar_okna_x #1250
wysokosc = rozmiar_komorki * rozmiar_okna_y  #750
pole_size = 6

Green = (179, 255, 179)
Red = (255, 204, 204)
Blue = (179, 179, 255)
Yellow = (255, 255, 153)
White = (255, 255, 255)
Black = (0, 0, 0)
Gray = (150, 150, 150)
Kolor_szpital = (0, 255, 255, 100)

pygame.init()
pygame.mixer.init()
okno = pygame.display.set_mode((szerokosc, wysokosc))
pygame.display.set_caption("Zhoska bitwa")
font = pygame.font.SysFont("Segoe UI Emoji", 20)
font_menu = pygame.font.SysFont("Segoe UI Emoji", 30)
clock = pygame.time.Clock()
tlo = pygame.image.load("fon1.png").convert()

pygame.mixer.music.load('background_music1.wav')
super_ork_dead = pygame.mixer.Sound('ork_die.wav')
super_ork_dead.set_volume(0.8)
goblin_spawn_thresholds = pygame.mixer.Sound('goblin_spawn_thresholds.wav')
goblin_spawn_thresholds.set_volume(0.5)
super_goblin_death = pygame.mixer.Sound('super_goblin_death.wav')
super_goblin_death.set_volume(0.7)
super_elf_attack = pygame.mixer.Sound('super_elf_attack.wav')
super_elf_attack.set_volume(0.1)
super_mag_attack1 = pygame.mixer.Sound('super_mag_attack1.wav')
super_mag_attack1.set_volume(0.5)

gear = pygame.image.load("gear.png")
gear = pygame.transform.scale(gear, (100, 100))

allies = set()
enemies = set()
classes = ["Elf", "Goblin", "Ork", "People"]
class_colors = {
    "Elf": Green,
    "Goblin": Yellow,
    "Ork": Red,
    "People": Blue
}

music_on = True
god_mode = False
paused = False
selected_god_unit_type = None
selected_object_to_move = None
selected_object_original_pos = None

class Organizm:
    def __init__(self):
        self.moc = 0
        self.zdrowie = 0
        self.napadnik = None

    def symbol(self):
        return '⬜'

    def ruch(self, x, y, plansza):
        #najpierw elfy atakują
        if isinstance(self, (Elf, Super_elf, Super_mag)):
            if self.atak_z_dystansu(x, y, plansza):
                return

#Jeśli doszło do ostrzału z dystansu - reaguj
        if self.napadnik:
            nx, ny = self.napadnik
            dx = nx - x
            dy = ny - y
            krok_x = 1 if dx > 0 else -1 if dx < 0 else 0
            krok_y = 1 if dy > 0 else -1 if dy < 0 else 0
            cel_x = x + krok_x
            cel_y = y + krok_y
            if 0 <= cel_x < len(plansza[0]) and 0 <= cel_y < len(plansza):
                cel = plansza[cel_y][cel_x]
                if isinstance(cel, Pustka):
                    plansza[cel_y][cel_x] = self
                    plansza[y][x] = Pustka()
                    # aktualizacja położenia super orka
                    if isinstance(self, (Super_ork, Super_mag)):
                        self._update_position(cel_x, cel_y)
                    kolor = kolor_terenu(self)
                    if kolor:
                        kolory_terenu[cel_y][cel_x] = kolor
                    return
                elif self.czy_wrog(cel):
                    self.walcz(cel)
                    if cel.zdrowie <= 0:
                        plansza[cel_y][cel_x] = self
                        plansza[y][x] = Pustka()
                        # aktualizacja położenia super orka
                        if isinstance(self, (Super_ork, Super_mag)):
                            self._update_position(cel_x, cel_y)
                    elif self.zdrowie <= 0:
                        plansza[y][x] = Pustka()
                    return
#Jeśli cel został osiągnięty lub zniknął, zresetuj współrzędne.
            if (nx, ny) == (x, y) or not isinstance(plansza[ny][nx], Organizm):
                self.napadnik = None

        kierunki = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(kierunki)
#Wyszukuje zasoby w pobliżu sąsiednich komórek
        for dx, dy in kierunki:
            nowy_x = x + dx
            nowy_y = y + dy
            if 0 <= nowy_x < len(plansza[0]) and 0 <= nowy_y < len(plansza):
                cel = plansza[nowy_y][nowy_x]
                if isinstance(self, (Elf, Goblin, Ork, People, Super_elf, Super_goblin, Super_ork, Super_mag)):
                    if isinstance(cel, (Wood, Stone, Roslina, Roslinozerca)):
                        if isinstance(cel, Wood):
                            self.zasoby["wood"] += 1
                        elif isinstance(cel, Stone):
                            self.zasoby["stone"] += 1
                        elif isinstance(cel, Roslina):
                            self.zasoby["plants"] += 1
                        elif isinstance(cel, Roslinozerca):
                            self.zasoby["meat"] += 1

                        plansza[nowy_y][nowy_x] = self
                        plansza[y][x] = Pustka()
                        # aktualizacja położenia super orka
                        if isinstance(self, (Super_ork, Super_mag)):
                            self._update_position(nowy_x, nowy_y)
                        kolor = kolor_terenu(self)
                        if kolor:
                            kolory_terenu[nowy_y][nowy_x] = kolor
                        return

#Jeśli wróg w pobliżu, atakuj
        for dx, dy in kierunki:
            nowy_x = x + dx
            nowy_y = y + dy
            if 0 <= nowy_x < len(plansza[0]) and 0 <= nowy_y < len(plansza):
                cel = plansza[nowy_y][nowy_x]
                if self.czy_wrog(cel):
                    self.walcz(cel)

                    if cel.zdrowie <= 0:
                        plansza[nowy_y][nowy_x] = self
                        plansza[y][x] = Pustka()
                        #aktualizacja położenia super orka
                        if isinstance(self, (Super_ork, Super_mag)):
                            self._update_position(nowy_x, nowy_y)
                        kolor = kolor_terenu(self)
                        if kolor:
                            kolory_terenu[nowy_y][nowy_x] = kolor
                    elif self.zdrowie <= 0:
                        if isinstance(self, Super_ork):
                            super_ork_dead.play()
                        elif isinstance(self, Super_goblin):
                            super_goblin_death.play()
                        plansza[y][x] = Pustka()
                    return

#Jeśli w pobliżu niema żadnego zasobu, przechodzi do pustej komórki
        for dx, dy in kierunki:
            nowy_x = x + dx
            nowy_y = y + dy
            if 0 <= nowy_x < len(plansza[0]) and 0 <= nowy_y < len(plansza):
                cel = plansza[nowy_y][nowy_x]
                if isinstance(cel, Pustka):
                    plansza[nowy_y][nowy_x] = self
                    plansza[y][x] = Pustka()
                    #aktualizacja położenia super orka
                    if isinstance(self, (Super_ork, Super_mag)):
                        self._update_position(nowy_x, nowy_y)
                    kolor = kolor_terenu(self)
                    if kolor:
                        kolory_terenu[nowy_y][nowy_x] = kolor
                    return

    def buduj_dom(self, x, y, plansza, kolory_terenu):
        if not isinstance(self, (Elf, Goblin, Ork, People, Super_elf, Super_goblin, Super_ork, Super_mag)):
            return

        kolor = kolor_terenu(self)

        if self.zasoby["wood"] >= 3 and self.zasoby["stone"] >= 1:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(plansza[0]) and 0 <= ny < len(plansza):
                    if isinstance(plansza[ny][nx], Pustka) and kolory_terenu[ny][nx] == kolor:
                        plansza[ny][nx] = Dom(kolor)
                        kolory_terenu[ny][nx] = kolor
                        self.zasoby["wood"] -= 3
                        self.zasoby["stone"] -= 1
                        return

    # Sprawdza, czy inny organizm to wróg, uwzględniając dyplomację
    def czy_wrog(self, inny):
        if not isinstance(self, (Elf, Goblin, Ork, People, Super_elf, Super_goblin, Super_ork, Super_mag)) or \
            not isinstance(inny, (Elf, Goblin, Ork, People, Super_elf, Super_goblin, Super_ork, Super_mag)):
            return False
    #Ta sama rasa nie jest wrogiem
        if type(self) == type(inny):
            return False

        #Sprawdzenie globalnych ustawień dyplomacji
        self_class_name = type(self).__name__
        inny_class_name = type(inny).__name__

        # Sprawdzenie, czy Super_elf jest sojusznikiem lub wrogiem zgodnie z zasadami dla Elfa
        if self_class_name == "Super_elf":
            self_class_name = "Elf"
        if inny_class_name == "Super_elf":
            inny_class_name = "Elf"

        if self_class_name == "Super_goblin":
            self_class_name = "Goblin"
        if inny_class_name == "Super_goblin":
            inny_class_name = "Goblin"

        if self_class_name == "Super_ork":
            self_class_name = "Ork"
        if inny_class_name == "Super_ork":
            inny_class_name = "Ork"

        if self_class_name == "Super_mag":
            self_class_name = "People"
        if inny_class_name == "Super_mag":
            inny_class_name = "People"

        if not allies and not enemies:
            return self_class_name != inny_class_name

        if self_class_name in allies and inny_class_name in allies:
            return False  # Sojusznicy nie są wrogami
        if self_class_name in enemies and inny_class_name in enemies:
            return False  # Wrogowie wobec siebie nie są wrogami (walczą z innymi)

        # Jeśli self jest sojusznikiem, a inny nie jest sojusznikiem, to inny jest wrogiem
        if self_class_name in allies and inny_class_name not in allies:
            return True
        if self_class_name in enemies and inny_class_name not in enemies:
            return True

        return False

#Zwalcza przeciwnika, modyfikując zdrowie
    def walcz(self, przeciwnik):
        przeciwnik.zdrowie -= self.moc
        if przeciwnik.zdrowie > 0:
            self.zdrowie -= przeciwnik.moc

def kolor_terenu(organizm):
    if isinstance(organizm, (Elf, Super_elf)):
        return Green
    elif isinstance(organizm, (Goblin, Super_goblin)):
        return Yellow
    elif isinstance(organizm, (Ork, Super_ork)):
        return Red
    elif isinstance(organizm, (People, Super_mag)):
        return Blue
    return None

class Pustka(Organizm):
    def symbol(self):
        return ""

class Elf(Organizm):
    def __init__(self):
        super().__init__()
        self.moc = 5
        self.zdrowie = 50
        self.max_zdrowie = 50
        self.zasoby = {"wood": 0, "stone": 0, "plants": 0, "meat": 0}
        self.symbol_ = random.choice(["🧝", "🧝‍♂️", "🧝‍♀️"])
    def symbol(self):
        return self.symbol_

    def atak_z_dystansu(self, x, y, plansza):
        zasieg = 5
        for dy in range(-zasieg, zasieg + 1):
            for dx in range(-zasieg, zasieg + 1):
                if dx == 0 and dy == 0:
                    continue
                cel_x, cel_y = x + dx, y + dy
                if 0 <= cel_x < len(plansza[0]) and 0 <= cel_y < len(plansza):
                    cel = plansza[cel_y][cel_x]
                    if self.czy_wrog(cel):
                        cel.napadnik = (x, y)
                        strzaly.append(Strzala(x, y, cel_x, cel_y, self))
                        return True
        return False

class Super_elf(Elf):
    def __init__(self):
        super().__init__()
        self.moc = 20
        self.zdrowie = 200
        self.max_zdrowie = 200
        self.zasoby = {"wood": 0, "stone": 0, "plants": 0, "meat": 0}
    def symbol(self):
        return "🏹"

    def atak_z_dystansu(self, x, y, plansza):
        zasieg = 10
        for dy in range(-zasieg, zasieg + 1):
            for dx in range(-zasieg, zasieg + 1):
                if dx == 0 and dy == 0:
                    continue
                cel_x, cel_y = x + dx, y + dy
                if 0 <= cel_x < len(plansza[0]) and 0 <= cel_y < len(plansza):
                    cel = plansza[cel_y][cel_x]
                    if self.czy_wrog(cel):
                        cel.napadnik = (x, y)
                        strzaly.append(Strzala(x, y, cel_x, cel_y, self))
                        super_elf_attack.play()
                        return True
        return False

class Strzala:
    def __init__(self, x, y, cel_x, cel_y, strzelec):
        self.x = x
        self.y = y
        self.cel_x = cel_x
        self.cel_y = cel_y
        self.strzelec = strzelec
        self.ikona = "'"
        self.kroki = 5
        self.licznik = 0

class Goblin(Organizm):
    def __init__(self):
        super().__init__()
        self.moc = 10
        self.zdrowie = 30
        self.max_zdrowie = 30
        self.zasoby = {"wood": 0, "stone": 0, "plants": 0, "meat": 0}
    def symbol(self):
        return "👺"

class Super_goblin(Goblin):
    def __init__(self):
        super().__init__()
        self.moc = 30
        self.zdrowie = 200
        self.max_zdrowie = 200
        self.zasoby = {"wood": 0, "stone": 0, "plants": 0, "meat": 0}
        self.wywolanie_zdrowia = set()

    def symbol(self):
        return "👹"

    def spawn_goblins_around(self, x, y, plansza, count=50, radius=6):
        puste_pola = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(plansza[0]) and 0 <= ny < len(plansza):
                    if isinstance(plansza[ny][nx], Pustka):
                        puste_pola.append((nx, ny))
        random.shuffle(puste_pola)
        for _ in range(min(count, len(puste_pola))):
            nx, ny = puste_pola.pop()
            plansza[ny][nx] = Goblin()
            kolory_terenu[ny][nx] = kolor_terenu(Goblin())

    def walcz(self, przeciwnik):
        przeciwnik.zdrowie -= self.moc
        if przeciwnik.zdrowie > 0:
            self.zdrowie -= przeciwnik.moc

        if self.zdrowie > 0:
            self.check_health_triggers(przeciwnik)

        if self.zdrowie <= 0:
            self.spawn_goblins_on_death(przeciwnik)

    def check_health_triggers(self, przeciwnik):
        thresholds = {150, 100, 50}
        for threshold in thresholds:
            if self.zdrowie <= threshold and threshold not in self.wywolanie_zdrowia:
                self.wywolanie_zdrowia.add(threshold)
                self.find_and_spawn(przeciwnik)
                goblin_spawn_thresholds.play()

    def spawn_goblins_on_death(self, przeciwnik):
        self.find_and_spawn(przeciwnik)

    def find_and_spawn(self, przeciwnik):
        for y in range(len(plansza)):
            for x in range(len(plansza[0])):
                if plansza[y][x] is self:
                    self.spawn_goblins_around(x, y, plansza)
                    return

class Ork(Organizm):
    def __init__(self):
        super().__init__()
        self.moc = 15
        self.zdrowie = 70
        self.max_zdrowie = 70
        self.zasoby = {"wood": 0, "stone": 0, "plants": 0, "meat": 0}
    def symbol(self):
        return "🧟‍♂️"

    def walcz(self, przeciwnik):
        przeciwnik.zdrowie -= self.moc
        if przeciwnik.zdrowie > 0:
            self.zdrowie -= przeciwnik.moc

class Super_ork(Ork):
    def __init__(self):
        super().__init__()
        self.moc = 25
        self.zdrowie = 250
        self.max_zdrowie = 250
        self.zasoby = {"wood": 0, "stone": 0, "plants": 0, "meat": 0}
        self.heal_range = 4
        self.current_x = -1
        self.current_y = -1
    def symbol(self):
        return "🪓"

    def _update_position(self, x, y):
        self.current_x = x
        self.current_y = y

    def leczenie_sojusznikow(self, x, y, plansza):
        for dy in range(-self.heal_range, self.heal_range + 1):
            for dx in range(-self.heal_range, self.heal_range + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(plansza[0]) and 0 <= ny < len(plansza):
                    cel = plansza[ny][nx]
                    if isinstance(cel, (Ork, Super_ork)):
                        if cel.zdrowie < cel.max_zdrowie:
                            cel.zdrowie = min(cel.zdrowie + 5, cel.max_zdrowie)

    def walcz(self, przeciwnik):
        przeciwnik.zdrowie -= self.moc
        if przeciwnik.zdrowie > 0:
            self.zdrowie -= przeciwnik.moc

class People(Organizm):
    def __init__(self):
        super().__init__()
        self.moc = 10
        self.zdrowie = 50
        self.max_zdrowie = 50
        self.zasoby = {"wood": 0, "stone": 0, "plants": 0, "meat": 0}
    def symbol(self):
        return "🧑"

class Super_mag(People):
    def __init__(self):
        super().__init__()
        self.moc = 30
        self.zdrowie = 180
        self.max_zdrowie = 180
        self.zasoby = {"wood": 0, "stone": 0, "plants": 0, "meat": 0}
        self.heal_range = 4
        self.current_x = -1
        self.current_y = -1
        self.zasieg = 5
    def symbol(self):
        return "🧙"

    def _update_position(self, x, y):
        self.current_x = x
        self.current_y = y

    def walcz(self, przeciwnik):
        przeciwnik.zdrowie -= self.moc
        if przeciwnik.zdrowie > 0:
            self.zdrowie -= przeciwnik.moc

    def leczenie_sojusznikow(self, x, y, plansza):
        for dy in range(-self.heal_range, self.heal_range + 1):
            for dx in range(-self.heal_range, self.heal_range + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(plansza[0]) and 0 <= ny < len(plansza):
                    cel = plansza[ny][nx]
                    if isinstance(cel, (People, Super_mag)):
                        if cel.zdrowie < cel.max_zdrowie:
                            cel.zdrowie = min(cel.zdrowie + 5, cel.max_zdrowie)

    def atak_z_dystansu(self, x, y, plansza):
        for dy in range(-self.zasieg, self.zasieg + 1):
            for dx in range(-self.zasieg, self.zasieg + 1):
                if dx == 0 and dy == 0:
                    continue
                cel_x, cel_y = x + dx, y + dy
                if 0 <= cel_x < len(plansza[0]) and 0 <= cel_y < len(plansza):
                    cel = plansza[cel_y][cel_x]
                    if self.czy_wrog(cel):
                        cel.napadnik = (x, y)
                        strzaly.append(Ogien(x, y, cel_x, cel_y, self))
                        super_mag_attack1.play()
                        return True
        return False

class Ogien:
    def __init__(self, x, y, cel_x, cel_y, strzelec):
        self.x = x
        self.y = y
        self.cel_x = cel_x
        self.cel_y = cel_y
        self.strzelec = strzelec
        self.ikona = "🔥"
        self.kroki = 7
        self.licznik = 0

class Wood(Organizm):
    def __init__(self):
        super().__init__()
    def symbol(self):
        return "🌳"

class Stone(Organizm):
    def __init__(self):
        super().__init__()
    def symbol(self):
        return "⛰️"

class Roslina(Organizm):
    def __init__(self):
        super().__init__()
    def symbol(self):
        return "🌾"

class Roslinozerca(Organizm):
    def __init__(self):
        super().__init__()
        self.symbol_ = random.choice(["🐔", "🐇", "🐑", "🐄", "🐷"])
    def symbol(self):
        return self.symbol_

class Dom(Organizm):
    def __init__(self, kolor):
        super().__init__()
        self.kolor = kolor
    def symbol(self):
        return "🏠"

class Szpital(Organizm):
    def __init__(self, kolor_rasy, is_starting_szpital=False):
        super().__init__()
        self.kolor_rasy = kolor_rasy #Kolor rasy, którą szpital leczy
        self.x = -1
        self.y = -1
        #Jeśli to szpital początkowy, leczy cały obszar 6x6
        #Jeśli utworzony w trybie boga, leczy wokół siebie (3 pola w każdą stronę)
        self.is_starting_szpital = is_starting_szpital
        self.heal_radius_dynamic = 3 #Promień leczenia dla dynamicznych szpitali

    def symbol(self):
        return "🏥"
    def ruch(self, x, y, plansza):
        pass

    def _update_position(self, x, y):
        self.x = x
        self.y = y

class FabrykaKomorek:
    @staticmethod
    def utworz_komorke(type, is_starting_szpital=False):
        if type == "Elf":
            return Elf()
        elif type == "Ork":
            return Ork()
        elif type == "People":
            return People()
        elif type == "Goblin":
            return Goblin()
        elif type == "Wood":
            return Wood()
        elif type == "Stone":
            return Stone()
        elif type == "Roslinozerca":
            return Roslinozerca()
        elif type == "Roslina":
            return Roslina()
        elif type == "Szpital":
            return Szpital(None, is_starting_szpital)
        elif type == "SuperElf":
            return Super_elf()
        elif type == "SuperGoblin":
            return Super_goblin()
        elif type == "SuperOrk":
            return Super_ork()
        elif type == "SuperMag":
            return Super_mag()
        else:
            return Pustka()

plansza = [[Pustka() for _ in range(rozmiar_okna_x)] for _ in range(rozmiar_okna_y)]
kolory_terenu = [[White for _ in range(rozmiar_okna_x)] for _ in range(rozmiar_okna_y)]
strzaly = []

def get_wolne_pola(x_start, y_start, size):
    pola = [(x, y) for y in range(y_start, y_start + size) for x in range(x_start, x_start + size)]
    random.shuffle(pola)
    return pola

def dodaj_obiekty(type, liczba, pola):
    for _ in range(min(liczba, len(pola))):
        x, y = random.choice(pola)
        pola.remove((x, y))
        plansza[y][x] = FabrykaKomorek.utworz_komorke(type)

def get_wszystkie_wolne_pola():
    pola = [(x, y)
            for y in range(rozmiar_okna_y)
            for x in range(rozmiar_okna_x)
            if type(plansza[y][x]) == Pustka]
    random.shuffle(pola)
    return pola

def policz_jednostki():
    liczby = {
        "Elf": 0,
        "Ork": 0,
        "Goblin": 0,
        "People": 0,
        "SuperElf": 0,
        "SuperGoblin": 0,
        "SuperOrk": 0,
        "SuperMag": 0
    }
    for y in range(rozmiar_okna_y):
        for x in range(rozmiar_okna_x):
            if isinstance(plansza[y][x], Elf):
                liczby["Elf"] += 1
            elif isinstance(plansza[y][x], Ork):
                liczby["Ork"] += 1
            elif isinstance(plansza[y][x], Goblin):
                liczby["Goblin"] += 1
            elif isinstance(plansza[y][x], People):
                liczby["People"] += 1
            elif isinstance(plansza[y][x], Super_elf):
                liczby["SuperElf"] += 1
            elif isinstance(plansza[y][x], Super_goblin):
                liczby["SuperGoblin"] += 1
            elif isinstance(plansza[y][x], Super_ork):
                liczby["SuperOrk"] += 1
            elif isinstance(plansza[y][x], Super_mag):
                liczby["SuperMag"] += 1
    return liczby

def wyczysc_terytorium(kolor_do_usuniecia):
    for y in range(rozmiar_okna_y):
        for x in range(rozmiar_okna_x):
            if kolory_terenu[y][x] == kolor_do_usuniecia:
                kolory_terenu[y][x] = White

def usun_domy_po_ostatnim_junicie(kolor):
    for y in range(rozmiar_okna_y):
        for x in range(rozmiar_okna_x):
            komorka = plansza[y][x]
            if isinstance(komorka, Dom) and komorka.kolor == kolor:
                plansza[y][x] = Pustka()
            if isinstance(komorka, Szpital) and komorka.kolor_rasy == kolor and komorka.is_starting_szpital:
                plansza[y][x] = Pustka()

def get_szpital_area_coords(szpital_color):
    if szpital_color == Green:
        return 0, 0
    elif szpital_color == Yellow:
        return rozmiar_okna_x - pole_size, 0
    elif szpital_color == Red:
        return 0, rozmiar_okna_y - pole_size
    elif szpital_color == Blue:
        return rozmiar_okna_x - pole_size, rozmiar_okna_y - pole_size
    return -1, -1

def settings_menu():
    global music_on
    settings_running = True

    #Rozmiary i pozycja okna
    menu_width = 400
    menu_height = 250
    menu_x = (szerokosc - menu_width) // 2
    menu_y = (wysokosc - menu_height) // 2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)

    music_button = pygame.Rect(menu_x + 100, menu_y + 80, 200, 50)
    back_button = pygame.Rect(menu_x + 100, menu_y + 160, 200, 50)

    while settings_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if music_button.collidepoint(event.pos):
                    music_on = not music_on
                    if music_on:
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(0.5)
                    else:
                        pygame.mixer.music.stop()
                if back_button.collidepoint(event.pos):
                    settings_running = False

        pygame.draw.rect(okno, White, menu_rect, border_radius=10)
        pygame.draw.rect(okno, Black, menu_rect, 3, border_radius=10)

        title_text = font_menu.render("Settings", True, Black)
        title_rect = title_text.get_rect(center=(menu_x + menu_width // 2, menu_y + 40))
        okno.blit(title_text, title_rect)

        music_text_display = "Music: On" if music_on else "Music: Off"
        music_button_color = (0, 255, 0) if music_on else (255, 0, 0)
        pygame.draw.rect(okno, music_button_color, music_button, border_radius=10)
        pygame.draw.rect(okno, Black, music_button, 3, border_radius=10)
        music_text_render = font.render(music_text_display, True, Black)
        music_text_rect = music_text_render.get_rect(center=music_button.center)
        okno.blit(music_text_render, music_text_rect)

        pygame.draw.rect(okno, (0, 0, 255), back_button, border_radius=10)
        pygame.draw.rect(okno, Black, back_button, 3, border_radius=10)
        back_text_render = font.render("Back", True, Black)
        back_text_rect = back_text_render.get_rect(center=back_button.center)
        okno.blit(back_text_render, back_text_rect)

        pygame.display.flip()

def zacznij_gre():
    global plansza, kolory_terenu, strzaly, wybrany_unit, wybrany_szpital, god_mode, paused, selected_god_unit_type, selected_object_to_move, selected_object_original_pos, delete_mode

    #Resetowanie stanu gry na początku
    plansza = [[Pustka() for _ in range(rozmiar_okna_x)] for _ in range(rozmiar_okna_y)]
    kolory_terenu = [[White for _ in range(rozmiar_okna_x)] for _ in range(rozmiar_okna_y)]
    strzaly = []
    wybrany_unit = None
    wybrany_szpital = None
    god_mode = False #Na początku gry tryb boga jest wyłączony
    paused = False
    selected_god_unit_type = None
    selected_object_to_move = None
    selected_object_original_pos = None
    delete_mode = False
    # Zapisujemy listę początkowych szpitali
    starting_hospitals = []

    startowa_area = {
        "Elf": {"coords": (0, 0), "color": Green},
        "Goblin": {"coords": (rozmiar_okna_x - pole_size, 0), "color": Yellow},
        "Ork": {"coords": (0, rozmiar_okna_y - pole_size), "color": Red},
        "People": {"coords": (rozmiar_okna_x - pole_size, rozmiar_okna_y - pole_size), "color": Blue}
    }

    poczatkowa_liczba_jednostek = {
        "Elf": 10,
        "Goblin": 20,
        "Ork": 10,
        "People": 10
    }

    for rasa, data in startowa_area.items():
        x_start, y_start = data["coords"]
        area_color = data["color"]

        # Ustaw kolor terytorium
        for y in range(y_start, y_start + pole_size):
            for x in range(x_start, x_start + pole_size):
                kolory_terenu[y][x] = area_color

        # Dodaj jednostki
        wolne_pola_rasy = get_wolne_pola(x_start, y_start, pole_size)
        dodaj_obiekty(rasa, poczatkowa_liczba_jednostek[rasa], wolne_pola_rasy)

        if rasa == "Elf" and wolne_pola_rasy:
            x_super_elf, y_super_elf = random.choice(wolne_pola_rasy)
            wolne_pola_rasy.remove((x_super_elf, y_super_elf))
            plansza[y_super_elf][x_super_elf] = FabrykaKomorek.utworz_komorke("SuperElf")

        if rasa == "Goblin" and wolne_pola_rasy:
            x_super_goblin, y_super_goblin = random.choice(wolne_pola_rasy)
            wolne_pola_rasy.remove((x_super_goblin, y_super_goblin))
            plansza[y_super_goblin][x_super_goblin] = FabrykaKomorek.utworz_komorke("SuperGoblin")

        if rasa == "Ork" and wolne_pola_rasy:
            x_super_ork, y_super_ork = random.choice(wolne_pola_rasy)
            wolne_pola_rasy.remove((x_super_ork, y_super_ork))
            super_ork_instance = FabrykaKomorek.utworz_komorke("SuperOrk")
            plansza[y_super_ork][x_super_ork] = super_ork_instance
            super_ork_instance._update_position(x_super_ork, y_super_ork)

        if rasa == "People" and wolne_pola_rasy:
            x_super_mag, y_super_mag = random.choice(wolne_pola_rasy)
            wolne_pola_rasy.remove((x_super_mag, y_super_mag))
            super_mag_instance = FabrykaKomorek.utworz_komorke("SuperMag")
            plansza[y_super_mag][x_super_mag] = super_mag_instance
            super_mag_instance._update_position(x_super_mag, y_super_mag)

        #Dodanie szpitala (jako początkowego)
        if wolne_pola_rasy:
            sx, sy = random.choice(wolne_pola_rasy)
            wolne_pola_rasy.remove((sx, sy))
            szpital = FabrykaKomorek.utworz_komorke("Szpital", is_starting_szpital=True)
            szpital.kolor_rasy = area_color
            plansza[sy][sx] = szpital
            szpital._update_position(sx, sy)
            starting_hospitals.append(szpital)

    wolne_pola = get_wszystkie_wolne_pola()
    dodaj_obiekty("Wood", 20, wolne_pola)
    dodaj_obiekty("Stone", 20, wolne_pola)
    dodaj_obiekty("Roslina", 20, wolne_pola)
    dodaj_obiekty("Roslinozerca", 20, wolne_pola)

    running = True
    licznik_klatek = 0

    if music_on:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.5)

    while running:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g: #Przełączanie trybu boga
                    god_mode = not god_mode
                    selected_god_unit_type = None #Resetowanie wyboru jednostki po wyjściu z trybu boga
                    selected_object_to_move = None
                    selected_object_original_pos = None
                    delete_mode = False
                if event.key == pygame.K_p: #Przełączanie pauzy
                    paused = not paused

                if god_mode:
                    if event.key == pygame.K_0:
                        delete_mode = not delete_mode
                        selected_god_unit_type = None
                    elif event.key == pygame.K_1:
                        selected_god_unit_type = "Elf"; delete_mode = False
                    elif event.key == pygame.K_2:
                        selected_god_unit_type = "Goblin"; delete_mode = False
                    elif event.key == pygame.K_3:
                        selected_god_unit_type = "Ork"; delete_mode = False
                    elif event.key == pygame.K_4:
                        selected_god_unit_type = "People"; delete_mode = False
                    elif event.key == pygame.K_5:
                        selected_god_unit_type = "SuperElf"; delete_mode = False
                    elif event.key == pygame.K_6:
                        selected_god_unit_type = "SuperGoblin"; delete_mode = False
                    elif event.key == pygame.K_7:
                        selected_god_unit_type = "SuperOrk"; delete_mode = False
                    elif event.key == pygame.K_8:
                        selected_god_unit_type = "SuperMag"; delete_mode = False
                    elif event.key == pygame.K_9:
                        selected_god_unit_type = "Szpital"; delete_mode = False
                    else:
                        selected_god_unit_type = None; delete_mode = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                grid_x = mouse_x // rozmiar_komorki
                grid_y = mouse_y // rozmiar_komorki
                if 0 <= grid_x < rozmiar_okna_x and 0 <= grid_y < rozmiar_okna_y:
                    organizm = plansza[grid_y][grid_x]

                    if god_mode:
                        if delete_mode:
                            if isinstance(organizm, (
                            Elf, Goblin, Ork, People, Super_elf, Super_goblin, Super_ork, Super_mag, Wood, Stone, Roslina, Roslinozerca, Dom, Szpital)):
                                plansza[grid_y][grid_x] = Pustka()
                                # Czyszczenie terenu, jeśli to nie jest zasób
                                if not isinstance(organizm, (Wood, Stone, Roslina, Roslinozerca)):
                                    kolory_terenu[grid_y][grid_x] = White

                        if event.button == 1: #Lewy przycisk myszy służy do wyboru obiektu do przeniesienia
                            if isinstance(organizm, (Elf, Goblin, Ork, People, Szpital, Super_elf, Super_goblin, Super_ork, Super_mag, Wood, Stone, Roslina, Roslinozerca, Dom)):
                                selected_object_to_move = organizm
                                selected_object_original_pos = (grid_x, grid_y)
                            else:
                                selected_object_to_move = None
                                selected_object_original_pos = None

                        elif event.button == 3: #Prawy przycisk myszy do dodawania jednostek lub przenoszenia
                            if selected_object_to_move:
                                if isinstance(plansza[grid_y][grid_x], Pustka): #Przenosimy tylko na puste pole
                                    #Zapisujemy starą pozycję do wyczyszczenia
                                    old_x, old_y = selected_object_original_pos
                                    plansza[grid_y][grid_x] = selected_object_to_move
                                    plansza[old_y][old_x] = Pustka() #Czyścimy starą pozycję

                                    # aktualizacja pozycji dla Super_ork, Super_mag oraz Szpital
                                    if isinstance(selected_object_to_move, (Super_ork, Super_mag, Szpital)):
                                        selected_object_to_move._update_position(grid_x, grid_y)
                                        #Jeśli szpital został przeniesiony, staje się "dynamiczny"
                                        if isinstance(selected_object_to_move, Szpital):
                                            selected_object_to_move.is_starting_szpital = False

                                    # Aktualizacja koloru terytorium
                                    kolor = kolor_terenu(selected_object_to_move)
                                    if kolor:
                                        kolory_terenu[grid_y][grid_x] = kolor
                                    selected_object_to_move = None
                                    selected_object_original_pos = None
                            elif selected_god_unit_type:
                                if isinstance(plansza[grid_y][grid_x], Pustka): # Dodajemy tylko na puste pole
                                    if selected_god_unit_type == "Szpital":
                                        current_territory_color = kolory_terenu[grid_y][grid_x] # Dla szpitala należy określić kolor rasy
                                        if current_territory_color in class_colors.values():
                                            new_szpital = FabrykaKomorek.utworz_komorke(selected_god_unit_type, is_starting_szpital=False)
                                            new_szpital.kolor_rasy = current_territory_color
                                            plansza[grid_y][grid_x] = new_szpital
                                            new_szpital._update_position(grid_x, grid_y)
                                            kolory_terenu[grid_y][grid_x] = current_territory_color# Upewnić się, że terytorium jest pokolorowane
                                    else:
                                        new_unit = FabrykaKomorek.utworz_komorke(selected_god_unit_type)
                                        plansza[grid_y][grid_x] = new_unit
                                        #Jeśli dodajemy jednostkę, zaktualizuj kolor terytorium, jeśli jest pusty
                                        kolor = kolor_terenu(new_unit)
                                        if kolor and kolory_terenu[grid_y][grid_x] == White:
                                            kolory_terenu[grid_y][grid_x] = kolor
                            else:
                                if isinstance(organizm, (Elf, Goblin, Ork, People, Super_elf, Super_goblin, Super_ork, Super_mag)):
                                    wybrany_unit = organizm
                                    wybrany_szpital = None
                                elif isinstance(organizm, Szpital):
                                    wybrany_szpital = organizm
                                    wybrany_unit = None
                                else:
                                    wybrany_unit = None
                                    wybrany_szpital = None
                    #Zwykła logika wyboru jednostek, jeśli tryb boga jest wyłączony
                    else:
                        if isinstance(organizm, (Elf, Goblin, Ork, People, Super_elf, Super_goblin, Super_ork, Super_mag)):
                            wybrany_unit = organizm
                            wybrany_szpital = None
                        elif isinstance(organizm, Szpital):
                            wybrany_szpital = organizm
                            wybrany_unit = None
                        else:
                            wybrany_unit = None
                            wybrany_szpital = None

        okno.fill(White)

        for y in range(rozmiar_okna_y):
            for x in range(rozmiar_okna_x):
                kolor = kolory_terenu[y][x]
                pygame.draw.rect(okno, kolor, (x * rozmiar_komorki, y * rozmiar_komorki, rozmiar_komorki, rozmiar_komorki))

                symbol = plansza[y][x].symbol()
                if symbol:
                    text = font.render(symbol, True, (0, 0, 0))
                    text_rect = text.get_rect(center=(
                        x * rozmiar_komorki + rozmiar_komorki // 2,
                        y * rozmiar_komorki + rozmiar_komorki // 2))
                    okno.blit(text, text_rect)

        if isinstance(wybrany_szpital, Szpital):
            if wybrany_szpital.is_starting_szpital:
                #Początkowy szpital
                szpital_x_start, szpital_y_start = get_szpital_area_coords(wybrany_szpital.kolor_rasy)
                if szpital_x_start != -1 and szpital_y_start != -1:
                    area_width = pole_size * rozmiar_komorki
                    area_height = pole_size * rozmiar_komorki
                    top_left_x = szpital_x_start * rozmiar_komorki
                    top_left_y = szpital_y_start * rozmiar_komorki

                    heal_surface_szpital = pygame.Surface((area_width, area_height), pygame.SRCALPHA)
                    pygame.draw.rect(heal_surface_szpital, Kolor_szpital, heal_surface_szpital.get_rect())
                    okno.blit(heal_surface_szpital, (top_left_x, top_left_y))
            # To dynamiczny szpital
            else:
                if wybrany_szpital.x != -1 and wybrany_szpital.y != -1:
                    szpital_x_on_grid = wybrany_szpital.x
                    szpital_y_on_grid = wybrany_szpital.y
                    heal_range_szpital = wybrany_szpital.heal_radius_dynamic
                    area_width_szpital = (2 * heal_range_szpital + 1) * rozmiar_komorki
                    area_height_szpital = (2 * heal_range_szpital + 1) * rozmiar_komorki
                    top_left_x_szpital = (szpital_x_on_grid - heal_range_szpital) * rozmiar_komorki
                    top_left_y_szpital = (szpital_y_on_grid - heal_range_szpital) * rozmiar_komorki

                    heal_surface_szpital = pygame.Surface((area_width_szpital, area_height_szpital), pygame.SRCALPHA)
                    pygame.draw.rect(heal_surface_szpital, Kolor_szpital, heal_surface_szpital.get_rect())
                    okno.blit(heal_surface_szpital, (top_left_x_szpital, top_left_y_szpital))

        # Podświetlenie wybranego obiektu w trybie boga
        if god_mode and selected_object_to_move and selected_object_original_pos:
            obszar_zaznaczenia = pygame.Rect(
                selected_object_original_pos[0] * rozmiar_komorki,
                selected_object_original_pos[1] * rozmiar_komorki, rozmiar_komorki, rozmiar_komorki
            )
            pygame.draw.rect(okno, (255, 0, 0), obszar_zaznaczenia, 3)

        # Wyświetlanie obszaru, w którym jednostka zostanie dodana w trybie boga
        if god_mode and selected_god_unit_type:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = mouse_x // rozmiar_komorki
            grid_y = mouse_y // rozmiar_komorki
            if 0 <= grid_x < rozmiar_okna_x and 0 <= grid_y < rozmiar_okna_y:
                obszar_wstawiania = pygame.Rect(grid_x * rozmiar_komorki, grid_y * rozmiar_komorki, rozmiar_komorki, rozmiar_komorki
                )
                pygame.draw.rect(okno, (0, 255, 0), obszar_wstawiania, 3)

        # Wyświetlanie obszaru leczenia Super_orka
        # Sprawdzamy, czy wybrana jednostka to Super_ork i czy jej współrzędne zostały zainicjalizowane
        if isinstance(wybrany_unit, Super_ork) and wybrany_unit.current_x != -1 and wybrany_unit.current_y != -1:
            super_ork_x = wybrany_unit.current_x
            super_ork_y = wybrany_unit.current_y
            heal_range = wybrany_unit.heal_range
            #Obliczamy rozmiary obszaru leczenia
            area_width = (2 * heal_range + 1) * rozmiar_komorki
            area_height = (2 * heal_range + 1) * rozmiar_komorki
            #Obliczamy rozmiary obszaru leczenia
            top_left_x = (super_ork_x - heal_range) * rozmiar_komorki
            top_left_y = (super_ork_y - heal_range) * rozmiar_komorki

            heal_surface = pygame.Surface((area_width, area_height), pygame.SRCALPHA)
            pygame.draw.rect(heal_surface, Kolor_szpital, heal_surface.get_rect())
            okno.blit(heal_surface, (top_left_x, top_left_y))

            # Wyświetlanie obszaru ataku Super_maga
        if isinstance(wybrany_unit, Super_mag) and wybrany_unit.current_x != -1 and wybrany_unit.current_y != -1:
            super_mag_x = wybrany_unit.current_x
            super_mag_y = wybrany_unit.current_y
            attack_range = wybrany_unit.zasieg
            area_width = (2 * attack_range + 1) * rozmiar_komorki
            area_height = (2 * attack_range + 1) * rozmiar_komorki
            top_left_x = (super_mag_x - attack_range) * rozmiar_komorki
            top_left_y = (super_mag_y - attack_range) * rozmiar_komorki

            attack_surface = pygame.Surface((area_width, area_height), pygame.SRCALPHA)
            pygame.draw.rect(attack_surface, (255, 0, 0, 80), attack_surface.get_rect())
            okno.blit(attack_surface, (top_left_x, top_left_y))

        if isinstance(wybrany_unit, Super_mag) and wybrany_unit.current_x != -1 and wybrany_unit.current_y != -1:
            super_mag_x = wybrany_unit.current_x
            super_mag_y = wybrany_unit.current_y
            heal_range = wybrany_unit.heal_range
            #Obliczamy rozmiary obszaru leczenia
            area_width = (2 * heal_range + 1) * rozmiar_komorki
            area_height = (2 * heal_range + 1) * rozmiar_komorki
            #Obliczamy rozmiary obszaru leczenia
            top_left_x = (super_mag_x - heal_range) * rozmiar_komorki
            top_left_y = (super_mag_y - heal_range) * rozmiar_komorki

            heal_surface = pygame.Surface((area_width, area_height), pygame.SRCALPHA)
            pygame.draw.rect(heal_surface, Kolor_szpital, heal_surface.get_rect())
            okno.blit(heal_surface, (top_left_x, top_left_y))

        liczby = policz_jednostki()
        if liczby["Elf"] == 0 and liczby["SuperElf"] == 0:
            wyczysc_terytorium(Green)
            usun_domy_po_ostatnim_junicie(Green)
        if liczby["Goblin"] == 0 and liczby["SuperGoblin"] == 0:
            wyczysc_terytorium(Yellow)
            usun_domy_po_ostatnim_junicie(Yellow)
        if liczby["Ork"] == 0 and liczby["SuperOrk"] == 0:
            wyczysc_terytorium(Red)
            usun_domy_po_ostatnim_junicie(Red)
        if liczby["People"] == 0 and liczby["SuperMag"] == 0:
            wyczysc_terytorium(Blue)
            usun_domy_po_ostatnim_junicie(Blue)

        tekst_statystyki = font_menu.render(f"Elf: {liczby['Elf'] + liczby['SuperElf']}  Goblin: {liczby['Goblin'] + liczby['SuperGoblin']}  Ork: {liczby['Ork'] + liczby['SuperOrk']}  People: {liczby['People'] + liczby['SuperMag']}", True, Black)
        lokalizacja_tekstu =tekst_statystyki.get_rect(center=(szerokosc // 2, 30))
        okno.blit(tekst_statystyki, lokalizacja_tekstu)

        god_mode_text = font.render(f"God mode: {'ON' if god_mode else 'OFF'} (G)", True, 0, (255, 255, 255))
        okno.blit(god_mode_text, (400, 50))
        paused_text = font.render(f"Pause: {'YES' if paused else 'NO'} (P)", True, 0, (255, 255, 255))
        okno.blit(paused_text, (600, 50))

        if god_mode and selected_god_unit_type:
            selected_unit_text = font.render(f"Dodaj: {selected_god_unit_type}", True, 0, (255, 255, 255))
            okno.blit(selected_unit_text, (750, 50))

        if god_mode and delete_mode:
            delete_mode_text = font.render("Tryb usuwania", True, (255, 0, 0), (255, 255, 255))
            okno.blit(delete_mode_text, (750, 50))

        for strzala in strzaly[:]:
            sx = strzala.x * rozmiar_komorki + rozmiar_komorki // 2
            sy = strzala.y * rozmiar_komorki + rozmiar_komorki // 2
            celx = strzala.cel_x * rozmiar_komorki + rozmiar_komorki // 2
            cely = strzala.cel_y * rozmiar_komorki + rozmiar_komorki // 2

            t = strzala.licznik / strzala.kroki
            px = int(sx + (celx - sx) * t)
            py = int(sy + (cely - sy) * t)

            text = font.render(strzala.ikona, True, (0, 0, 0))
            text_rect = text.get_rect(center=(px, py))
            okno.blit(text, text_rect)

            strzala.licznik += 1

            if strzala.licznik >= strzala.kroki:
                cel = plansza[strzala.cel_y][strzala.cel_x]
                if isinstance(cel, Organizm) and strzala.strzelec.czy_wrog(cel):
                    cel.zdrowie -= strzala.strzelec.moc
                    if isinstance(strzala.strzelec, Super_elf) and random.random() < 0.1:
                        cel.zdrowie -= 40
                    elif isinstance(strzala.strzelec, Super_mag) and random.random() < 0.1:
                        cel.zdrowie -= 30
                    if cel.zdrowie <= 0:
                        if isinstance(cel, Super_ork):
                            super_ork_dead.play()
                        elif isinstance(cel, Super_goblin):
                            super_goblin_death.play()
                        plansza[strzala.cel_y][strzala.cel_x] = Pustka()
                strzaly.remove(strzala)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = mouse_x // rozmiar_komorki
        grid_y = mouse_y // rozmiar_komorki

        if 0 <= grid_x < rozmiar_okna_x and 0 <= grid_y < rozmiar_okna_y:
            organizm = plansza[grid_y][grid_x]
            if isinstance(organizm, (Elf, Goblin, Ork, People, Szpital, Super_elf, Super_goblin, Super_ork, Super_mag)):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if wybrany_unit is not None:
            #Sprawdzamy, czy wybrana jednostka nadal znajduje się na planszy w zaktualizowanej lokalizacji
            znalezc_unit_na_plansze = False
            for y_check in range(rozmiar_okna_y):
                for x_check in range(rozmiar_okna_x):
                    if plansza[y_check][x_check] is wybrany_unit:
                        x_pos = x_check * rozmiar_komorki + rozmiar_komorki // 2
                        y_pos = y_check * rozmiar_komorki + rozmiar_komorki // 2

                        zdrowie_text = font.render(f"❤️ {wybrany_unit.zdrowie} 💥 {wybrany_unit.moc}", True, (255, 0, 0))
                        text_rect = zdrowie_text.get_rect(center=(x_pos, y_pos - rozmiar_komorki))
                        okno.blit(zdrowie_text, text_rect)
                        znalezc_unit_na_plansze = True
                        break
                if znalezc_unit_na_plansze:
                    break
            if not znalezc_unit_na_plansze:
                wybrany_unit = None

        pygame.display.flip()

        if not paused:
            licznik_klatek += 1
            if licznik_klatek % 30 == 0:
                for y in range(rozmiar_okna_y):
                    for x in range(rozmiar_okna_x):
                        komorka = plansza[y][x]
                        if isinstance(komorka, Szpital):
                            rasa_szpitala = None
                            for rasa_name, rasa_color in class_colors.items():
                                if rasa_color == komorka.kolor_rasy:
                                    rasa_szpitala = rasa_name
                                    break

                            if rasa_szpitala:
                                if komorka.is_starting_szpital:
                                    szpital_x_start, szpital_y_start = get_szpital_area_coords(komorka.kolor_rasy)
                                    if szpital_x_start != -1 and szpital_y_start != -1:
                                        for dy_heal in range(pole_size):  # range(6)
                                            for dx_heal in range(pole_size):
                                                px, py = szpital_x_start + dx_heal, szpital_y_start + dy_heal
                                                if 0 <= px < rozmiar_okna_x and 0 <= py < rozmiar_okna_y:
                                                    jednostka = plansza[py][px]
                                                    if (isinstance(jednostka, (Elf, Super_elf)) and rasa_szpitala == "Elf") or \
                                                            (isinstance(jednostka, (Goblin, Super_goblin)) and rasa_szpitala == "Goblin") or \
                                                            (isinstance(jednostka, (Ork, Super_ork)) and rasa_szpitala == "Ork") or \
                                                            (isinstance(jednostka, (People, Super_mag)) and rasa_szpitala == "People"):
                                                        if jednostka.zdrowie < jednostka.max_zdrowie:
                                                            jednostka.zdrowie = min(jednostka.zdrowie + 5, jednostka.max_zdrowie)
                                #To dynamiczny szpital
                                else:
                                    szpital_x_center = x
                                    szpital_y_center = y
                                    heal_range_szpital = komorka.heal_radius_dynamic

                                    for dy_heal in range(-heal_range_szpital, heal_range_szpital + 1):
                                        for dx_heal in range(-heal_range_szpital, heal_range_szpital + 1):
                                            px, py = szpital_x_center + dx_heal, szpital_y_center + dy_heal
                                            if 0 <= px < rozmiar_okna_x and 0 <= py < rozmiar_okna_y:
                                                jednostka = plansza[py][px]
                                                if (isinstance(jednostka, (Elf, Super_elf)) and rasa_szpitala == "Elf") or \
                                                        (isinstance(jednostka, (Goblin, Super_goblin)) and rasa_szpitala == "Goblin") or \
                                                        (isinstance(jednostka, (Ork, Super_ork)) and rasa_szpitala == "Ork") or \
                                                        (isinstance(jednostka, (People, Super_mag)) and rasa_szpitala == "People"):
                                                    if jednostka.zdrowie < jednostka.max_zdrowie:
                                                        jednostka.zdrowie = min(jednostka.zdrowie + 5, jednostka.max_zdrowie)

                        # Logika leczenia dla Super-Orka i Super-Maga
                        elif isinstance(komorka, (Super_ork, Super_mag)):
                            komorka.leczenie_sojusznikow(x, y, plansza)

                wspolrzedne = [(x, y) for y in range(rozmiar_okna_y) for x in range(rozmiar_okna_x)]
                random.shuffle(wspolrzedne)
                for x, y in wspolrzedne:
                    organizm = plansza[y][x]
                    if plansza[y][x] is organizm:
                        if isinstance(organizm, (Elf, Goblin, Ork, People, Roslinozerca, Super_elf, Super_goblin, Super_ork, Super_mag)):
                            # Przed ruchem zapisujemy starą pozycję, aby ją zaktualizować
                            old_x, old_y = x, y
                            organizm.ruch(x, y, plansza) #Jeśli organizm się przemieścił, jego stara komórka stała się Pustką, a nowa komórka zawiera teraz jego
                            #Obsługa śmierci po ruchu/walce
                            if organizm.zdrowie <= 0:
                                plansza[old_y][old_x] = Pustka() #Ustaw Pustkę na starej pozycji, jeśli jednostka zginęła przed ruchem
                            if isinstance(organizm, (Elf, Goblin, Ork, People, Super_elf, Super_goblin, Super_ork, Super_mag)):
                                organizm.buduj_dom(x, y, plansza, kolory_terenu)

                #Rozmnażanie
                for y in range(rozmiar_okna_y):
                    for x in range(rozmiar_okna_x):
                        organizm = plansza[y][x]

                        if isinstance(organizm, (Elf, Goblin, Ork, People, Super_elf, Super_goblin, Super_ork, Super_mag)):
                            if organizm.zasoby["plants"] > 0 or organizm.zasoby["meat"] > 0:
                                if isinstance(organizm, (Elf, Super_elf)): #Super Elf też może "rozmnażać" Elfy
                                    kolor_terenu_jednostki = Green
                                    typ = "Elf" #Super elf tworzy zwykłe Elfy
                                elif isinstance(organizm, (Goblin, Super_goblin)):
                                    kolor_terenu_jednostki = Yellow
                                    typ = "Goblin"
                                elif isinstance(organizm, (Ork, Super_ork)):
                                    kolor_terenu_jednostki = Red
                                    typ = "Ork"
                                elif isinstance(organizm, (People, Super_mag)):
                                    kolor_terenu_jednostki = Blue
                                    typ = "People"
                                else:
                                    continue

                                mozliwe_pola = [(ix, iy) for iy in range(rozmiar_okna_y)
                                            for ix in range(rozmiar_okna_x)
                                                if type(plansza[iy][ix]) == Pustka and kolory_terenu[iy][ix] == kolor_terenu_jednostki]

                                if mozliwe_pola:
                                    ix, iy = random.choice(mozliwe_pola)
                                    plansza[iy][ix] = FabrykaKomorek.utworz_komorke(typ)
                                    if organizm.zasoby["plants"] > 0:
                                        organizm.zasoby["plants"] -= 1
                                    elif organizm.zasoby["meat"] > 0:
                                        organizm.zasoby["meat"] -= 1

                #Dodawanie organizmów, gdy zabraknie zapasów
                liczba_roslinozercow = sum(isinstance(plansza[y][x], Roslinozerca) for y in range(rozmiar_okna_y) for x in range(rozmiar_okna_x))
                if liczba_roslinozercow <= 5:
                    wolne_pola = get_wszystkie_wolne_pola()
                    dodaj_obiekty("Roslinozerca", 5, wolne_pola)

                liczba_roslin = sum(isinstance(plansza[y][x], Roslina) for y in range(rozmiar_okna_y) for x in range(rozmiar_okna_x))
                if liczba_roslin <= 5:
                    wolne_pola = get_wszystkie_wolne_pola()
                    dodaj_obiekty("Roslina", 5, wolne_pola)

                liczba_drewna = sum(isinstance(plansza[y][x], Wood) for y in range(rozmiar_okna_y) for x in range(rozmiar_okna_x))
                if liczba_drewna <= 10:
                    wolne_pola = get_wszystkie_wolne_pola()
                    dodaj_obiekty("Wood", 5, wolne_pola)

                liczba_stone = sum(isinstance(plansza[y][x], Stone) for y in range(rozmiar_okna_y) for x in range(rozmiar_okna_x))
                if liczba_stone <= 10:
                    wolne_pola = get_wszystkie_wolne_pola()
                    dodaj_obiekty("Stone", 5, wolne_pola)

    pygame.quit()

def diplomacy_menu():
    global allies, enemies, music_on

    menu_running = True

    if music_on:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.5)

    while menu_running:
        okno.blit(tlo, (0, 0))
        title_text = font_menu.render("Wybierz Sojusze i Wrogów", True, Black)
        title_rect = title_text.get_rect(center=(szerokosc // 2, 50))
        okno.blit(title_text, title_rect)

        gear_button = gear.get_rect(topright=(szerokosc - 20, 20))
        okno.blit(gear, gear_button)

        # Wybór sojuszników
        ally_text = font_menu.render("Sojusznicy:", True, Black)
        okno.blit(ally_text, (350, 120))
        for i, cls in enumerate(classes):
            button_rect = pygame.Rect(350, 170 + i * 50, 200, 40) #400 od lewej, 170 od góry, 50 w dół od przycisku, 200 to szerokość przycisku, 40 wysokość
            color = (0,255,0) if cls in allies else Gray
            pygame.draw.rect(okno, color, button_rect, border_radius=10)
            pygame.draw.rect(okno, Black, button_rect, 2, border_radius=10)
            class_text = font.render(cls, True, Black)
            class_text_rect = class_text.get_rect(center=button_rect.center)
            okno.blit(class_text, class_text_rect)

        # Wybór wrogów
        enemy_text = font_menu.render("Wrogowie:", True, Black)
        okno.blit(enemy_text, (700, 120))
        for i, cls in enumerate(classes):
            button_rect = pygame.Rect(700, 170 + i * 50, 200, 40)
            color = (255,0,0) if cls in enemies else Gray
            pygame.draw.rect(okno, color, button_rect, border_radius=10)
            pygame.draw.rect(okno, Black, button_rect, 2, border_radius=10)
            class_text = font.render(cls, True, Black)
            class_text_rect = class_text.get_rect(center=button_rect.center)
            okno.blit(class_text, class_text_rect)

        # Przycisk "Rozpocznij grę"
        start_button_rect = pygame.Rect(szerokosc // 2 - 100, wysokosc - 300, 200, 50)
        pygame.draw.rect(okno, (255,0,0), start_button_rect, border_radius=15)
        pygame.draw.rect(okno, Black, start_button_rect, 2, border_radius=15)
        start_text = font_menu.render("Start", True, Black)
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        okno.blit(start_text, start_text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # Obsługa przycisku "Settings"
                if gear_button.collidepoint(mouse_pos):
                    settings_menu()

                # Obsługa kliknięć przycisków sojuszników
                for i, cls in enumerate(classes):
                    button_rect = pygame.Rect(350, 170 + i * 50, 200, 40)
                    if button_rect.collidepoint(mouse_pos):
                        if cls in allies:
                            allies.remove(cls)
                        else:
                            allies.add(cls)
                        # Upewnij się, że nie może być jednocześnie sojusznikiem i wrogiem
                        if cls in enemies:
                            enemies.remove(cls)

                # Obsługa kliknięć przycisków wrogów
                for i, cls in enumerate(classes):
                    button_rect = pygame.Rect(700, 170 + i * 50, 200, 40)
                    if button_rect.collidepoint(mouse_pos):
                        if cls in enemies:
                            enemies.remove(cls)
                        else:
                            enemies.add(cls)
                        # Upewnij się, że nie może być jednocześnie sojusznikiem i wrogiem
                        if cls in allies:
                            allies.remove(cls)

                # Obsługa przycisku "Rozpocznij grę"
                if start_button_rect.collidepoint(mouse_pos):
                    menu_running = False

# Uruchomienie najpierw menu dyplomacji a potem grę
diplomacy_menu()
zacznij_gre()