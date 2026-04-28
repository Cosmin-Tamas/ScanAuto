import re

# testare numere de inmatriculare auto "normale" din romania
judete = ["AB", "AG", "AR", "BC", "BH", "BN", "BR", "BT", "BV", "BZ", "CJ", 
          "CL", "CS", "CT", "CV", "DB", "DJ", "GJ", "GL", "GR", "HD", "HR", "IF", 
          "IL", "IS", "MH", "MM", "MS", "NT", "OT", "PH", "SB",
            "SJ", "SM", "SV", "TL", "TM", "TR", "VL", "VN", "VS"]

# baza de numere de inmatriculare pentru test

numere_inmatriculare = ["TM08RGM", "CJ12ABC", "B123XYZ", "AB99ZZZ", "GJ01AAA"]

# greseli comune de citire a inmatricularii

dict = {'T':'7', 'B':'8', 'A':'4', 'I':'1', 'S':'5', 'Z':'2', 'O':'0', 'G':'6', 'L':'3',
        '7':'T', '8':'B', '4':'A', '1':'I', '5':'S', '2':'Z', '0':'O', '6':'G', '3':'L'}

# functie de inlocuire a caracterelor gresite intalnite frecvent

def inlocuire_caractere(inmatriculare, pos, alpha):
    if inmatriculare[pos].isalpha() != alpha:
            inmatriculare = inmatriculare[0:pos] + dict.get(inmatriculare[pos], inmatriculare[pos]) + inmatriculare[pos+1:]
    return inmatriculare

def validare_numar_provizoriu_rosu(numar):
    reg = r""
    judet = numar[:2]
    judet = inlocuire_caractere(judet, 0, True)
    judet = inlocuire_caractere(judet, 1, True)
    if judet in judete:
        if not numar[2] == '0' or numar[3] == '0':
            print("Numarul trebuie sa inceapa cu 0 si a doua cifra sa fie diferita de 0")
            return False
        numar_fara_spatiu = numar[2:]
        # verificare_numere_interior = numar[3:-2]

        if len(numar_fara_spatiu) > 6 or len(numar_fara_spatiu) < 3: 
            print("Numarul trebuie sa aiba intre 3 si 6 cifre")
            return False
        for i in numar_fara_spatiu:
            if not i.isdigit():
                print("Numarul trebuie sa contina doar cifre dupa judet")
                return False
    else:
        print("Judetul nu este valid")
        return False
    return True

def validare_numar_clasic_negru(inmatriculare):
    reg = r"^[A-Z]{2}[0-9]{2}[A-Z]{3}$"
    inmatriculare = inlocuire_caractere(inmatriculare, 0, True)
    inmatriculare = inlocuire_caractere(inmatriculare, 1, True)
    inmatriculare = inlocuire_caractere(inmatriculare, 2, False)
    inmatriculare = inlocuire_caractere(inmatriculare, 3, False)
    inmatriculare = inlocuire_caractere(inmatriculare, 4, True)
    inmatriculare = inlocuire_caractere(inmatriculare, 5, True)
    inmatriculare = inlocuire_caractere(inmatriculare, 6, True)
    print(f"Inmatriculare dupa inlocuire: {inmatriculare}")
    if re.match(reg, inmatriculare):
        if inmatriculare in numere_inmatriculare:
            print("Acces Aprobat!")
        else:
            print("Numarul de inmatriculare nu este in baza de date")
    else:
        print("Numarul de inmatriculare nu este valid")


def main():

    # citire numere de inmatriculare de intrare

    f = open("inmatriculare.txt", "r")

    # prelucrare in forma standard

    for line in f:
        inmatriculare = line.strip().upper().replace(" ", "")
        print(f"Verificare pentru: {inmatriculare}")
        
        # aducerea inmatricularii la forma standard
        
        validare_numar_clasic_negru(inmatriculare)
        

            
if __name__ == "__main__":    main()
