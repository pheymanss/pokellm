from os import path, mkdir
import requests
from bs4 import BeautifulSoup
import json

class Smogon:
    """
    A class used to interface with the Smogon Pokemon competitive battling platform
    for a specific generation.

    ...

    Attributes
    ----------
    gen : int
        an integer representing the Pokemon generation
    gen_codename : str
        a string representing the codename of the Pokemon generation (eg rb, gs, sv)
    base_url : str
        a string representing the base URL for the Smogon dex
    mechanics : dict
        a dictionary containing the game mechanics for the specified generation
    pokedex : list
        a list of dictionaries containing the Pokemon in the specified generation

    Methods
    -------
    get_game_mechanics():
        Returns a dictionary containing the game mechanics for the specified generation.
        Includes the fields: pokemon, abilities, items, moves, formats, natures, types
    get_pokemon_info(pokemon):
        Returns a dictionary containing the information for the specified Pokemon
    """


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

        # check and create 'gen_#' directory if it does not exist
        if not path.exists(f'gen_{self.gen}'):
            mkdir(f'gen_{self.gen}')

        # fetch game mechanics and save into separate json files
        self.mechanics = self.get_game_mechanics()
        self.pokedex = self.mechanics['pokemon']

        # check if subdirectory 'mechanics' exists inside the gen_# directory
        if not path.exists(f'gen_{self.gen}/mechanics'):
            mkdir(f'gen_{self.gen}/mechanics')


        for m in self.mechanics:
            with open(f'gen_{self.gen}/mechanics/{m}.json', 'w') as f:
                json.dump(self.mechanics[m], f)


    def get_game_mechanics(self):
        """
        Fetches the game mechanics from Smogon for the specified generation
        Includes the fields: pokemon, abilities, items, moves, formats, natures, types

        Returns
        -------
        mechanics : dict
            a dictionary containing the game mechanics for the specified generation
        """
        
        url = f'{self.base_url}pokemon/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        
        if scripts is None:
            raise Exception(f'Could not find game mechanics on {url}')

        for script in scripts:
            if 'dexSettings' in script.text:
                mechanics = json.loads(script.text[14:])['injectRpcs'][1][1]

        return mechanics


    def get_pokemon_info(self, pokemon):
        """
        Fetches the information for the specified Pokemon from the Smogon dex
        from the specified pokemon strategy page. Includes learnset, stats, evolutions,
        metagame overview, all the existing sets and their corresponding strategies.

        Parameters
        ----------
        pokemon : str
            a string representing the name of the Pokemon

        Returns
        -------
        pokemon_info : dict
            a dictionary containing the information for the specified Pokemon
        """
        # validate pokemon
        if pokemon not in [poke['name'] for poke in self.mechanics['pokemon']]:
            raise ValueError(f'{pokemon} not found on generation {self.gen} pokedex')

        # get info from smogon page
        url = f'{self.base_url}pokemon/{pokemon}/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        
        if scripts is None:
            raise Exception(f'Could not find info on {url}')

        for script in scripts:
            if 'dexSettings' in script.text:
                pokemon_info = json.loads(script.text[14:])['injectRpcs'][2][1]

        return pokemon_info




















    def generate_type_chart(self):
        """Creates cypher text corresponding to the relationship between types.
        Values can be: IS_SUPER_EFFECTIVE, IS_NEUTRAL, IS_NOT_VERY_EFFECTIVE, HAS_NO_EFFECT
        """

        pass




