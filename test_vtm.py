# Automatizované testování webu https://vtm.zive.cz

# Co testujeme:
# 1. Název stránky           -> ověření, že se načte správný titulek stránky
# 2. Viditelnost loga VTM    -> kontrola, že se v záhlaví zobrazuje logo
# 3. Funkčnost hlavního menu -> kliknutí na položky jako „POČÍTAČE“, „MOBILY“, „VĚDA“ apod.
# 4. Otevření článku         -> kliknutí na první článek a kontrola, že se stránka správně načte
# 5. Vyhledávání             -> kliknutí na lupu, zadání výrazu, ověření výsledků
# 6. Přihlášení uživatele    -> (zatím připraveno – test bude doplněn později)
# 7. Odhlášení uživatele     -> (zatím připraveno – test bude doplněn později)

# Projektová struktura:
# - složka „projekt“
# - soubor requirements.txt s knihovnami
# - logovací soubor „log.csv“ pro ukládání výsledků testů

# Použité nástroje:
# - Knihovna Playwright pro Python – slouží k automatizaci webového prohlížeče
# - Umožňuje simulaci kliknutí, vyhledávání a čtení prvků na stránce

# Instalace v PyCharm terminálu:
# 1. pip install -r requirements.txt
# 2. playwright install


from playwright.sync_api import sync_playwright  # Načteme synchronní Playwright API
from pathlib import Path                           # Pro práci s cestami k souborům
import csv                                       # Pro práci s CSV soubory
from datetime import datetime                    # Pro získání aktuálního data a času

# Cesta k logovacímu souboru "log.csv"
soubor_logu = Path("log.csv")

# Funkce pro zápis výsledku do logu
def zapis_vysledek(nazev_testu, vysledek_testu):
    casovy_razitko = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    try:
        soubor_existuje = soubor_logu.exists()
        with soubor_logu.open(mode="a", newline="", encoding="utf-8") as soubor:
            pole = ["čas", "test", "výsledek"]
            zapisovac = csv.DictWriter(soubor, fieldnames=pole)
            if not soubor_existuje:
                zapisovac.writeheader()
            zapisovac.writerow({"čas": casovy_razitko, "test": nazev_testu, "výsledek": vysledek_testu})
    except Exception as chyba:
        print(f"Chyba při zápisu do logu: {chyba}")

# Kontrola tlačítka "Souhlasím" – pokud je viditelné, klikneme; pokud není, nic nevypíšeme
def kontrola_souhlasim(page):
    btn = page.locator("button:has-text('Souhlasím')")
    if btn.count() > 0:
        if btn.first.is_visible():
            btn.first.click(timeout=20000)
        else:
            pass

# Test 1 – Ověření titulku stránky
def test_nazev_stranky(page):
    print("Test 1 - Testuji titulek stránky")
    try:
        titulek = page.title()
        if titulek == "VTM.cz – Věda, technika, zajímavosti, budoucnost":
            print("Test 1 – Titulek je správný")
            zapis_vysledek("Ověření názvu stránky", "Úspěšný")
        else:
            print("Test 1 – Titulek je nesprávný")
            zapis_vysledek("Ověření názvu stránky", "Neúspěšný")
    except Exception as chyba:
        print(f"Test 1 – Chyba při načítání titulku: {chyba}")
        zapis_vysledek("Ověření názvu stránky", "Chyba")

# Test 2 – Ověření viditelnosti loga VTM
def test_viditelnost_loga(page):
    print("Test 2 - Testuji viditelnost loga")
    try:
        kontrola_souhlasim(page)
        # Vyhledáme obrázky, jejichž alt atribut obsahuje řetězec "VTM"
        logo_locator = page.locator("img[alt*='VTM']")
        logo_count = logo_locator.count()
        found_visible = False
        for i in range(logo_count):
            try:
                logo = logo_locator.nth(i)
                logo.wait_for(state="visible", timeout=20000)
                if logo.is_visible():
                    found_visible = True
                    break
            except Exception:
                continue
        if found_visible:
            print("Test 2 - Logo je viditelné")
            zapis_vysledek("Ověření loga", "Úspěšný")
        else:
            print("Logo není viditelné, i když jsou nalezeny elementy.")
            zapis_vysledek("Ověření loga", "Neúspěšný")
    except Exception as e:
        print(f"Chyba při ověřování loga: {e}")
        zapis_vysledek("Ověření loga", "Neúspěšný")

