"""
projekt_3.py: třetí projekt 
author: Tadeáš Žežulka
email: grumpysilver@seznam.cz
discord: grumpy6666
"""

#Importy
import requests
from bs4 import BeautifulSoup
import argparse

# Funkce pro sestavení úplné URL z relativní URL
def sestav_url(base_url, relative_url):
    if '/' in base_url:
        return base_url[:base_url.rfind('/')] + "/" + relative_url
    return base_url

# Funkce pro získání názvů stran z dané URL
def ziskej_nazvy_stran(stranky_url):
    response = requests.get(stranky_url)  # Odeslání HTTP GET požadavku
    if response.status_code == 200:  # Kontrola, zda byl požadavek úspěšný
        soup = BeautifulSoup(response.content, 'html.parser')  # Parsování HTML obsahu
        radky = soup.find_all('tr')  # Vyhledání všech řádků tabulky
        seznam_stran = []
        for radek in radky:
            bunky = radek.find_all("td")  # Vyhledání všech buněk v řádku
            if len(bunky) == 5:  # Pokud řádek obsahuje 5 buněk
                nazev_strany = bunky[1].get_text().strip()  # Získání názvu strany z druhé buňky
                if nazev_strany not in seznam_stran:
                    seznam_stran.append(nazev_strany)  # Přidání názvu strany do seznamu
        return seznam_stran
    else:
        print("Nepodařilo se stáhnout data")
        return []

# Funkce pro zpracování hlavních dat z první URL
def zpracuj_data(prvni_url, soubor, strany_url):
    response = requests.get(prvni_url)  # Odeslání HTTP GET požadavku

    if response.status_code == 200:  # Kontrola, zda byl požadavek úspěšný
        soup = BeautifulSoup(response.content, 'html.parser')  # Parsování HTML obsahu
        radky = soup.find_all('tr')  # Vyhledání všech řádků tabulky
        cislo_radku = 0
        with open(soubor, 'w', encoding='cp1250') as f:  # Otevření souboru pro zápis
            # Zápis záhlaví CSV souboru
            f.write("Kod oblasti;Nazev oblasti;Registrovany volici;Obalky;Platné hlasy;")
            seznam_stran = ziskej_nazvy_stran(strany_url)  # Získání seznamu názvů stran
            f.write(";".join(seznam_stran))
            f.write("\n")
            for radek in radky:
                bunky = radek.find_all("td")  # Vyhledání všech buněk v řádku

                if len(bunky) >= 2:  # Pokud řádek obsahuje alespoň 2 buňky
                    cislo_radku += 1
                    prvni_bunka = bunky.pop(0)
                    druha_bunka = bunky.pop(0)
                    odkazy = prvni_bunka.find_all("a")  # Vyhledání všech odkazů v první buňce
                    if odkazy:
                        prvni_odkaz = odkazy.pop(0)
                        relativni_url = prvni_odkaz.get('href')  # Získání relativní URL z odkazu
                        druha_url = sestav_url(prvni_url, relativni_url)  # Sestavení úplné URL

                        radek_data = prvni_bunka.get_text().strip() + ";" + druha_bunka.get_text().strip()
                        seznam_stran = zpracuj_podrobnosti(druha_url, f, radek_data, cislo_radku, seznam_stran)  # Zpracování podrobností
            if cislo_radku == 1 and seznam_stran:
                f.write(";".join(seznam_stran))
                f.write("\n")
    else:
        print("Nepodařilo se stáhnout data")

# Funkce pro zpracování podrobných dat z druhé URL
def zpracuj_podrobnosti(druha_url, soubor, radek_data, cislo_radku, seznam_stran):
    response = requests.get(druha_url)  # Odeslání HTTP GET požadavku

    if response.status_code == 200:  # Kontrola, zda byl požadavek úspěšný
        soup = BeautifulSoup(response.content, 'html.parser')  # Parsování HTML obsahu
        radky = soup.find_all('tr')  # Vyhledání všech řádků tabulky

        radek_info = ""
        seznam_hlasu = []
        for radek in radky:
            bunky = radek.find_all("td")  # Vyhledání všech buněk v řádku

            if len(bunky) == 9:  # Pokud řádek obsahuje 9 buněk
                prvni_bunka = bunky.pop(3)
                druha_bunka = bunky.pop(3)
                platne_hlasy_bunka = bunky.pop(5)
                radek_info = prvni_bunka.get_text().strip() + ";" + druha_bunka.get_text().strip() + ";" + platne_hlasy_bunka.get_text().strip()
            if len(bunky) == 5:  # Pokud řádek obsahuje 5 buněk
                nazev_strany = bunky.pop(1)
                hlasy_strany = bunky.pop(1)
                if cislo_radku == 1:
                    seznam_stran.append(nazev_strany.get_text().strip())  # Přidání názvu strany do seznamu
                seznam_hlasu.append(hlasy_strany.get_text().strip())  # Přidání hlasů strany do seznamu


        # Zápis dat do souboru
        soubor.write(radek_data + ";" + radek_info + ";" + ";".join(seznam_hlasu))
        soubor.write("\n")
        return seznam_stran
    else:
        print("Nepodařilo se stáhnout data")
        return seznam_stran

# Hlavní funkce skriptu
def hlavni(url, soubor, strany_url):
    zpracuj_data(url, soubor, strany_url)

if __name__ == '__main__':
    # Nastavení argumentů příkazového řádku
    parser = argparse.ArgumentParser(description='Skript pro web scraping')
    parser.add_argument('url', type=str, help='URL stránky pro stažení')
    parser.add_argument('soubor', type=str, help='Výstupní soubor')
    parser.add_argument('strany_url', type=str, help='URL pro získání názvů stran')
    args = parser.parse_args()
    hlavni(args.url, args.soubor, args.strany_url)