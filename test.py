

if __name__ == "__main__":
    get_carousel_data()
    
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
            puvodni_sloupce = film_to_col.get(film, [])
            max_radku = max_pocet_radku.get(kat, 10)
            if any(abs(col - c) < 3 for c in puvodni_sloupce):
                continue  # film je už příliš blízko, pokračuj další kategorií
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