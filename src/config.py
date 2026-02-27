import os
from dotenv import load_dotenv
from pokemontcgsdk import RestClient

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv('POKEMONTCG_API_KEY')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'pokemon_tcg.db')

# Configure PokémonTCG API client
if API_KEY:
    RestClient.configure(API_KEY)
else:
    print("Warning: No API key configured. Rate limits will be restrictive.")

# Database URI
DATABASE_URI = f'sqlite:///{DATABASE_PATH}'