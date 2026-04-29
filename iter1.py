import re


# ============================================================
# DATE GENERALE
# ============================================================

# Judete valide din Romania
judete = [
    "AB", "AG", "AR", "BC", "BH", "BN", "BR", "BT", "BV", "BZ",
    "CJ", "CL", "CS", "CT", "CV", "DB", "DJ", "GJ", "GL", "GR",
    "HD", "HR", "IF", "IL", "IS", "MH", "MM", "MS", "NT", "OT",
    "PH", "SB", "SJ", "SM", "SV", "TL", "TM", "TR", "VL", "VN", "VS"
]

# Bucuresti
capitala = ["B"]

# Prefixe speciale / administrative
speciale = ["MAI", "CD", "CO", "FA", "A", "TC", "PROBE"]

# Baza de date simulata pentru testarea accesului
numere_inmatriculare = ["TM08RGM", "CJ12ABC", "B123XYZ", "AB99ZZZ", "GJ01AAA", "TM29TCR"]

# Greseli comune de OCR / scanare
corectii_caractere = {
    'T': '7', 'B': '8', 'A': '4', 'I': '1', 'S': '5', 'Z': '2', 'O': '0', 'G': '6', 'L': '3',
    '7': 'T', '8': 'B', '4': 'A', '1': 'I', '5': 'S', '2': 'Z', '0': 'O', '6': 'G', '3': 'L'
}


# ============================================================
# FUNCTII DE CORECTARE SI PREGATIRE TEXT
# ============================================================

def curata_numar(numar):
    """
    Aduce textul citit din fisier / OCR intr-o forma standard:
    - elimina spatiile;
    - elimina newline;
    - transforma in litere mari.
    """
    return numar.strip().upper().replace(" ", "")


def inlocuire_caractere(inmatriculare, pos, alpha):
    """
    Corecteaza un caracter de pe o pozitie data, daca tipul sau nu corespunde.

    alpha = True  -> pe pozitia respectiva asteptam litera
    alpha = False -> pe pozitia respectiva asteptam cifra

    Exemplu:
    - daca asteptam litera si avem '8', incercam sa il corectam in 'B'
    - daca asteptam cifra si avem 'O', incercam sa il corectam in '0'
    """
    if pos < 0 or pos >= len(inmatriculare):
        return inmatriculare

    if inmatriculare[pos].isalpha() != alpha:
        inmatriculare = (
            inmatriculare[:pos] +
            corectii_caractere.get(inmatriculare[pos], inmatriculare[pos]) +
            inmatriculare[pos + 1:]
        )

    return inmatriculare


def corecteaza_dupa_format(numar, format_asteptat):
    """
    Corecteaza un numar dupa un format de tip:
    - L = litera
    - D = cifra

    Exemplu:
    format_asteptat = "LLDDLLL" pentru TM08RGM
    format_asteptat = "LDDDLLL" pentru B123XYZ
    format_asteptat = "LLDDDD" pentru TM0876
    """
    if len(numar) != len(format_asteptat):
        return numar

    numar_corectat = numar

    for i, tip in enumerate(format_asteptat):
        if tip == "L":
            numar_corectat = inlocuire_caractere(numar_corectat, i, True)
        elif tip == "D":
            numar_corectat = inlocuire_caractere(numar_corectat, i, False)

    return numar_corectat


def genereaza_subsiruri(numar, lungime_minima=4, lungime_maxima=12):
    """
    Genereaza variante posibile dintr-un string scanat.

    Daca OCR-ul citeste ceva de forma:
        XTM08RGM9

    atunci se vor testa si bucati precum:
        TM08RGM

    Am pastrat lungimea maxima 12 deoarece numerele administrative pot avea
    prefix de pana la 6 litere si pana la 6 cifre.
    """
    candidati = set()

    if not numar:
        return candidati

    candidati.add(numar)

    for lungime in range(lungime_minima, lungime_maxima + 1):
        if len(numar) >= lungime:
            for i in range(len(numar) - lungime + 1):
                candidati.add(numar[i:i + lungime])

    return candidati


# ============================================================
# VALIDARI SIMPLE, FARA CORECTIE OCR
# ============================================================

