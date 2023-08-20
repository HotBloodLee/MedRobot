import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import time

class MedBot:
    def __init__(self, output_dir, country, num, start_page=1, end_page=None, info_label=None, num_label=None, handle_label=None):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        self.start_url = 'https://pubmed.ncbi.nlm.nih.gov/'
        self.country = country
        self.articles = list()
        self.num = num
        self.start_page = start_page
        self.end_page = end_page
        self.total_api = 0
        self.output_dir = output_dir
        self.info_label = info_label
        self.handle_label = handle_label
        self.num_label = num_label

    def get_total_pages(self, topic) -> int:
        topic_url = ''
        for topic_word in topic:
            topic_url += ('+AND+' if topic_url != '' else '') + f'%28{"+".join(topic_word.split())}%29'
        if self.country != 'all':
            search_url = f'%28%28{topic_url}%29%29+AND+%28{self.country}%5BAffiliation%5D%29'
        response = requests.get(
            f'{self.start_url}?term={search_url}&sort=&page={1}', headers=self.headers)
        print(f'{self.start_url}?term={search_url}&sort=&page={1}')
        soup = BeautifulSoup(response.text, 'lxml')
        pages = soup.find_all("label", class_="of-total-pages")[0]
        return int(pages.text.split()[1].replace(",", ""))

    def handle_json(self):
        for author_info in tqdm(self.author_infos):
            author_info["full_institution"] = author_info["institution"]
            try:
                author_info["institution"] = " , ".join(author_info["institution"].split(",")[0:2])
            except:
                print(author_info)
                raise
            if "Electronic address:" in author_info["email"]:
                author_info["email"] = author_info["email"].split(":")[1].strip()
        df = pd.DataFrame(self.author_infos)
        df.to_excel(f"{self.output_dir}")

    def search_topics(self, topics):
        self.author_infos = list()
        for topic in topics:
            total_page = self.get_total_pages(topic)
            self.articles = list()
            self.search_topic(topic, total_page)
            self.search_articles(topic)
            time.sleep(10)
        self.handle_json()
        if self.info_label:
            self.info_label.configure(text=f"已检索导出完毕，可关闭当前页面")
        if self.handle_label:
            self.handle_label.configure(text=f"")


    def search_topic(self, topic, total_page):
        if (not self.end_page) or (self.end_page > total_page):
            self.end_page = total_page
        topic_url = ''
        for topic_word in topic:
            topic_url += ('+AND+' if topic_url != '' else '') + f'%28{"+".join(topic_word.split())}%29'
        if self.country != 'all':
            search_url = f'%28%28{topic_url}%29%29+AND+%28{self.country}%5BAffiliation%5D%29'
        pages_len = self.end_page - self.start_page + 1
        for i in tqdm(range(pages_len)):
            if self.handle_label:
                self.handle_label.configure(text=f"正在检索{topic}相关的页面 第{i}页/共{pages_len}页")
            response = requests.get(
                f'{self.start_url}?term={search_url}&sort=&page={i + self.start_page}', headers=self.headers)
            soup = BeautifulSoup(response.text, 'lxml')
            docs = soup.find_all("article", class_="full-docsum")
            for doc in docs:
                name = doc.find("a", class_="docsum-title")["data-article-id"]
                self.articles.append(f'{self.start_url}{name}')
            self.total_api += 1
            if self.total_api > 500:
                time.sleep(10)
                self.total_api = 0

    def search_articles(self, topic):
        done = False
        len_articles = len(self.articles)
        for idx, article in tqdm(enumerate(self.articles)):
            if self.handle_label:
                self.handle_label.configure(text=f"正在检索{topic}相关的论文 第{idx}个/共{len_articles}个")
            if done:
                break
            try:
                if self.total_api > 500:
                    time.sleep(10)
                    self.total_api = 0
                response = requests.get(article, headers=self.headers)

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
                    school = ",".join(val.split(",")[:-1])
                    email = val.split(",")[-1].split(".", 1)[-1]

                    if email != "" and "@" in email:
                        author_info = {
                            "name": id2author[key][0],
                            "institution": school,
                            "email": email.strip().rstrip("."),
                            "interests": ";".join([key_word.strip().rstrip(".") for key_word in key_words]),
                            "full_info": val
                        }
                        print(author_info)
                        self.author_infos.append(author_info)
                        print("\n")
                        if len(self.author_infos) > self.num:
                            done = True
                        if self.num_label:
                            self.num_label.configure(text=f"已检索到{len(self.author_infos)}个专家信息")
            except:
                print(article)