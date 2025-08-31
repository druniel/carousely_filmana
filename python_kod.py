import pandas as pd
import random

prioritni_kategorie = ["Plné velikosti", "Náš výběr", "Obsah zdarma","Pro děti", "Náš výběr z internetu", "Originální produkce", "Seriály", "Rodinné filmy"]
max_pocet_radku = {"Plné velikosti": 3, "Náš výběr": 5, "Náš výběr z internetu": 10,}

def get_carousel_data():
    df = pd.read_excel("databaze_filmu.xlsx", header=0)
    kategorie = df.columns[2:].tolist()  # Kategorie ze sloupců B–U
    tabulka = [[None for column in range(len(kategorie))] for row in range(10)]
    buffer = []
    rebuffer = []
    test = []
    film_to_col = {}  # slovník pro uložení filmu a jeho kategorií
    while_counter = 0  # pro cyklus while, aby se necyklil do nekonečna

    for index, row in df.iterrows():
        nazev_filmu = row.iloc[1]
       
        if pd.isna(nazev_filmu) or str(nazev_filmu).strip() == "": 
            break # 🛑 Pokud je sloupec A prázdný, ukonči načítání

        bool_hodnoty = row.iloc[2:].astype(str).str.lower().tolist()  # převede hodnoty na seznam a na lowercase
        
        # vezme index sloupců kde je true a převádí na názvy kategorií pomocí seznamu kategorií v proměnné kategorie
        kategorie_aktualniho_filmu = [kat for kat, val in zip(kategorie, bool_hodnoty) if val == "true"]
        
        if not kategorie_aktualniho_filmu:
            continue

        # Pokud film patří do některé z prioritních kategorií a není zaplněných všech 10 pozic, šoupne ho tam a potom ukončí cyklus, pokud ne, tak ho dá do bufferu
        for kat in prioritni_kategorie:
            col_index = kategorie.index(kat)
            if kat in kategorie_aktualniho_filmu and nazev_filmu not in film_to_col:
                for radek in range(10):
                    if tabulka[radek][col_index] is None:
                        tabulka[radek][col_index] = nazev_filmu
                        film_to_col[nazev_filmu] = col_index
                        break
                else:
                    continue # pokud je sloupec zaplněný, zkus další kategorii
                break   # pokud byl film zařazen přeruš for
        else:
            buffer.append((nazev_filmu, kategorie_aktualniho_filmu))  # pokud nebyl film zařazen do prioritní kategorie, přidej ho do bufferu

    random.shuffle(buffer)  # zamíchání bufferu, aby se filmy opakovaly náhodně

     # Druhé kolo jedna kategorie: naplň z bufferu – každý film jen jednou - prochází postupně všechny řádky a sloupce a prázdné naplňuje, náhodně vybere do které kategorie, a následně film přidá do nového bufferu
    for index in range(len(buffer) - 1, -1, -1):  # Prochází buffer odzadu kvůli bezpečnému mazání
        film, kat_filmu = buffer[index]
        if len(kat_filmu) == 1:
            kat = kat_filmu[0]
            col_index = kategorie.index(kat)
            max_radku = max_pocet_radku.get(kat, 10)
            obsazeno = sum(1 for r in range(10) if tabulka[r][col_index] is not None)
            if obsazeno >= max_radku:
                del buffer[index]
                continue
            for radek in range(10):
                if tabulka[radek][col_index] is None:
                    tabulka[radek][col_index] = film
                    film_to_col[film] = col_index
                    del buffer[index]
                    break
        
        # Druhé kolo více kategorií: naplň z bufferu – každý film jen jednou - prochází postupně všechny řádky a sloupce a prázdné naplňuje, náhodně vybere do které kategorie, a následně film přidá do nového bufferu
    for index in range(len(buffer) - 1, -1, -1):
        film, kat_filmu = buffer[index]

        random.shuffle(kat_filmu)  # Zamíchá pořadí kategorií pro tento film

        for kat in kat_filmu:
            col_index = kategorie.index(kat)
            max_radku = max_pocet_radku.get(kat, 10)  # pokud není v max_pocet_radku, nastav na 10
            obsazeno = sum(1 for r in range(10) if tabulka[r][col_index] is not None)
            if obsazeno >= max_radku:
                continue  # Kategorie je plná podle limitu, zkus jinou

            for radek in range(10):
                if tabulka[radek][col_index] is None and "Dokumenty" not in kat_filmu:  # pokud je prázdné místo a není to dokument
                    tabulka[radek][col_index] = film
                    film_to_col[film] = col_index
                    new_buffer = [k for k in kat_filmu if k != kat]
                    if new_buffer:  # pokud zůstaly kategorie, přidej do rebufferu
                        rebuffer.append((film, new_buffer))
                    del buffer[index]  # Odstraní film z bufferu
                    break  # Film úspěšně vložen, končíme
                if "Dokumenty" in kat_filmu:
                    rebuffer.append((film, kat_filmu))  # pokud je to dokument, přidej do rebufferu
                    del buffer[index]  # Odstraní film z bufferu
                    break  # Film úspěšně vložen, končíme
            else:
                continue  # Kategorie plná, zkus další
            break  # Nepokračuj na další kategorie, pokud film byl vložen

    random.shuffle(rebuffer)  # zamíchání rebufferu, aby se filmy opakovaly náhodně

# Třetí kolo: doplň z rebufferu (filmy se mohou opakovat), prvně funkce na propočítání volných míst
    def get_volna_mista(tabulka, kategorie, max_pocet_radku):
        volna_mista = {}
        for i, kat in enumerate(kategorie):
            max_radku = max_pocet_radku.get(kat, 10)  # pokud není v max_pocet_radku, nastav na 10
            volna_mista[kat] = sum(1 for r in range(max_radku) if tabulka[r][i] is None)
        return volna_mista

    volna_mista = get_volna_mista(tabulka, kategorie, max_pocet_radku) # počítá volná místa v tabulce, vrací slovník s počtem volných míst pro každou kategorii

    while rebuffer and any(v > 0 for v in volna_mista.values()):
        film, kategorie_filmu = rebuffer.pop()
        for kat in kategorie_filmu:
            col = kategorie.index(kat)
            puvodni_sloupec = film_to_col.get(film)
            max_radku = max_pocet_radku.get(kat, 10)
            if puvodni_sloupec is not None and abs(col - puvodni_sloupec) < 3:  # je už film někde v tabulce? a je blíž než 2 sloupce? pokud jo, tak jdem dál
                continue
            if any(tabulka[r][col] == film for r in range(max_radku)):  # je už film v daném sloupci? pokud jo, tak jdem dál
                continue
            for radek in range(max_radku):
                if tabulka[radek][col] is None:
                    tabulka[radek][col] = film
                    volna_mista[kat] -= 1
                    break   # přidáno, další film
            else:
                continue    # pokud je sloupec zaplněný, zkus další kategorii
            break  # pokud byl film už zařazen, přeruš cyklus

    return tabulka