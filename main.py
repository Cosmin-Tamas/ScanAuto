from ValidFunction import validare_numar_special



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
    
    "PROBE987654": True,
    "A111222": True,
    "MAI12345": True,   
    "CD123": True, 
    
    
    # --- CAZURI INVALIDE NR PROVIZORII (Asteptam False) ---
    "GUV123456": False,   # Litere valide, 6 cifre, nu e "special"
    "SENAT123456": False, # Litere valide (5), 6 cifre
    "X999888": False,     # O singura litera (valid conform {1,6}), 6 cifre
    "CD000000": False,    # nu se poate doar 0 la cifrele finale, trebuie sa fie intre 000001 si 999999
    "MAI1234567": False,  # Prea multe cifre (7)
    "SPECIAL123456": False, # Prea multe litere (7 litere, regex permite maxim 6)
    "mai123456": False,   # Litere mici (regex-ul tau accepta doar [A-Z] mari)
    "MAI 123456": False,  # Contine spatiu (regex-ul nu permite spatii)
    "123456MAI": False,   # Format inversat
    "CD12345A": False     # Contine litera la final (regex-ul cere exact 6 cifre la final)
}


def testare_automata():
    teste_trecute = 0
    teste_picate = 0

    print("\n--- INCEPERE TESTARE AUTOMATA ---")
    for numar_test, rezultat_asteptat in cazuri_test.items():
        rezultat_obtinut = validare_numar_special(numar_test) 
        
        if rezultat_obtinut == rezultat_asteptat:
            teste_trecute += 1
        else:
            print(f"[EROARE TEST] '{numar_test}' -> Asteptam {rezultat_asteptat}, am primit {rezultat_obtinut}")
            teste_picate += 1

    print("--- REZULTATE FINALE TESTARE ---")
    print(f"Teste trecute cu succes: {teste_trecute} din {len(cazuri_test)}")
    if teste_picate > 0:
        print(f"Teste esuate: {teste_picate}")
    print("--------------------------------\n")


def main():
    nume_fisier_intrare = "inmatriculari.txt"
    nume_fisier_iesire = "baza_de_date.txt"

    # 1. Creeaza / Goleste fisierul de output la fiecare rulare
    with open(nume_fisier_iesire, "w") as f:
        pass # Doar il deschidem in modul "w" ca sa il curete/creeze

    # Un "set" este o structura de date foarte rapida pentru a verifica daca un element exista deja
    numere_procesate = set()

    print("--- INCEPERE PROCESARE FISIER ---")

    try:
        with open(nume_fisier_intrare, "r") as fisier_in:
            
            with open(nume_fisier_iesire, "a") as fisier_out:
                
                for line in fisier_in:
                    numar = line.strip().replace(" ", "") # Curatam spatiile si newline-urile                 
                    if not numar:
                        continue # Sarim peste liniile goale
                        
                    if validare_numar_special(numar):
                        if numar in numere_procesate: # Verificam daca numarul a fost deja adaugat in baza de date
                            print(f"Numarul: {numar} exista deja in baza de date. Nu a fost adaugat din nou.\n---------------------------------")
                        else:
                            # Adaugam in fisier
                            fisier_out.write(numar + "\n")
                            # Adaugam si in set-ul memoriei noastre
                            numere_procesate.add(numar)
                            print(f"Numarul: {numar} a fost adaugat in baza de date.\n")
                    else:
                        print(f"Numarul: {numar} este invalid.\n")
                        
    except FileNotFoundError:
        print(f"Eroare: Fisierul '{nume_fisier_intrare}' nu exista in folder! Te rog sa il creezi.")

if __name__ == "__main__":
    main()