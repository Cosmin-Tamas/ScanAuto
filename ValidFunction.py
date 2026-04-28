import re # Importam modulul re pentru a putea folosi expresii regulate in validarea numerelor de inmatriculare


# Liste de prefixe pentru diferite tipuri de numere de inmatriculare din Romania
# Le poti sterge de aici, le-am creat ca sa pot testa si sa verific, dar noi le avem si in main-ul nostru.
speciale = ["MAI", "CD", "CO", "FA", "A", "TC", "PROBE"]

capitala = ["B"]

judete = ["AB", "AG", "AR", "BC", "BH", "BN", "BR", "BT", "BV", "BZ",
               "CJ", "CL", "CS", "CT", "CV", "DB", "DJ", "GJ", "GL",
               "GR", "HD", "HR", "IF", "IL", "IS", "MH", "MM", "MS",
               "NT", "OT", "PH", "SB", "SJ", "SM", "SV", "TL", "TM",
               "TR", "VL", "VN", "VS"]



# Functii de validare pentru diferite tipuri de numere de inmatriculare din Romania

def validare_numar_provizoriu_rosu(numar):
    pattern = r"[A-Z]{1,2}0[1-9][0-9]{1,4}$" # Format: 1-2 litere, urmate de '0', apoi o cifra intre 1-9, apoi 1-4 cifre (total 4-6 cifre)
    if re.match(pattern, numar):
        if numar[:2] in judete:
            print("Masina este din judet, inmatriculata in format provizoriu rosu. Numarul este valid")
            return True
        elif numar[:1] in capitala:
            print("Masina este din Bucuresti, inmatriculata in format provizoriu rosu. Numarul este valid")
            return True
    else:
        return False


def validare_numar_bucuresti(numar):
    pattern = r"^B[0-9]{2,3}[A-Z]{3}$" # Format: 'B', urmat de 2-3 cifre, apoi 3 litere
    if re.match(pattern, numar):
        print("Masina este din Bucuresti si inmatriculata in format standard. Numarul este valid")
        return True
    else:
        return False


def validare_numar_administrativ(numar):
    pattern = r"^[A-Z]{1,6}[0-9]{6}$" # Format: 1-6 litere, urmate de 6 cifre
    if re.match(pattern, numar):
        for prefix in speciale:
            if numar.startswith(prefix):
                 print("Masina este inmatriculata in format special. Numarul este valid")
                 return True
        return False
    else:
        return False


# Functie principala care verifica daca un numar de inmatriculare este valid conform regulilor pentru numerele speciale din Romania

def validare_numar_special(numar):
    if validare_numar_provizoriu_rosu(numar):
        #add to database "TM051245"
        print("Numarul este valid si a fost adaugat in baza de date\n")
        return True
    elif validare_numar_bucuresti(numar):
        #add to database "B129ABD"
        print("Numarul este valid si a fost adaugat in baza de date\n")
        return True
    elif validare_numar_administrativ(numar):
        #add to database "CD123456"
        print("Numarul este valid si a fost adaugat in baza de date\n")
        return True
    else:
        print("Numarul este invalid si nu a fost adaugat in baza de date\n")
        return False






















# Teste automate pentru validari de numere din Romania
# --------------------------------------------------------------
# Aceste teste acopera atat numerele provizorii rosii, cat si cele speciale, precum si cazuri invalide pentru ambele categorii.
#---------------------------------------------------------------
# Fiecare test are un numar de inmatriculare si rezultatul asteptat (True pentru valid, False pentru invalid).
# Testele acopera limitele minime si maxime, formate corecte si incorecte, precum si cazuri speciale pentru a asigura o acoperire cat mai completa a scenariilor posibile.
#---------------------------------------------------------------


cazuri_test = {
    
    # --- CAZURI VALIDE NR PROVIZORII (Asteptam True) ---
    "CJ0634": True,     # Judet format din 2 litere, 4 cifre
    "TM087654": True,   # Judet format din 2 litere, 6 cifre
    "IS0234": True,     # Judet format din 2 litere, 4 cifre
    "B023": True,       # Bucuresti, limita minima de cifre (3)
    "B023456": True,    # Bucuresti, limita maxima de cifre (6)
    "BR012": True,      # Judet format din 2 litere, 3 cifre
    
    # --- CAZURI INVALIDE NR PROVIZORII (Asteptam False) ---
    "B12": False,       # Prea putine cifre (sub 3)
    "CJ1234567": False, # Prea multe cifre (peste 6)
    "XX1234": False,    # Cod de judet inexistent in lista
    "1234CJ": False,    # Format inversat (cifre urmate de litere)
    "B123AB": False,   # Contine litere la final (format standard, nu rosu)
    "TM": False,        # Fara cifre
    "": False,          # String gol
    " CJ1234 ": False,  # Contine spatii (daca zici ca le-ai sters inainte, testul asta confirma ca functia respinge ce nu a fost curatat)

    # --- CAZURI VALIDE NR SPECIALE (Asteptam True) ---
    # Trebuie sa aiba 1-6 litere, EXACT 6 cifre si sa inceapa cu un prefix din lista
    "MAI123456": True,
    "CD000000": True,
    "PROBE987654": True,
    "A111222": True,

    # --- CAZURI INVALIDE NR PROVIZORII (Asteptam False) ---
    "GUV123456": False,   # Litere valide, 6 cifre, nu e "special"
    "SENAT123456": False, # Litere valide (5), 6 cifre
    "X999888": False,     # O singura litera (valid conform {1,6}), 6 cifre
    "MAI12345": False,    # REALITATE: Valid in RO, dar functia ta da False (are doar 5 cifre)
    "CD123": False,       # REALITATE: Valid in RO, dar functia ta da False (are doar 3 cifre)
    "MAI1234567": False,  # Prea multe cifre (7)
    "SPECIAL123456": False, # Prea multe litere (7 litere, regex permite maxim 6)
    "mai123456": False,   # Litere mici (regex-ul tau accepta doar [A-Z] mari)
    "MAI 123456": False,  # Contine spatiu (regex-ul nu permite spatii)
    "123456MAI": False,   # Format inversat
    "CD12345A": False     # Contine litera la final (regex-ul cere exact 6 cifre la final)
}

# Rulam testele automat
teste_trecute = 0
teste_picate = 0

print("--- INCEPERE TESTARE ---")
for numar_test, rezultat_asteptat in cazuri_test.items():
    rezultat_obtinut = validare_numar_special(numar_test) # Apeleaza functia principala care verifica toate tipurile de numere
    
    if rezultat_obtinut == rezultat_asteptat: # Daca rezultatul obtinut corespunde cu cel asteptat, testul a trecut
        teste_trecute += 1
    else:
        print(f"Eroare la testul: {numar_test}. Asteptam {rezultat_asteptat}, dar am primit {rezultat_obtinut}.")
        teste_picate += 1

print("\n--- REZULTATE FINALE ---")
print(f"Teste trecute cu succes: {teste_trecute} din {len(cazuri_test)}")
if teste_picate > 0:
    print(f"Teste esuate: {teste_picate}")



print(validare_numar_special("B513AB")) 
