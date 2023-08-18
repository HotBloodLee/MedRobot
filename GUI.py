import customtkinter
from tkinterdnd2 import TkinterDnD, DND_ALL
from typing import Any, Optional
import threading

from MedBot import MedBot

class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x300")
        self.title("爬虫运行中...")
        self.info_label = customtkinter.CTkLabel(self, text="爬虫运行中...请勿点击其他按钮", fg_color="transparent", text_color="yellow")
        self.info_label.place(relx=0.05, rely=0.23, relwidth=0.9, relheight=0.05)

        self.handle_info_label = customtkinter.CTkLabel(self, text="处理信息", fg_color="transparent", text_color="yellow")
        self.handle_info_label.place(relx=0.05, rely=0.53, relwidth=0.9, relheight=0.05)

        self.num_info_label = customtkinter.CTkLabel(self, text="", fg_color="transparent", text_color="yellow")
        self.num_info_label.place(relx=0.05, rely=0.73, relwidth=0.9, relheight=0.05)


class CTk(customtkinter.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)
        self.title("爬虫小工具v0.01（仅针对PubMed）")
        self.geometry("600x700")
        self.create_ui()
        self.country = None
        self.toplevel_window = None

    def create_ui(self):
        self.topics_txt_label = customtkinter.CTkLabel(self, text="关键词输入框（预览）", fg_color="transparent")
        self.topics_txt_label.place(relx=0.05, rely=0.00, relwidth=0.43, relheight=0.1)
        self.topics_txt_textbox = customtkinter.CTkTextbox(self, fg_color="#E6E6E6", text_color="black")
        self.topics_txt_textbox.place(relx=0.05, rely=0.1, relwidth=0.43, relheight=0.4)

        self.topics_file_label = customtkinter.CTkLabel(self, text="关键词文本（可拖拽）", fg_color="transparent")
        self.topics_file_label.place(relx=0.52, rely=0.00, relwidth=0.43, relheight=0.1)
        self.topics_file_textbox = customtkinter.CTkLabel(self, text="请将文件拖入此", fg_color="#333333")
        self.topics_file_textbox.drop_target_register(DND_ALL)
        self.topics_file_textbox.dnd_bind('<<Drop>>', lambda event: self.select_source_path(event.data))
        self.topics_file_textbox.place(relx=0.52, rely=0.1, relwidth=0.43, relheight=0.25)

        self.topics_file_button = customtkinter.CTkButton(self, text="选择文件", command=lambda: self.select_source_path())
        self.topics_file_button.place(relx=0.52, rely=0.4, relwidth=0.43, relheight=0.1)



        self.country_select_label = customtkinter.CTkLabel(self, text="地区检索范围: ", fg_color="transparent")
        self.country_select_label.place(relx=0.05, rely=0.6, relwidth=0.23, relheight=0.05)
        self.country_select_options = customtkinter.CTkOptionMenu(self, values=["国内", "全球"],
                                                 command=self.country_optionmenu_callback)
        self.country_select_options.place(relx=0.3, rely=0.6, relwidth=0.43, relheight=0.05)
        self.country_select_options.set("选择一项")

        self.num_label = customtkinter.CTkLabel(self, text="检索数量: ", fg_color="transparent")
        self.num_label.place(relx=0.05, rely=0.67, relwidth=0.23, relheight=0.05)
        self.num_txt_textbox = customtkinter.CTkTextbox(self, fg_color="#E6E6E6", text_color="black")
        self.num_txt_textbox.place(relx=0.3, rely=0.67, relwidth=0.43, relheight=0.05)
        self.num_txt_textbox.insert("0.0", "100")

        self.start_page_label = customtkinter.CTkLabel(self, text="起始页码: ", fg_color="transparent")
        self.start_page_label.place(relx=0.05, rely=0.74, relwidth=0.23, relheight=0.05)
        self.start_page_txt_textbox = customtkinter.CTkTextbox(self, fg_color="#E6E6E6", text_color="black")
        self.start_page_txt_textbox.place(relx=0.3, rely=0.74, relwidth=0.2, relheight=0.05)
        self.start_page_txt_textbox.insert("0.0", "1")

        self.end_page_label = customtkinter.CTkLabel(self, text="结束页码: ", fg_color="transparent")
        self.end_page_label.place(relx=0.5, rely=0.74, relwidth=0.23, relheight=0.05)
        self.end_page_txt_textbox = customtkinter.CTkTextbox(self, fg_color="#E6E6E6", text_color="black")
        self.end_page_txt_textbox.place(relx=0.73, rely=0.74, relwidth=0.2, relheight=0.05)
        self.end_page_txt_textbox.insert("0.0", "10")

        self.output_file_button = customtkinter.CTkButton(self, text="开始", command=lambda: self.start())
        self.output_file_button.place(relx=0.25, rely=0.85, relwidth=0.5, relheight=0.1)

        # todo:实现各个ui的功能
        # todo:实现爬虫的闭环

    def args_safe(self) -> bool:
        if not self.country:
            print("none")
            # todo:加入警告页面
            return False
        elif self.topics_txt_textbox.get("0.0", "end").rstrip("\n") == "":
            print("no")
            return False
        else:
            return True

    def get_topics(self) -> list:
        topics = list()
        topics_txt = self.topics_txt_textbox.get("0.0", "end").rstrip("\n")
        for topic_txt in topics_txt.split("\n"):
            topic = list()
            for topic_words in topic_txt.split(";"):
                topic.append(topic_words)
            topics.append(topic)
        return topics

    def start(self):
        if self.args_safe():
            topics = self.get_topics()
            output_dir = self.select_output_path()
            end_page = self.end_page_txt_textbox.get("0.0", "end").replace("\n", "")
            start_page = self.start_page_txt_textbox.get("0.0", "end").replace("\n", "")
            num = self.num_txt_textbox.get("0.0", "end").replace("\n", "")
            if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
                self.toplevel_window = ToplevelWindow(self)  # create window if its None or destroyed

            medbot = MedBot(output_dir=output_dir, country='China', num=int(num), start_page=int(start_page), end_page=int(end_page), info_label=self.toplevel_window.info_label, handle_label=self.toplevel_window.handle_info_label, num_label=self.toplevel_window.num_info_label)
            robot_thread = threading.Thread(name='t1', target=medbot.search_topics, args=(topics,))
            self.toplevel_window.focus()
            robot_thread.start()


    def select_source_path(self, source_path: Optional[str] = None):
        print(source_path)
        if source_path is None:
            source_path = customtkinter.filedialog.askopenfilename(title='选择一个关键词文本')
            if source_path:
                with open(source_path, 'r') as f:
                    content = f.read()
                self.topics_txt_textbox.insert("0.0", content)
                self.topics_file_textbox.configure(text="添加成功!!!")
        else:
            with open(source_path, 'r') as f:
                content = f.read()
            self.topics_txt_textbox.insert("0.0", content)
            self.topics_file_textbox.configure(text="添加成功!!!")

    def select_output_path(self, output_path: Optional[str] = None):
        if output_path is None:
            output_path = customtkinter.filedialog.asksaveasfilename(title='保存文件', defaultextension='.xlsx', initialfile='author_infos_test.xlsx')
        return output_path

    def country_optionmenu_callback(self, choice):
        if choice == "国内":
            self.country = 'China'
        else:
            self.country = 'All'

app = CTk()
app.mainloop()