def validare_numar_judet_standard(numar):
    """
    Verifica formatul clasic de judet:
    - TM08RGM
    - CJ12ABC
    - AB99ZZZ

    Format: 2 litere judet + 2 cifre + 3 litere.
    """
    pattern = r"^[A-Z]{2}[0-9]{2}[A-Z]{3}$"

    if re.match(pattern, numar):
        return numar[:2] in judete

    return False


def validare_numar_bucuresti(numar):
    """
    Verifica formatul clasic de Bucuresti:
    - B12ABC
    - B123XYZ

    Format: B + 2 sau 3 cifre + 3 litere.
    """
    pattern = r"^B[0-9]{2,3}[A-Z]{3}$"
    return re.match(pattern, numar) is not None


def validare_numar_provizoriu_rosu(numar):
    """
    Verifica numere provizorii rosii:
    - TM087654
    - CJ0634
    - B023456

    Format general:
    - judet/capitala + 0 + cifra diferita de 0 + inca 1-4 cifre
    """
    pattern = r"^[A-Z]{1,2}0[1-9][0-9]{1,4}$"

    if not re.match(pattern, numar):
        return False

    if numar[:2] in judete:
        return True

    if numar[:1] in capitala:
        return True

    return False


def validare_numar_administrativ(numar):
    """
    Verifica numere administrative / speciale:
    - MAI012345
    - CD0123
    - PROBE098765

    Format:
    - prefix special din lista
    - 0
    - cifra diferita de 0
    - inca 1-4 cifre

    """
    pattern = r"^[A-Z]{1,6}0[1-9][0-9]{1,4}$"

    if not re.match(pattern, numar):
        return False

    for prefix in speciale:
        if numar.startswith(prefix):
            return True

    return False


def validare_numar_special(numar):
    """
    Functia principala pentru validarea tuturor tipurilor acceptate:
    - numar clasic judet;
    - numar Bucuresti;
    - numar provizoriu rosu;
    - numar administrativ/special.
    """
    if validare_numar_judet_standard(numar):
        return True

    if validare_numar_bucuresti(numar):
        return True

    if validare_numar_provizoriu_rosu(numar):
        return True

    if validare_numar_administrativ(numar):
        return True

    return False


# ============================================================
# VALIDARI CU CORECTIE OCR
# ============================================================

def testeaza_candidat_clasic_negru(numar):
    """
    Testeaza un candidat de tip numar clasic de judet, cu corectii OCR.

    Format asteptat:
        LLDDLLL

    Exemplu:
        TM08RGM
        CJ12ABC
    """
    if len(numar) != 7:
        return None

    numar_corectat = corecteaza_dupa_format(numar, "LLDDLLL")

    if validare_numar_judet_standard(numar_corectat):
        return numar_corectat

    return None


def testeaza_candidat_bucuresti(numar):
    """
    Testeaza un candidat de tip Bucuresti, cu corectii OCR.

    Formate acceptate:
        B12ABC   -> LDDLLL
        B123ABC  -> LDDDLLL
    """
    if len(numar) == 6:
        numar_corectat = corecteaza_dupa_format(numar, "LDDLLL")
    elif len(numar) == 7:
        numar_corectat = corecteaza_dupa_format(numar, "LDDDLLL")
    else:
        return None

    if validare_numar_bucuresti(numar_corectat):
        return numar_corectat

    return None


def testeaza_candidat_provizoriu_rosu(numar):
    """
    Testeaza un candidat de tip numar provizoriu rosu, cu corectii OCR.

    Formate posibile:
        B023
        B023456
        TM012
        TM087654

    Prefixul poate avea 1 litera pentru Bucuresti sau 2 litere pentru judet.
    Dupa prefix urmeaza doar cifre.
    """
    variante_corectate = set()

    for lungime_prefix in [1, 2]:
        lungime_cifre = len(numar) - lungime_prefix

        if 3 <= lungime_cifre <= 6:
            format_asteptat = "L" * lungime_prefix + "D" * lungime_cifre
            variante_corectate.add(corecteaza_dupa_format(numar, format_asteptat))

    for varianta in variante_corectate:
        if validare_numar_provizoriu_rosu(varianta):
            return varianta

    return None


