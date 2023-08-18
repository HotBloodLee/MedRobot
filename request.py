import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
from pathlib import Path
import json
from pypinyin import pinyin, lazy_pinyin
from Pinyin2Hanzi import DefaultDagParams
from Pinyin2Hanzi import dag

'''
国外：https://pubmed.ncbi.nlm.nih.gov/?term=((artificial%20intelligence)%20AND%20(clinical))&page={i+201}
国内：https://pubmed.ncbi.nlm.nih.gov/?term=%28%28%28artificial+intelligence%29+AND+%28clinical%29%29%29+AND+%28China%5BAffiliation%5D%29&sort=&page={i+1}
'''



# def pinyin_2_hanzi(pinyinList):
#     dagParams = DefaultDagParams()
#     # path_num：候选值，可设置一个或多个
#     result = dag(dagParams, pinyinList, path_num=10, log=True)
#     if(len(result) > 0):
#         return True
#     else:
#         return False
#
# for author_info in tqdm(author_infos):
#     is_name = True
#     for n in author_info['name'].lower().split():
#         if not pinyin_2_hanzi(n):
#             is_name = False
#             break
#     if is_name:
#         print(author_info)



headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
articles = list()
start_url = 'https://pubmed.ncbi.nlm.nih.gov/'

for i in tqdm(range(100)):
    response = requests.get(
                f'https://pubmed.ncbi.nlm.nih.gov/?term=%28%28%28artificial+intelligence%29+AND+%28clinical%29%29%29+AND+%28China%5BAffiliation%5D%29&sort=&page={i+1}', headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    docs = soup.find_all("article", class_="full-docsum")
    for doc in docs:
        name = doc.find("a", class_="docsum-title")["data-article-id"]
        articles.append(f'{start_url}{name}')

author_infos = list()
try:
    with Path(f"author_infos.json").open() as json_file:
        author_infos = json.load(json_file)
except:
    print("new file")

for article in tqdm(articles):
    try:
        response = requests.get(article, headers=headers)

        soup = BeautifulSoup(response.text, 'lxml')


        id2author = {}
        authors = soup.find_all(id="full-view-heading")[0].find_all("span", class_="authors-list-item")
        for author in authors:
            name = author.find_all("a", class_="full-name")[0]
            ids = str(author.find_all("sup")[0].text).split("\n")
            for id in ids:
                id = "".join(id.split())
                if not id == "":
                    if id not in id2author.keys():
                        id2author[id] = list()
                    id2author[id].append(name.text)





        key_words = soup.find_all(id="abstract")[0].find_all("p")[1]
        key_words = key_words.text.split(":")[1].split(";")



        infos = soup.find_all(id="full-view-expanded-authors")[0].find_all("li")
        for info in infos:
            key = info.find_all("sup")[0].text
            val = str(info.text[1:]).strip()
            school = val.split(".", 1)[0]
            email = val.split(".", 1)[-1]

            if email != "" and "@" in email:
                author_info = {
                    "name": id2author[key][0],
                    "institution": school,
                    "email": email.strip().rstrip("."),
                    "interests": ";".join([key_word.strip().rstrip(".") for key_word in key_words]),
                    "full_info": val
                }
                print(author_info)
                author_infos.append(author_info)

                print("\n")



    except:
        print(article)
print(len(author_infos))
df = pd.DataFrame(author_infos)
df.to_json(f"author_infos.json", orient="records")


