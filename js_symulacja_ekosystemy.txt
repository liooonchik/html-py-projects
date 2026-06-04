const ROZMIAR_OKNA = 30;
const MAX_GENERACJI = 300;

function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

class Organizm {
    constructor() {
        this.wiek = 0;
        this.energia = 0;
    }
    symbol() { return '⬜'; }
    generacja(x, y, plansza) { this.wiek++; }
    
    znalezc_sasiadow(x, y, plansza) {
        let sasiedzi = [];
        for (let delta_x = -1; delta_x <= 1; delta_x++) {
            for (let delta_y = -1; delta_y <= 1; delta_y++) {
                if (delta_x === 0 && delta_y === 0) continue;
                let nowy_x = x + delta_x;
                let nowy_y = y + delta_y;
                if (nowy_x >= 0 && nowy_x < ROZMIAR_OKNA && nowy_y >= 0 && nowy_y < ROZMIAR_OKNA) {
                    sasiedzi.push({x: nowy_x, y: nowy_y, organizm: plansza[nowy_x][nowy_y]});
                }
            }
        }
        return shuffle(sasiedzi);
    }
}

class Pustka extends Organizm {
    symbol() { return "⬜"; }
}

class Roslina extends Organizm {
    constructor() { super(); this.energia = 1; }
    symbol() { return "🥕"; }
    generacja(x, y, plansza) {
        this.wiek++;
        if (this.energia < 10) this.energia++;

        let liczba_roslin = 0;
        for (let r = 0; r < ROZMIAR_OKNA; r++) {
            for (let c = 0; c < ROZMIAR_OKNA; c++) {
                if (plansza[r][c] instanceof Roslina) liczba_roslin++;
            }
        }
        let max_roslin = Math.floor((ROZMIAR_OKNA * ROZMIAR_OKNA) / 2);

        if (this.wiek >= 4 && liczba_roslin < max_roslin) {
            for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
                if (sasiad.organizm instanceof Pustka) {
                    plansza[sasiad.x][sasiad.y] = new Roslina();
                    break;
                }
            }
        }
    }
}

class Roslinozerca extends Organizm {
    constructor() { super(); this.energia = 8; }
    symbol() { return "🐇"; }
    generacja(x, y, plansza) {
        this.wiek++;
        if (this.energia <= 0) {
            for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
                if (sasiad.organizm instanceof Roslina) {
                    this.energia += 2;
                    plansza[sasiad.x][sasiad.y] = new Pustka();
                    break;
                }
            }
            if (this.wiek > 15) { plansza[x][y] = new Pustka(); return; }
        }
        this.energia--;
        let ruch = false;

        for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
            if (sasiad.organizm instanceof Roslina) {
                this.energia += 2;
                plansza[sasiad.x][sasiad.y] = this;
                plansza[x][y] = new Pustka();
                ruch = true;
                break;
            }
        }

        if (!ruch) {
            for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
                if (sasiad.organizm instanceof Pustka) {
                    this.energia--;
                    plansza[sasiad.x][sasiad.y] = this;
                    plansza[x][y] = new Pustka();
                    break;
                }
            }
        }

        if (this.wiek >= 4 && this.energia >= 4) {
            for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
                if (sasiad.organizm instanceof Roslinozerca && sasiad.organizm.wiek >= 4 && sasiad.organizm.energia >= 4) {
                    for (let p of this.znalezc_sasiadow(x, y, plansza)) {
                        if (p.organizm instanceof Pustka) {
                            plansza[p.x][p.y] = new Roslinozerca();
                            break;
                        }
                    }
                    break;
                }
            }
        }
        if (this.wiek > 15) plansza[x][y] = new Pustka();
    }
}

class Miesozerca extends Organizm {
    constructor() { super(); this.energia = 12; }
    symbol() { return "🐺"; }
    generacja(x, y, plansza) {
        this.wiek++;
        if (this.energia <= 0) {
            for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
                if (sasiad.organizm instanceof Roslinozerca) {
                    this.energia += 9;
                    plansza[sasiad.x][sasiad.y] = new Pustka();
                    break;
                }
            }
            if (this.wiek > 25) { plansza[x][y] = new Pustka(); return; }
        }
        this.energia -= 2;
        let ruch = false;

        for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
            if (sasiad.organizm instanceof Roslinozerca) {
                this.energia += 9;
                plansza[sasiad.x][sasiad.y] = this;
                plansza[x][y] = new Pustka();
                ruch = true;
                break;
            }
        }

        if (!ruch) {
            for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
                if (sasiad.organizm instanceof Pustka) {
                    this.energia -= 2;
                    plansza[sasiad.x][sasiad.y] = this;
                    plansza[x][y] = new Pustka();
                    break;
                }
            }
        }

        if (this.wiek >= 5 && this.energia >= 10) {
            for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
                if (sasiad.organizm instanceof Miesozerca && sasiad.organizm.wiek >= 5 && sasiad.organizm.energia >= 10) {
                    for (let p of this.znalezc_sasiadow(x, y, plansza)) {
                        if (p.organizm instanceof Pustka) {
                            plansza[p.x][p.y] = new Miesozerca();
                            break;
                        }
                    }
                    break;
                }
            }
        }
        if (this.wiek > 25) plansza[x][y] = new Pustka();
    }
}

