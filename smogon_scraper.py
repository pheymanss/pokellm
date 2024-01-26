from os import path, mkdir
import requests
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup

class SmogonScraper:
    def __init__(self, gen: int):	

        # assert valid gen
        gen = int(gen)
        assert gen in range(1, 10), 'Generation must be between 1 and 9.'

        # map gen to codename
        gen_codenames = {
            1: 'rb',
            2: 'gs',
            3: 'rs',
            4: 'dp',
            5: 'bw',
            6: 'xy',
            7: 'sm',
            8: 'ss',
            9: 'sv'
        }

        self.gen = gen
        self.gen_codename = gen_codenames[gen]
        self.base_url = f'https://www.smogon.com/dex/{self.gen_codename}/'


    def collect_pokemon_urls(self):

        # Set up headless browser options
        options = FirefoxOptions()
        options.add_argument("--headless")

        # Initialize a browser driver
        driver = webdriver.Firefox(options=options)  # or webdriver.Chrome(options=options), depending on your browser

        # Get the webpage
        driver.get(self.base_url + 'pokemon/')

        pokemon_hrefs = set()
        scroll_position = 0

        while True:
            # Scroll down a small amount
            scroll_position += 500
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")

            # Wait to load page
            time.sleep(2)

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find all hrefs that point to a Pokemon and add them to the set
            for a_tag in soup.find_all('a'):
                href = a_tag.get('href')
                if f'/dex/{self.gen_codename}/pokemon/' in href:
                    pokemon_hrefs.add(href)

            # If we've reached the end of the page, break the loop
            if scroll_position >= driver.execute_script("return document.body.scrollHeight"):
                break

        # Close the browser
        driver.quit()

        # create directory for generation
        if not path.exists(f'gen_{self.gen}'):
            mkdir(f'gen_{self.gen}')

        # write the hrefs to a file
        with open(f'gen_{self.gen}/gen_{self.gen}_urls.txt', 'w') as f:
            for href in pokemon_hrefs:
                f.write( 'https://www.smogon.com/' + href + '\n')
        
        print(f'Collected {len(pokemon_hrefs)} hrefs for gen {self.gen} Pokemon.')


    def scrape_pokemon_data(self, pokemon):
        # Set up headless browser options
        options = FirefoxOptions()
        options.add_argument("--headless")

        # Initialize a browser driver
        driver = webdriver.Firefox(options=options)  # or webdriver.Chrome(options=options), depending on your browser

        # Get the webpage
        url = self.base_url + pokemon
        driver.get(url)

        scroll_position = 0
        data = {}

        while True:
            # Scroll down a small amount
            scroll_position += 500
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")

            # Wait to load page
            time.sleep(2)

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Scrape the Pokemon's name
            name_div = soup.find('div', class_='PokemonAltRow')
            if name_div:
                data['name'] = name_div.text.strip()

            # Scrape the Pokemon's typing
            type_icon_div = soup.find('div', class_='TypeIcon')
            if type_icon_div:
                data['typing'] = [img['alt'] for img in type_icon_div.find_all('img')]

            # Scrape the Pokemon's stats
            stat_divs = soup.find_all('div', class_='Stat')
            if stat_divs:
                data['stats'] = {stat.find('b').text: stat.find('span').text for stat in stat_divs}

            # Scrape the Pokemon's evolutions
            dex_nav_button_div = soup.find('div', class_='DexNavButton')
            if dex_nav_button_div:
                data['evolutions'] = [evolution.text for evolution in dex_nav_button_div.find_all('a')]

            # Scrape the Pokemon's strategy overview
            strategy_overview_div = soup.find('div', class_='StrategyOverview')
            if strategy_overview_div:
                data['strategy_overview'] = strategy_overview_div.text.strip()

            # Scrape the Pokemon's specific strategies
            strategy_divs = soup.find_all('div', class_='Strategy')
            if strategy_divs:
                data['specific_strategies'] = [strategy.text for strategy in strategy_divs]

            # Scrape the Pokemon's formats
            formats_div = soup.find('div', class_='Formats')
            if formats_div:
                data['formats'] = [format.text for format in formats_div.find_all('a')]

            # Scrape the Pokemon's moves
            move_divs = soup.find_all('div', class_='Move')
            if move_divs:
                data['moves'] = [{'name': move.find('a').text, 'type': move.find('img')['alt'], 'class': move.find('span').text} for move in move_divs]

            # If we've reached the end of the page, break the loop
            if scroll_position >= driver.execute_script("return document.body.scrollHeight"):
                break

        # Close the browser
        driver.quit()

        return data