# Test 3 – Funkčnost hlavního menu
def test_funkcnost_hlavniho_menu(page):
    print("Test 3 - Testuji funkčnost hlavního menu")
    odkazy = [
        {"text": "Počítače", "url": "https://www.zive.cz/pocitace"},
        {"text": "Mobily", "url": "https://mobilmania.zive.cz/"},
        {"text": "Věda a technika", "url": "https://vtm.zive.cz/"},
        {"text": "Hry", "url": "https://doupe.zive.cz/"},
        {"text": "Filmy a AV", "url": "https://avmania.zive.cz/"}
    ]
    all_success = True
    for odkaz in odkazy:
        try:
            page.goto("https://vtm.zive.cz/", timeout=20000)
            kontrola_souhlasim(page)
            page.wait_for_load_state("networkidle", timeout=20000)
            page.hover("header", timeout=20000)
            link_locator = page.locator(f"a:has-text('{odkaz['text']}')")
            visible_link = None
            count_links = link_locator.count()
            for i in range(count_links):
                candidate = link_locator.nth(i)
                if candidate.is_visible():
                    visible_link = candidate
                    break
            if visible_link is None:
                raise Exception(f"Nenalezen žádný viditelný odkaz pro {odkaz['text']}")
            visible_link.scroll_into_view_if_needed(timeout=20000)
            with page.expect_navigation(timeout=20000):
                visible_link.click(timeout=20000)
            page.wait_for_load_state("load", timeout=20000)
            current_url = page.url
            print(f"Aktuální URL po kliknutí pro '{odkaz['text']}': {current_url}")
            assert current_url == odkaz["url"], f"Špatná URL pro '{odkaz['text']}'"
            zapis_vysledek(f"Test odkazu: {odkaz['text']}", "Úspěšný")
        except Exception as e:
            print(f"Chyba při testování odkazu {odkaz['text']}: {e}")
            zapis_vysledek(f"Test odkazu: {odkaz['text']}", "Neúspěšný")
            all_success = False
    if all_success:
        print("Test 3 - hlavní menu je funkční")

# Test 4 – Otevření článku
def test_otevreni_clanku(page):
    print("Test 4 - Testuji otevření článku")
    home_url = "https://vtm.zive.cz/"
    page.goto(home_url, timeout=20000)
    kontrola_souhlasim(page)
    page.wait_for_load_state("load", timeout=20000)
    # Hledáme první odkaz, který vede k článku. Selektor "article a" se zde používá jako příklad.
    article_link = page.locator("article a").first
    article_link.wait_for(state="visible", timeout=20000)
    with page.expect_navigation(timeout=20000):
        article_link.click(timeout=20000)
    page.wait_for_load_state("load", timeout=20000)
    current_url = page.url
    if current_url == home_url:
        print("Článek se neotevřel správně, URL je stále homepage.")
        zapis_vysledek("Otevření článku", "Neúspěšný")
    else:
        print(f"Test 4 - Otevření článku byl úspěšný, aktuální URL: {current_url}")
        zapis_vysledek("Otevření článku", "Úspěšný")

# Test 5 – Vyhledávání
def test_vyhledavani(page):
    print("Test 5 - Testuji vyhledávání")
    home_url = "https://vtm.zive.cz/"
    page.goto(home_url, timeout=20000)
    kontrola_souhlasim(page)
    page.wait_for_load_state("load", timeout=20000)
    # Seznam selektorů, které se pokusíme použít k nalezení viditelného tlačítka vyhledávání.
    selectors = [
        "button:has-text('Vyhledávání')",
        "button:has-text('Hledat')",
        "button[aria-label='Hledat']",
        "button[aria-label='Vyhledávání']",
        ".search-toggle"
    ]
    search_icon = None
    for sel in selectors:
        loc = page.locator(sel)
        if loc.count() > 0:
            for i in range(loc.count()):
                candidate = loc.nth(i)
                try:
                    candidate.wait_for(state="visible", timeout=5000)
                    if candidate.is_visible():
                        search_icon = candidate
                        break
                except Exception:
                    continue
        if search_icon is not None:
            break
    if search_icon is None:
        print("Test 5 - Nenašel se viditelný prvek vyhledávání")
        zapis_vysledek("Vyhledávání", "Neúspěšný")
        return
    search_icon.click(timeout=20000)
    # Očekáváme, že se zobrazí vyhledávací pole; předpokládáme, že má atribut type="search"
    search_input = page.locator("input[type='search']")
    search_input.wait_for(state="visible", timeout=20000)
    search_input.fill("test", timeout=20000)
    search_input.press("Enter", timeout=20000)
    # Ověříme, že se zobrazily výsledky s třídou "search-result"
    results = page.locator(".search-result")
    results.wait_for(state="visible", timeout=20000)
    count_results = results.count()
    if count_results > 0:
        print("Test 5 - Vyhledávání funguje, počet výsledků:", count_results)
        zapis_vysledek("Vyhledávání", "Úspěšný")
    else:
        print("Test 5 - Vyhledávání nevrátilo žádné výsledky")
        zapis_vysledek("Vyhledávání", "Neúspěšný")

# Spuštění testů s Playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://vtm.zive.cz/", timeout=20000)
    kontrola_souhlasim(page)
    try:
        test_nazev_stranky(page)          # Test 1 – Titulek
        test_viditelnost_loga(page)         # Test 2 – Logo
        test_funkcnost_hlavniho_menu(page)   # Test 3 – Hlavní menu
        test_otevreni_clanku(page)          # Test 4 – Otevření článku
        test_vyhledavani(page)              # Test 5 – Vyhledávání
    finally:
        browser.close()
