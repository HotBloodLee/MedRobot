import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
from pathlib import Path
import json

with Path(f"author_infos.json").open() as json_file:
    author_infos = json.load(json_file)

df = pd.DataFrame(author_infos)
df.to_excel(f"author_infos.xlsx")