def testeaza_candidat_administrativ(numar):
    """
    Testeaza un candidat de tip numar administrativ/special, cu corectii OCR.

    Prefixul poate avea 1-6 litere.
    Zona numerica poate avea 3-6 cifre.
    """
    variante_corectate = set()

    for lungime_prefix in range(1, 7):
        lungime_cifre = len(numar) - lungime_prefix

        if 3 <= lungime_cifre <= 6:
            format_asteptat = "L" * lungime_prefix + "D" * lungime_cifre
            variante_corectate.add(corecteaza_dupa_format(numar, format_asteptat))

    for varianta in variante_corectate:
        if validare_numar_administrativ(varianta):
            return varianta

    return None


def valideaza_cu_corectie(numar):
    """
    Trece numarul prin toate probele de validare.

    Ordinea este:
    1. clasic judet;
    2. Bucuresti;
    3. provizoriu rosu;
    4. administrativ/special.

    Returneaza numarul corectat daca este valid.
    Returneaza None daca nu s-a gasit nicio varianta valida.
    """
    validari = [
        testeaza_candidat_clasic_negru,
        testeaza_candidat_bucuresti,
        testeaza_candidat_provizoriu_rosu,
        testeaza_candidat_administrativ
    ]

    for functie_validare in validari:
        rezultat = functie_validare(numar)

        if rezultat is not None:
            return rezultat

    return None


def gaseste_numar_valid_din_scanare(numar_scanat):
    """
    Primeste un text posibil murdar / scanat gresit.

    Exemple:
        XTM08RGM9
        8CJ12ABC
        XXMAI012345ZZ

    Genereaza candidati si incearca sa gaseasca primul numar valid.
    """
    candidati = genereaza_subsiruri(numar_scanat)

    for candidat in candidati:
        rezultat = valideaza_cu_corectie(candidat)

        if rezultat is not None:
            return rezultat

    return None


# ============================================================
# FISIERE SI BAZA DE DATE SIMULATA
# ============================================================

def proceseaza_fisier_intrare(nume_fisier_intrare, nume_fisier_validari):
    """
    Citeste numerele din fisierul de intrare.
    Pentru fiecare linie:
    - curata textul;
    - cauta un numar valid;
    - scrie numarul valid in fisierul de validari;
    - evita duplicatele.
    """
    numere_validate = set()

    with open(nume_fisier_validari, "w") as fisier_out:
        pass

    print("\n--- INCEPERE PROCESARE FISIER ---\n")

    try:
        with open(nume_fisier_intrare, "r") as fisier_in:
            with open(nume_fisier_validari, "a") as fisier_out:

                for line in fisier_in:
                    numar_scanat = curata_numar(line)

                    if not numar_scanat:
                        continue

                    print(f"Verificare pentru: {numar_scanat}")

                    numar_valid = gaseste_numar_valid_din_scanare(numar_scanat)

                    if numar_valid is None:
                        print("Rezultat: numar invalid\n")
                        continue

                    if numar_valid in numere_validate:
                        print(f"Rezultat: {numar_valid} este valid, dar exista deja in fisier\n")
                        continue

                    fisier_out.write(numar_valid + "\n")
                    numere_validate.add(numar_valid)

                    print(f"Rezultat: {numar_valid} este valid si a fost adaugat in {nume_fisier_validari}\n")

    except FileNotFoundError:
        print(f"Eroare: fisierul '{nume_fisier_intrare}' nu exista.")
        print("Creeaza fisierul si adauga numerele scanate, cate unul pe linie.")


def verifica_acces_din_fisier(nume_fisier_validari):
    """
    Citeste numerele validate din fisier si verifica daca exista
    in baza de date simulata numere_inmatriculare.
    """
    print("\n--- VERIFICARE ACCES IN BAZA DE DATE ---\n")

    try:
        with open(nume_fisier_validari, "r") as fisier:
            for line in fisier:
                numar = curata_numar(line)

                if not numar:
                    continue

                if numar in numere_inmatriculare:
                    print(f"{numar}: Acces Aprobat!")
                else:
                    print(f"{numar}: numar valid, dar nu exista in baza de date.")

    except FileNotFoundError:
        print(f"Eroare: fisierul '{nume_fisier_validari}' nu exista.")


# ============================================================
# MAIN
# ============================================================

def main():
    nume_fisier_intrare = "inmatriculari.txt"
    nume_fisier_validari = "numere_validate.txt"

    proceseaza_fisier_intrare(nume_fisier_intrare, nume_fisier_validari)
    verifica_acces_din_fisier(nume_fisier_validari)


if __name__ == "__main__":
    main()