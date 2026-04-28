# ScanAuto
A Python script for validating and classifying Romanian vehicle license plates (standard, provisional, and special formats) using Regular Expressions.




# Validare Placute Inmatriculari România

Acest proiect oferă un set de funcții în Python concepute pentru a verifica, valida și clasifica diferite formate de numere de înmatriculare auto din România. Este util pentru aplicații care necesită procesarea și curățarea datelor auto.

**Funcționalități principale:**
* **Validare numere provizorii (roșii):** Verifică numerele temporare pentru toate cele 41 de județe și București, respectând limitele corecte de cifre.
* **Validare numere standard:** Verifică formatele standard (momentan implementat formatul de București cu 2/3 cifre și 3 litere).
* **Identificare numere speciale:** Recunoaște formatele administrative și speciale (MAI, CD, TC, FA, PROBE, etc.).
* **Eficiență:** Construit folosind modulele `re` (Regular Expressions) din Python pentru o potrivire rapidă și precisă a tiparelor textuale.
