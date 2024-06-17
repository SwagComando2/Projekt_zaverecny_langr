"""
projekt_3.py: třetí projekt 
author: Adam Langr
E-mail: adamlangr19@seznam.cz
"""

import requests
from bs4 import BeautifulSoup
import argparse

# Funkce pro vytvoření úplné URL z relativní cesty
def vytvorit_url(hlavni_url, relativni_cesta):
    if '/' in hlavni_url:
        return hlavni_url[:hlavni_url.rfind('/')] + "/" + relativni_cesta
    return hlavni_url

# Funkce pro extrahování názvů stran z dané stránky
def ziskat_nazvy_stran(url_stran):
    odpoved = requests.get(url_stran)
    if odpoved.status_code == 200:
        soup = BeautifulSoup(odpoved.content, 'html.parser')
        radky = soup.find_all('tr')
        seznam_stran = []
        for radek in radky:
            bunky = radek.find_all("td")
            if len(bunky) == 5:
                nazev = bunky[1].get_text().strip()
                if nazev not in seznam_stran:
                    seznam_stran.append(nazev)
        return seznam_stran
    else:
        print("Chyba při stahování dat")
        return []

# Funkce pro zpracování hlavních dat z hlavní stránky
def ziskat_data(url, soubor, url_stran):
    odpoved = requests.get(url)
    if odpoved.status_code == 200:
        soup = BeautifulSoup(odpoved.content, 'html.parser')
        radky = soup.find_all('tr')
        radky_cislo = 0
        seznam_stran = ziskat_nazvy_stran(url_stran)
        with open(soubor, 'w', encoding='cp1250') as f:
            f.write("Kod oblasti;Nazev oblasti;Registrovani volici;Obalky;Platne hlasy;")
            f.write(";".join(seznam_stran))
            f.write("\n")
            for radek in radky:
                bunky = radek.find_all("td")
                if len(bunky) >= 2:
                    radky_cislo += 1
                    prvni_bunka = bunky.pop(0)
                    druha_bunka = bunky.pop(0)
                    odkazy = prvni_bunka.find_all("a")
                    if odkazy:
                        prvni_odkaz = odkazy[0]
                        relativni_cesta = prvni_odkaz.get('href')
                        detailni_url = vytvorit_url(url, relativni_cesta)
                        radek_data = prvni_bunka.get_text().strip() + ";" + druha_bunka.get_text().strip()
                        seznam_stran = ziskat_detailni_data(detailni_url, f, radek_data, radky_cislo, seznam_stran)
            if radky_cislo == 1 and seznam_stran:
                f.write(";".join(seznam_stran))
                f.write("\n")
    else:
        print("Chyba při stahování dat")

# Funkce pro zpracování detailních dat z detailní stránky
def ziskat_detailni_data(url, soubor, radek_data, radky_cislo, seznam_stran):
    odpoved = requests.get(url)
    if odpoved.status_code == 200:
        soup = BeautifulSoup(odpoved.content, 'html.parser')
        radky = soup.find_all('tr')
        radek_info = ""
        seznam_hlasu = []
        for radek in radky:
            bunky = radek.find_all("td")
            if len(bunky) == 9:
                prvni_bunka = bunky[3]
                druha_bunka = bunky[4]
                platne_hlasy_bunka = bunky[8]
                radek_info = prvni_bunka.get_text().strip() + ";" + druha_bunka.get_text().strip() + ";" + platne_hlasy_bunka.get_text().strip()
            if len(bunky) == 5:
                nazev_strany = bunky[1]
                hlasy_strany = bunky[2]
                if radky_cislo == 1:
                    seznam_stran.append(nazev_strany.get_text().strip())
                seznam_hlasu.append(hlasy_strany.get_text().strip())
        soubor.write(radek_data + ";" + radek_info + ";" + ";".join(seznam_hlasu))
        soubor.write("\n")
        return seznam_stran
    else:
        print("Chyba při stahování dat")
        return seznam_stran

# Hlavní funkce skriptu
def hlavni(vstupni_url, vystupni_soubor, url_stran):
    ziskat_data(vstupni_url, vystupni_soubor, url_stran)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Skript pro web scraping')
    parser.add_argument('vstupni_url', type=str, help='URL hlavní stránky')
    parser.add_argument('vystupni_soubor', type=str, help='Cesta k výstupnímu souboru')
    parser.add_argument('url_stran', type=str, help='URL pro získání názvů stran')
    args = parser.parse_args()
    hlavni(args.vstupni_url, args.vystupni_soubor, args.url_stran)