class Wszystkozerca extends Organizm {
    constructor() { super(); this.energia = 10; }
    symbol() { return "🐻"; }
    generacja(x, y, plansza) {
        this.wiek++;
        if (this.energia <= 0) {
            for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
                if (sasiad.organizm instanceof Roslina) {
                    this.energia += 3;
                    plansza[sasiad.x][sasiad.y] = new Pustka();
                    break;
                } else if (sasiad.organizm instanceof Miesozerca) {
                    this.energia += 7;
                    plansza[sasiad.x][sasiad.y] = new Pustka();
                    break;
                }
            }
            if (this.wiek > 30) { plansza[x][y] = new Pustka(); return; }
        }
        this.energia -= 1;
        let ruch = false;

        for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
            if (sasiad.organizm instanceof Roslina) {
                this.energia += 3;
                plansza[sasiad.x][sasiad.y] = this;
                plansza[x][y] = new Pustka();
                ruch = true;
                break;
            } else if (sasiad.organizm instanceof Miesozerca) {
                this.energia += 7;
                plansza[sasiad.x][sasiad.y] = this;
                plansza[x][y] = new Pustka();
                ruch = true;
                break;
            }
        }

        if (!ruch) {
            for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
                if (sasiad.organizm instanceof Pustka) {
                    this.energia -= 1;
                    plansza[sasiad.x][sasiad.y] = this;
                    plansza[x][y] = new Pustka();
                    break;
                }
            }
        }

        if (this.wiek >= 5 && this.energia >= 8) {
            for (let sasiad of this.znalezc_sasiadow(x, y, plansza)) {
                if (sasiad.organizm instanceof Wszystkozerca && sasiad.organizm.wiek >= 5 && sasiad.organizm.energia >= 8) {
                    for (let p of this.znalezc_sasiadow(x, y, plansza)) {
                        if (p.organizm instanceof Pustka) {
                            plansza[p.x][p.y] = new Wszystkozerca();
                            break;
                        }
                    }
                    break;
                }
            }
        }
        if (this.wiek > 30) plansza[x][y] = new Pustka();
    }
}

class FabrykaKomorek {
    static utworz_komorke(type) {
        if (type === "Roslina") return new Roslina();
        if (type === "Roslinozerca") return new Roslinozerca();
        if (type === "Miesozerca") return new Miesozerca();
        if (type === "Wszystkozerca") return new Wszystkozerca();
        return new Pustka();
    }
}

class GUIWidok {
    constructor() {
        this.container = document.getElementById('grid-container');
        this.label = document.getElementById('generation-label');
        this.cells = [];
        
        for (let r = 0; r < ROZMIAR_OKNA; r++) {
            this.cells[r] = [];
            for (let c = 0; c < ROZMIAR_OKNA; c++) {
                let cell = document.createElement('div');
                cell.className = 'cell';
                this.container.appendChild(cell);
                this.cells[r][c] = cell;
            }
        }
    }
    aktualizuj(plansza, numer_generacji = 0) {
        this.label.innerText = `Generation: ${numer_generacji}`;
        for (let r = 0; r < ROZMIAR_OKNA; r++) {
            for (let c = 0; c < ROZMIAR_OKNA; c++) {
                this.cells[r][c].innerText = plansza[r][c].symbol();
            }
        }
    }
}

class Symulacja {
    constructor(plansza, widok) {
        this.plansza = plansza
        this.widok = widok;
        this.generacja = 0;
        this.startowe_ilosci = {
            "Roslina": 1,
            "Roslinozerca": 20,
            "Miesozerca": 10,
            "Wszystkozerca": 3
        };
        
        this.initCharts();
    }

