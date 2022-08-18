import tkinter as tk
from tkinter import filedialog as fd
from tkinter import scrolledtext as st
import regex as re
import scraper
import os

class Reader:
    def __init__(self):
        # Initialize variables
        self.root = tk.Tk()
        self.folder = ''
        self.index_contents = {'FOLDER MISSING': 'FOLDER MISSING'}

        # Start page
        self._page1()

        # Mainloop
        self.root.mainloop()

    def _page1(self):
        """
        Start page
        :return: None
        """

        # Clear
        for widget in self.root.winfo_children():
            widget.destroy()

        # Description label
        tk.Label(self.root, text='Wikipedia Offline Reader').pack()

        # Get folder button
        cwd = os.getcwd()
        cwd = re.sub(r'\\', r'/', cwd)
        if os.path.exists(cwd + '/articles'):
            self.folder = cwd
            print(self.folder)
        else:
            tk.Button(self.root, text='Get folder', command=self._get_folder).pack()

        # Continue button
        tk.Button(self.root, text='Open reader', command=self._page2).pack()

        # Open scraper button
        tk.Button(self.root, text='Open scraper', command=self._open_scraper).pack()

        # Dev label
        tk.Label(self.root, text='2022, jdehmel@outlook.com').pack()

        return

    def _page2(self):
        """
        Search page
        :return: None
        """

        # Load index
        self.index_contents = {}
        with open(self.folder + '/index.txt', 'r') as file:
            lines = file.read().split('\n')
            seperated = [i.split(' ', 1) for i in lines]
            while [''] in seperated:
                seperated.remove([''])
            for article in seperated:
                self.index_contents[article[0]] = article[1]

        # Clear
        for widget in self.root.winfo_children():
            widget.destroy()

        # Label
        tk.Label(self.root, text='Search Local Backup').pack()

        # Search box
        self.search_box = tk.Text(self.root, height=1, width=20)
        self.search_box.pack()

        # Search button
        tk.Button(self.root, text='Search', command=self._search).pack()

        # Result dropdown
        self.results = ''

        # Go to article button
        self.go_button = ''

        return

    def _page3(self, title):
        """
        Read page
        :param title: Title of article to open
        :return: None
        """

        # Get contents of article
        filename = self.folder + '/articles/' + title + '.txt'
        try:
            with open(filename, 'r') as file:
                text = file.read()
            self.current_title = title
        except FileNotFoundError:
            text = 'FILE LOADING FAILED'
            self.current_title = 'ERROR'

        # Clear
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title label
        tk.Label(self.root, text=title).pack()

        # Scrollable text
        text_box = st.ScrolledText(self.root, height=20)
        text_box.insert(tk.INSERT, text)
        text_box.configure(state='disabled')
        text_box.pack()

        # Back button
        tk.Button(self.root, text='Back', command=self._page2).pack()

        # Quit button
        tk.Button(self.root, text='Quit', command=self.root.destroy).pack()

        # Source label
        self._get_source()

        return

    def _get_folder(self):
        # self.folder = os.getcwd()
        self.folder = fd.askdirectory()

        return

    def _open_scraper(self):
        scraper.Scraper(self.root, self.folder)
        self.root.destroy()
        return

    def _search(self):
        options = ['Select result']

        search = self.search_box.get('1.0', tk.END).strip()
        for key in self.index_contents:
            if re.search(search, self.index_contents[key], re.IGNORECASE):
                options.append(self.index_contents[key])

        # Display select box
        self.clicked = tk.StringVar()
        self.clicked.set('Select result')
        results = tk.OptionMenu(self.root, self.clicked, *options)
        results.pack()

        # Go button
        self.go_button = tk.Button(self.root, text='Go to article', command=self._go)
        self.go_button.pack()

        return

    def _go(self):
        self._page3(self.clicked.get())
        return

    def _get_source(self):
        out_text = '(link not found)'
        for key in self.index_contents:
            if self.index_contents[key] == self.current_title:
                out_text = key
        tk.Label(self.root, text='From: '+out_text).pack()
        return


if __name__ == '__main__':
    Reader()
