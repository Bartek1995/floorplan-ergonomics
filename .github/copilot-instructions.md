# Instrukcje dla Asystenta AI – floorplan-ergonomics

## Django 5.2 + Django REST Framework + Vue 3 + TypeScript + PrimeVue

*Język odpowiedzi: ZAWSZE po polsku*

---

## 0. Cel dokumentu (AKTUALIZACJA – MODEL PRODUKTOWY)

Ten dokument definiuje **precyzyjne zasady generowania kodu i analiz** dla aplikacji *floorplan-ergonomics*, której celem jest **wsparcie decyzji zakupowej mieszkania poprzez analizę codziennych scenariuszy użytkowania**.

### Model działania aplikacji (kluczowy)

> **Użytkownik wrzuca rzut mieszkania → ustala skalę → obrysowuje ściany → zaznacza kilka punktów funkcjonalnych → system automatycznie wyznacza trasy i generuje analizę.**

Użytkownik:

* ❌ nie projektuje mieszkania
* ❌ nie rysuje tras
* ❌ nie liczy ręcznie żadnych metryk

System:

* automatycznie wyznacza najkrótsze trasy pomiędzy punktami
* analizuje powtarzalne scenariusze dnia
* zwraca **czytelny werdykt decyzyjny**

---

## 0.2 **ZASADA STYLOWANIA FRONTEND'U - WAŻNE!**

### ❌ **NIE DODAWAJ RĘCZNIE:**
- `bg-*` (background colors)
- `text-*` (text colors)  
- `border-*` (border colors)
- `hover:*` (hover effects)
- `p-*`, `m-*` (padding/margin - poza wyjątkami)
- Żadnych niestandardowych CSS klas

### ✅ **ZAWSZE UŻYWAJ TYLKO:**
- **PrimeVue komponenty** (Card, Button, Dialog, DataTable, etc.)
- **Tailwind utility** TYLKO dla layoutu (grid, flex, gap)
- **PrimeVue theme** automatycznie obsługuje kolory i style

### Reguła:
> **Komponenty PrimeVue same decydują o kolorach, rozmiarach i efektach. My tylko układamy layout.**

---

## 0.1 Środowisko i komendy (Windows PowerShell) – AKTUALIZACJA (AKTYWACJA venv)

### Backend (Django) – zawsze aktywuj venv z `backend/venv/Scripts/Activate.ps1`

**Zasada:** w terminalu PowerShell pracujemy „w katalogu backend” i **aktywujemy venv** zamiast wołać bezpośrednio `python.exe`.

```powershell
# 1) Przejdź do backendu
Set-Location C:\\Projects\\floorplan-ergonomics\\backend

# 2) Aktywuj venv (PowerShell)
. .\\venv\\Scripts\\Activate.ps1

# 3) Sprawdź, że używasz venv
python -c "import sys; print(sys.executable)"

# 4) Komendy Django
python manage.py runserver 0.0.0.0:8000
python manage.py makemigrations
python manage.py migrate --no-input
python manage.py shell
```

### Frontend (Vue/Vite)

```powershell
Set-Location C:\\Projects\\floorplan-ergonomics\\frontend
npm install
npm run dev
```

---

## 1. Zasady domenowe (NOWE – KLUCZOWE)

### 1.1 Rola użytkownika

Użytkownik wykonuje **wyłącznie czynności deklaratywne**:

* wrzuca rzut mieszkania (PDF / JPG)
* ustala skalę (2 punkty + wymiar w cm)
* obrysowuje ściany (polilinia)
* zaznacza punkty funkcjonalne (ikony)

Wszelka analiza, logika przejść i obliczenia są **100% po stronie systemu**.

---

### 1.2 Punkty funkcjonalne (ZAMIANA „OBIEKTÓW”)

Aplikacja **nie operuje na dowolnych obiektach**, tylko na **punktach funkcjonalnych**, które mają znaczenie dla codziennego życia.

Przykładowe punkty:

* `bed` – łóżko
* `wc` – toaleta
* `kitchen` – kuchnia
* `desk` – biurko / miejsce pracy
* `entrance` – wejście

Użytkownik:

* **nie ustawia rozmiarów mebli**
* **nie ustawia orientacji**
* **nie rysuje drzwi** (na MVP)

Punkt = punkt startowy / docelowy dla analizy tras.

---

## 2. Scenariusze dnia (NOWA OŚ ANALIZY)

System posiada **predefiniowane scenariusze**, które składają się z sekwencji punktów.

Przykład:

```text
PORANEK:
- bed → wc
- wc → kitchen
- kitchen → living_area

DZIEŃ PRACY:
- bed → kitchen
- kitchen → desk
- desk → wc
```

Użytkownik:

* wybiera, które scenariusze go dotyczą
* **nie edytuje tras ręcznie**

---

## 3. Wyznaczanie tras (PRECYZYJNE, ALE NIEWIDOCZNE)

### 3.1 Rasteryzacja

* layout jest rasteryowany do siatki (np. 10×10 cm)
* ściany = komórki zablokowane
* pozostałe komórki = dostępne

### 3.2 Algorytm

* BFS lub A* (najkrótsza ścieżka)
* koszt = dystans (cm) lub czas (sekundy)

Użytkownik **nigdy nie widzi siatki ani algorytmu**.

---

## 4. Wynik analizy (ZAMIANA „METRYK” NA WERDYKT)

System zwraca:

* ⏱️ czas trwania scenariusza (np. poranek: 6 min)
* 🔁 liczbę powtórzeń kluczowych przejść
* ⚠️ wykryte ryzyka ergonomiczne (opisowe)

Na końcu:

> **WERDYKT:**
>
> * ✔️ Układ wygodny
> * ⚠️ Układ ryzykowny
> * ❌ Układ męczący

* 1–2 zdania uzasadnienia.

---

## 5. Model danych – layout_data (ZMIANA)

```json
{
  "scale_cm_per_px": 0.5,
  "walls": [
    {"x1": 0, "y1": 0, "x2": 500, "y2": 0},
    {"x1": 500, "y1": 0, "x2": 500, "y2": 400}
  ],
  "points": [
    {"id": "bed", "x": 120, "y": 80},
    {"id": "wc", "x": 300, "y": 90},
    {"id": "kitchen", "x": 200, "y": 250}
  ]
}
```

❌ brak mebli
❌ brak tras
❌ brak logiki po stronie frontendu

---

## 6. Frontend – zmiana odpowiedzialności

### FloorCanvas.vue

Odpowiedzialność:

* wyświetlenie tła (rzut)
* rysowanie ścian
* ustawianie punktów

Zakaz:

* liczenia tras
* interpretacji scenariuszy

---

## 7. Backend – analysis (NIE opcjonalny)

Moduł `analysis` jest **rdzeniem biznesowym** aplikacji.

Odpowiada za:

* generowanie tras
* analizę scenariuszy
* werdykt decyzyjny

Frontend **tylko wyświetla wynik**.

---

## 8. MVP – ZAKTUALIZOWANE PRIORYTETY

| Task                | Priorytet | Opis             |
| ------------------- | --------- | ---------------- |
| Upload rzutu        | 🔥        | PDF/JPG jako tło |
| Skala               | 🔥        | 2 punkty + cm    |
| Obrys ścian         | 🔥        | Polilinia        |
| Punkty funkcjonalne | 🔥        | bed, wc, kitchen |
| Analiza scenariusza | 🔥        | poranek          |
| Werdykt             | 🔥        | tekstowy         |

---

## 9. Najważniejsza zasada (DO ZAPAMIĘTANIA)

> **Użytkownik deklaruje rzeczywistość. System ją analizuje.**

Jeśli użytkownik musi coś liczyć lub rysować – projekt jest zepsuty.

---

*Aktualizacja koncepcji: model „upload → punkty → analiza”*
