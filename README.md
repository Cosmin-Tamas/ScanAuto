# Smart Parking License Plate Validator

Acest proiect reprezintă un modul Python pentru validarea și prelucrarea numerelor de înmatriculare citite automat, fiind gândit ca parte dintr-un sistem inteligent de parcare. Sistemul este destinat să proceseze numere de înmatriculare obținute prin OCR/cameră, să corecteze erori frecvente de scanare și să verifice dacă numerele validate există într-o bază de date locală.

## Funcționalități principale

- Citirea numerelor de înmatriculare dintr-un fișier text.
- Curățarea automată a textului citit: eliminarea spațiilor și transformarea în litere mari.
- Corectarea erorilor OCR frecvente, precum:
  - `8` confundat cu `B`
  - `0` confundat cu `O`
  - `1` confundat cu `I`
  - `7` confundat cu `T`
  - `5` confundat cu `S`
- Validarea numerelor clasice de înmatriculare din România:
  - format județean, de tip `TM08RGM`, `CJ12ABC`;
  - format București, de tip `B123XYZ`;
  - numere provizorii roșii;
  - numere speciale/administrative, precum `MAI`, `CD`, `CO`, `FA`, `TC`, `PROBE`.
- Tratarea cazurilor în care OCR-ul detectează caractere suplimentare la începutul sau finalul numărului.
- Generarea de subșiruri posibile din textul scanat și testarea fiecărei variante.
- Salvarea numerelor validate într-un fișier separat.
- Verificarea numerelor validate într-o bază de date simulată.

## Scopul proiectului

Modulul face parte dintr-un proiect mai amplu de tip **Smart Parking System**, în care un sistem cu Raspberry Pi, cameră și Arduino poate permite accesul automat într-o parcare pe baza recunoașterii numărului de înmatriculare.

Fluxul dorit este:

1. Camera detectează mașina și citește numărul de înmatriculare.
2. OCR-ul extrage textul din imagine.
3. Modulul Python curăță și corectează textul detectat.
4. Numărul este validat conform formatelor acceptate în România.
5. Numărul validat este verificat într-o bază de date.
6. Dacă numărul există în baza de date, sistemul poate permite deschiderea barierei.

## Fișiere folosite

- `inmatriculari.txt` — fișierul de intrare, care conține numerele citite sau scanate, câte unul pe linie.
- `numere_validate.txt` — fișierul de ieșire, în care sunt salvate numerele care au trecut validarea.
- baza de date simulată este momentan reprezentată printr-o listă Python:
  ```python
  numere_inmatriculare = ["TM08RGM", "CJ12ABC", "B123XYZ", "AB99ZZZ", "GJ01AAA"]
