import pandas as pd
import numpy as np

prioritni_kategorie = ["Plné velikosti", "Náš výběr", "Náš výběr z internetu", "Obsah zdarma","Pro děti", "Biblické filmy", "Originální produkce", "Seriály", "Rodinné filmy"]
max_pocet_radku = {"Plné velikosti": 3, "Náš výběr": 5, "Náš výběr z internetu": 10}

def get_volna_mista(tabulka, kategorie, max_pocet_radku):
        volna_mista = {}
        for i, kat in enumerate(kategorie):
            max_radku = max_pocet_radku.get(kat, 10)  # pokud není v max_pocet_radku, nastav na 10
            volna_mista[kat] = sum(1 for r in range(max_radku) if tabulka[r][i] is None)
        return volna_mista

def get_carousel_data():
    df = pd.read_excel("databaze_filmu.xlsx", header=0)
    kategorie = df.columns[2:].tolist()  # Kategorie ze sloupců B–U
    tabulka = [[None for column in range(len(kategorie))] for row in range(10)]
    buffer = []
    rebuffer = []
    film_to_col = {}  # slovník pro uložení filmu a jeho kategorií

    for index, row in df.iterrows():
        nazev_filmu = row.iloc[1]
       
        if pd.isna(nazev_filmu) or str(nazev_filmu).strip() == "": 
            break #  Pokud je sloupec A prázdný, ukonči načítání

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
                        film_to_col.setdefault(nazev_filmu, []).append(col_index)
                        break
                else:
                    continue # pokud je sloupec zaplněný, zkus další kategorii
                break   # pokud byl film zařazen přeruš for
        else:
            buffer.append((nazev_filmu, kategorie_aktualniho_filmu))  # pokud nebyl film zařazen do prioritní kategorie, přidej ho do bufferu

    np.random.shuffle(buffer)  # zamíchání bufferu, aby se filmy opakovaly náhodně
    # Druhé kolo: z bufferu
    buffer.sort(key=lambda x: len(x[1]), reverse=True)

    for index in range(len(buffer) - 1, -1, -1):
        film, kat_filmu = buffer[index]
        np.random.shuffle(kat_filmu)  # náhodné pořadí kategorií pro spravedlivé rozmístění
        
        for kat in kat_filmu:
            col_index = kategorie.index(kat)
            max_radku = max_pocet_radku.get(kat, 10)

            for radek in range(max_radku):
                if tabulka[radek][col_index] is None:
                    if "Dokumenty" not in kat_filmu:
                        tabulka[radek][col_index] = film
                        film_to_col.setdefault(film, []).append(col_index)
                        # Pokud zůstaly další kategorie, přidej do rebufferu
                        dalsi_kategorie = [k for k in kat_filmu if k != kat]
                        if dalsi_kategorie:
                            rebuffer.append((film, dalsi_kategorie))
                    else:
                        # Pokud je dokument, přidej celý film do rebufferu
                        rebuffer.append((film, kat_filmu))
                    break  # film vložen, přestaň hledat další řádky
            del buffer[index]
            break  # film vložen, nepokračuj další kategorií

# Třetí kolo: doplň z rebufferu (filmy se mohou opakovat)
    np.random.shuffle(rebuffer)  # zamíchání rebufferu, aby se filmy opakovaly náhodně
    
    while rebuffer and any(v > 0 for v in get_volna_mista(tabulka, kategorie, max_pocet_radku).values()):
        film, kategorie_filmu = rebuffer.pop()
        np.random.shuffle(kategorie_filmu)
            
        for kat in kategorie_filmu:
            col_index = kategorie.index(kat)
            max_radku = max_pocet_radku.get(kat, 10)
            puvodni_sloupce = film_to_col.get(film, [])
                
            for radek in range(max_radku):
                if tabulka[radek][col_index] is None:
                    if any(abs(col_index - c) < 3 for c in puvodni_sloupce):
                        continue  # film je už příliš blízko, pokračuj další kategorií
                    tabulka[radek][col_index] = film
                    film_to_col.setdefault(film, []).append(col_index)
                    break

    return tabulka