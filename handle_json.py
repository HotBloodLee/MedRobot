import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
from pathlib import Path
import json

with Path(f"author_infos.json").open() as json_file:
    author_infos = json.load(json_file)

for author_info in tqdm(author_infos):
    author_info["full_institution"] = author_info["institution"]
    try:
        author_info["institution"] = " , ".join(author_info["institution"].split(",")[0:2])
    except:
        print(author_info)
        raise
    if "Electronic address:" in author_info["email"]:
        author_info["email"] = author_info["email"].split(":")[1].strip()

df = pd.DataFrame(author_infos)
df.to_json(f"author_infos.json", orient="records")