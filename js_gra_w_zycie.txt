class Komorka {
        constructor(zywa = false) { this.zywa = zywa; }
        zmien_stan(stan) { this.zywa = stan; }
    }
    class ZywaKomorka extends Komorka { constructor() { super(true); } }
    class MartwaKomorka extends Komorka { constructor() { super(false); } }

    class FabrykaKomorek {
        static utworz_komorke(typ) {
            return typ === "zywa" ? new ZywaKomorka() : new MartwaKomorka();
        }
    }

    class Plansza {
        static _instancja = null;
        static SZEROKOSC = 20;
        static WYSOKOSC = 20;

        constructor(szerokosc = 10, wysokosc = 10) {
            if (Plansza._instancja) return Plansza._instancja;
            this.szerokosc = szerokosc;
            this.wysokosc = wysokosc;
            this.komorki = Array.from({ length: wysokosc }, () =>
                Array.from({ length: szerokosc }, () => FabrykaKomorek.utworz_komorke("martwa"))
            );
            Plansza._instancja = this;
        }

        ustaw_komorke(x, y, komorka) {
            if (0 <= x && x < this.szerokosc && 0 <= y && y < this.wysokosc) {
                this.komorki[y][x] = komorka;
            }
        }

        pobierz_komorke(x, y) {
            if (0 <= x && x < this.szerokosc && 0 <= y && y < this.wysokosc) {
                return this.komorki[y][x];
            }
            return FabrykaKomorek.utworz_komorke("martwa");
        }
    }

    class Obserwator { aktualizuj(plansza) {} }

    class GUIWidok extends Obserwator {
        constructor(canvasId) {
            super();
            this.canvas = document.getElementById(canvasId);
            this.ctx = this.canvas.getContext('2d');
            this.rozmiarKomorki = 20;

            this.canvas.width = Plansza.SZEROKOSC * this.rozmiarKomorki;
            this.canvas.height = Plansza.WYSOKOSC * this.rozmiarKomorki;
        }

        aktualizuj(plansza) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

            for (let y = 0; y < plansza.wysokosc; y++) {
                for (let x = 0; x < plansza.szerokosc; x++) {
                    const komorka = plansza.pobierz_komorke(x, y);
                    
                    this.ctx.fillStyle = komorka.zywa ? '#0040ff' : '#ffffff';
                    this.ctx.fillRect(
                        x * this.rozmiarKomorki, 
                        y * this.rozmiarKomorki, 
                        this.rozmiarKomorki - 1, 
                        this.rozmiarKomorki - 1
                    );
                    
                    this.ctx.strokeStyle = '#e0e0e0';
                    this.ctx.strokeRect(
                        x * this.rozmiarKomorki, 
                        y * this.rozmiarKomorki, 
                        this.rozmiarKomorki, 
                        this.rozmiarKomorki
                    );
                }
            }
        }
    }

    class Symulacja {
        constructor(plansza, obserwator) {
            this.plansza = plansza;
            this.obserwator = obserwator;
        }

        policz_sasiadow(x, y) {
            let suma = 0;
            for (let delta_x = -1; delta_x <= 1; delta_x++) {
                for (let delta_y = -1; delta_y <= 1; delta_y++) {
                    if (delta_x === 0 && delta_y === 0) continue;
                    if (this.plansza.pobierz_komorke(x + delta_x, y + delta_y).zywa) {
                        suma++;
                    }
                }
            }
            return suma;
        }

        aktualizuj() {
            const nowe_stany = [];
            for (let y = 0; y < this.plansza.wysokosc; y++) {
                const wiersz = [];
                for (let x = 0; x < this.plansza.szerokosc; x++) {
                    const komorka = this.plansza.pobierz_komorke(x, y);
                    const sasiedzi = this.policz_sasiadow(x, y);
                    if (komorka.zywa) {
                        wiersz.push(sasiedzi === 2 || sasiedzi === 3);
                    } else {
                        wiersz.push(sasiedzi === 3);
                    }
                }
                nowe_stany.push(wiersz);
            }

            for (let y = 0; y < this.plansza.wysokosc; y++) {
                for (let x = 0; x < this.plansza.szerokosc; x++) {
                    this.plansza.komorki[y][x].zmien_stan(nowe_stany[y][x]);
                }
            }
            this.obserwator.aktualizuj(this.plansza);
        }
    }

    const plansza = new Plansza(Plansza.SZEROKOSC, Plansza.WYSOKOSC);
    const widok = new GUIWidok('gameCanvas');
    const symulacja = new Symulacja(plansza, widok);

    function restartGry() {
        for (let x = 0; x < plansza.szerokosc; x++) {
            for (let y = 0; y < plansza.wysokosc; y++) {
                if (Math.random() < 0.5) {
                    plansza.ustaw_komorke(x, y, FabrykaKomorek.utworz_komorke("zywa"));
                } else {
                    plansza.ustaw_komorke(x, y, FabrykaKomorek.utworz_komorke("martwa"));
                }
            }
        }
        widok.aktualizuj(plansza);
    }

    document.getElementById('gameCanvas').addEventListener('click', restartGry);

    restartGry();

    setInterval(() => { symulacja.aktualizuj(); }, 100);