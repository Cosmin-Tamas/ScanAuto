import re # Importam modulul re pentru a putea folosi expresii regulate in validarea numerelor de inmatriculare


#normal s-ar face un blacklist cu numere interzise, dar deoarece legea nu i-a obligat pe soferi sa schimbe placutele dupa interdictie,
# atunci am decis ca pot sa existe inca in circulatie, deci nu le vom considera invalide
# numere precum 'ION' sau 'GUV' sau altele samd 

speciale = ["MAI", "CD", "CO", "FA", "A", "TC", "PROBE"]

capitala = ["B"]

judete = ["AB", "AG", "AR", "BC", "BH", "BN", "BR", "BT", "BV", "BZ",
               "CJ", "CL", "CS", "CT", "CV", "DB", "DJ", "GJ", "GL",
               "GR", "HD", "HR", "IF", "IL", "IS", "MH", "MM", "MS",
               "NT", "OT", "PH", "SB", "SJ", "SM", "SV", "TL", "TM",
               "TR", "VL", "VN", "VS"]

# Functii de validare pentru diferite tipuri de numere de inmatriculare din Romania

def validare_numar_judet_standard(numar):
    # Format: 2 litere, 2 cifre, 3 litere (fara spatii)
    pattern = r"^[A-Z]{1,2}[0-9]{2}[A-Z]{3}$" 
    
    if re.match(pattern, numar):
        # Verificam daca primele 2 litere chiar sunt un judet real din lista ta
        if numar[:2] in judete: 
            return True
        elif numar[:1] in capitala: # verificam daca prima litera corespunde Bucurestiului
            return True
    return False


def validare_numar_provizoriu_rosu(numar):
    pattern = r"[A-Z]{1,2}0[1-9][0-9]{1,4}$" # Format: 1-2 litere, urmate de '0', apoi o cifra intre 1-9, apoi 1-4 cifre 
    if re.match(pattern, numar):
        if numar[:2] in judete: # verificam daca primele 2 litere corespund unui judet valid
            return True
        elif numar[:1] in capitala: # verificam daca prima litera corespunde Bucurestiului
            return True
    else: 
        return False


def validare_numar_bucuresti(numar):
    pattern = r"^B[0-9]{2,3}[A-Z]{3}$" # Format: 'B', urmat de 2-3 cifre, apoi 3 litere
    if re.match(pattern, numar):
        return True
    else:
        return False



def validare_numar_administrativ(numar):
    pattern = r"^[A-Z]{1,6}0[1-9][0-9]{1,4}$" 
    if re.match(pattern, numar):
        for prefix in speciale:
            if numar.startswith(prefix):
                 return True
        return False
    else:
        return False


# Functie principala care verifica daca un numar de inmatriculare este valid conform regulilor pentru numerele speciale din Romania
def validare_numar_special(numar):
    if validare_numar_provizoriu_rosu(numar):
        #add to database "TM051245"
        return True
    elif validare_numar_bucuresti(numar):
        #add to database "B129ABD"
        return True
    elif validare_numar_administrativ(numar):
        #add to database "CD123456"
        return True
    elif validare_numar_judet_standard(numar):
        #add to database "CJ12ABC"
        return True
    else:
        return False


