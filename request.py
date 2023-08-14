import requests
from bs4 import BeautifulSoup


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

response = requests.get('https://pubmed.ncbi.nlm.nih.gov/?term=Artificial+intelligence+identifies+stomach+cancer', headers=headers)
soup = BeautifulSoup(response.text, 'lxml')
docs = soup.find_all("article", class_="full-docsum")
for doc in docs:
    name = doc.find("a", class_="docsum-title")["data-article-id"]
    print(f'https://pubmed.ncbi.nlm.nih.gov/{name}')


# response = requests.get('https://pubmed.ncbi.nlm.nih.gov/34155567/', headers=headers)
#
# soup = BeautifulSoup(response.text, 'lxml')
#
# print(f"作者相关信息:")
# infos = soup.find_all(id="full-view-expanded-authors")[0].find_all("li")
# for info in infos:
#     key = info.find_all("sup")[0].text
#     val = str(info.text[1:]).strip()
#     print(key)
#     print(val)
#
# print("\n")
#
# print(f"论文关键词: ")
# key_words = soup.find_all(id="abstract")[0].find_all("p")[1]
# key_words = key_words.text.split(":")[1].split(";")
# for key_word in key_words:
#     print(key_word.strip().rstrip("."))
#
# print("\n")