    initCharts() {
        this.lineChart = new Chart(document.getElementById('lineChart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: 'Plants', data: [], borderColor: 'green', tension: 0.1, pointRadius: 0 },
                    { label: 'Herbivores', data: [], borderColor: 'blue', tension: 0.1, pointRadius: 0 },
                    { label: 'Carnivores', data: [], borderColor: 'red', tension: 0.1, pointRadius: 0 },
                    { label: 'Omnivores', data: [], borderColor: 'orange', tension: 0.1, pointRadius: 0 }
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Population line chart' } } }
        });

        this.pieChart = new Chart(document.getElementById('pieChart'), {
            type: 'pie',
            data: {
                labels: ['Plants', 'Herbivores', 'Carnivores', 'Omnivores'],
                datasets: [{ data: [0, 0, 0, 0], backgroundColor: ['green', 'blue', 'red', 'orange'] }]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Population pie chart' } } }
        });
    }

    aktualizuj() {
        if (this.generacja >= MAX_GENERACJI) {
            clearInterval(timer);
            console.log("Simulation completed after 300 generations");
            return;
        }

        let kierunek = [];
        for (let r = 0; r < ROZMIAR_OKNA; r++) {
            for (let c = 0; c < ROZMIAR_OKNA; c++) {
                kierunek.push({x: r, y: c});
            }
        }
        shuffle(kierunek);

        for (let pos of kierunek) {
            this.plansza[pos.x][pos.y].generacja(pos.x, pos.y, this.plansza);
        }

        this.generacja++;
        this.dodaj_brakujace_klasy();
        this.widok.aktualizuj(this.plansza, this.generacja);
        this.updateDataAndCharts();
    }

    updateDataAndCharts() {
        let counts = { Roslina: 0, Roslinozerca: 0, Miesozerca: 0, Wszystkozerca: 0 };

        for (let r = 0; r < ROZMIAR_OKNA; r++) {
            for (let c = 0; c < ROZMIAR_OKNA; c++) {
                let org = this.plansza[r][c];
                if (org instanceof Roslina) counts.Roslina++;
                else if (org instanceof Roslinozerca) counts.Roslinozerca++;
                else if (org instanceof Miesozerca) counts.Miesozerca++;
                else if (org instanceof Wszystkozerca) counts.Wszystkozerca++;
            }
        }

        this.lineChart.data.labels.push(this.generacja);
        this.lineChart.data.datasets[0].data.push(counts.Roslina);
        this.lineChart.data.datasets[1].data.push(counts.Roslinozerca);
        this.lineChart.data.datasets[2].data.push(counts.Miesozerca);
        this.lineChart.data.datasets[3].data.push(counts.Wszystkozerca);
        this.lineChart.update();

        this.pieChart.data.datasets[0].data = [counts.Roslina, counts.Roslinozerca, counts.Miesozerca, counts.Wszystkozerca];
        this.pieChart.update();
    }

    dodaj_brakujace_klasy() {
        let klasy = { "Roslina": false, "Roslinozerca": false, "Miesozerca": false, "Wszystkozerca": false };

        for (let r = 0; r < ROZMIAR_OKNA; r++) {
            for (let c = 0; c < ROZMIAR_OKNA; c++) {
                let obj = this.plansza[r][c];
                if (obj instanceof Roslina) klasy["Roslina"] = true;
                else if (obj instanceof Roslinozerca) klasy["Roslinozerca"] = true;
                else if (obj instanceof Miesozerca) klasy["Miesozerca"] = true;
                else if (obj instanceof Wszystkozerca) klasy["Wszystkozerca"] = true;
            }
        }

        for (let klasa in klasy) {
            if (!klasy[klasa]) {
                let wolne_pola = [];
                for (let r = 0; r < ROZMIAR_OKNA; r++) {
                    for (let c = 0; c < ROZMIAR_OKNA; c++) {
                        if (this.plansza[r][c] instanceof Pustka) wolne_pola.push({x: r, y: c});
                    }
                }
                
                let ilosc_do_dodania = this.startowe_ilosci[klasa];
                for (let i = 0; i < ilosc_do_dodania; i++) {
                    if (wolne_pola.length > 0) {
                        let idx = Math.floor(Math.random() * wolne_pola.length);
                        let pos = wolne_pola.splice(idx, 1)[0];
                        this.plansza[pos.x][pos.y] = FabrykaKomorek.utworz_komorke(klasa);
                    }
                }
            }
        }
    }
}

let plansza = [];
let wolne_pola = [];
for (let r = 0; r < ROZMIAR_OKNA; r++) {
    plansza[r] = [];
    for (let c = 0; c < ROZMIAR_OKNA; c++) {
        plansza[r][c] = new Pustka();
        wolne_pola.push({x: r, y: c});
    }
}

function dodaj_objekty(type, liczba) {
    for (let i = 0; i < liczba; i++) {
        if (wolne_pola.length > 0) {
            let idx = Math.floor(Math.random() * wolne_pola.length);
            let pos = wolne_pola.splice(idx, 1)[0];
            plansza[pos.x][pos.y] = FabrykaKomorek.utworz_komorke(type);
        }
    }
}

dodaj_objekty("Roslina", 1);
dodaj_objekty("Roslinozerca", 20);
dodaj_objekty("Miesozerca", 10);
dodaj_objekty("Wszystkozerca", 3);

const widok = new GUIWidok();
const symulacja = new Symulacja(plansza, widok);

widok.aktualizuj(plansza, 0);
const timer = setInterval(() => {
    symulacja.aktualizuj();
}, 600);