import tkinter as tk
from tkinter import filedialog as fd
import requests as r
import regex as re
import os
import time

def to_time(seconds):
    out = ''

    seconds = int(seconds)

    minutes = seconds // 60
    seconds %= 60
    hours = minutes // 60
    minutes %= 60
    days = hours // 24
    hours %= 24

    if days != 0:
        out += str(days) + 'd '
    if hours != 0:
        out += str(hours) + 'h '
    if minutes != 0:
        out += str(minutes) + 'm '
    if seconds != 0:
        out += str(seconds) + 's '
    out += 'left'
    buffer = ' ' * 30
    return buffer + out + buffer

class Scraper:
    def __init__(self, root=None, folder = ''):
        # Needed variables
        self.folder = folder
        self.starting_link = ''
        self.depth = 0
        self.session_size = 100
        self.timeout = .5
        self.start_time = -1

        # Create window
        if root is not None:
            self.root = tk.Tk()
        else:
            self.root = root
        self.root.title('WikiScraper')

        # First page
        self._page1()

        # Start loop
        self.root.mainloop()

    """
    Page methods
    """

    def _page1(self):
        """
        Intro page
        :return: None
        """

        # Wipe
        for widget in self.root.winfo_children():
            widget.destroy()

        # Description label
        tk.Label(self.root, text='WikiScraper').pack()

        # Help button
        tk.Button(self.root, text='Help', command=self._info_page).pack()

        # Instructional label
        tk.Label(self.root, text='Article scraping depth:').pack()

        # Size textbox
        self.depth_tb = tk.Text(self.root, height=1, width=20)
        self.depth_tb.pack()

        # Instructional label
        tk.Label(self.root, text='Starting link:').pack()

        # Initial link textbox
        self.link_tb = tk.Text(self.root, height=1, width=20)
        self.link_tb.pack()

        if self.folder == '':
            # Get location button
            tk.Button(self.root, text='Select folder', command=self._get_dir).pack()

        # Go button
        tk.Button(self.root, text='Begin', command=self._page2).pack()

        # Dev info label
        tk.Label(self.root, text='2022, jdehmel@outlook.com').pack()

        return

    def _info_page(self):
        # Wipe
        for widget in self.root.winfo_children():
            widget.destroy()

        # Directions
        directions = \
            'What is this?\n' \
            'Wikiscraper starts at an inputted Wikipedia page, and\n' \
            'scrapes it for Wikipedia links. For all pages it comes\n' \
            'across, it saves them locally as .txt files. A navigator\n' \
            'is also included with these files to make them more\n' \
            'usable.\n' \
            'Scraping depth?\n' \
            'This is how deep to scrape Wikipedia. 0 means just get\n' \
            'the inputted article, 1 means get all articles mentioned\n' \
            'in that, and 2 means get all articles mentioned in those.\n' \
            'Etc. forever.\n' \
            'Contact info:\n' \
            'Jorb Dehmel, jdehmel@outlook.com'
        tk.Label(self.root, text=directions).pack()

        # Return button
        tk.Button(self.root, text='Back', command=self._page1).pack()

        return

    def _page2(self):
        """
        Running page
        :return: None
        """

        # Get data
        self.depth = self.depth_tb.get('1.0', tk.END)
        self.starting_link = self.link_tb.get('1.0', tk.END)

        # Wipe
        for widget in self.root.winfo_children():
            widget.destroy()

        # Time left indicator
        self.time_left = tk.Label(self.root, text='')
        self.time_left.pack()

        # Master article indicator
        self.within = tk.Label(self.root, text='')
        self.within.pack()

        # Article indicator
        self.article = tk.Label(self.root, text='')
        self.article.pack()

        # Emergency kill button
        tk.Button(self.root, text='Cancel (saves data)', command=self.root.destroy).pack()

        self.root.update()

        # Run
        self._run()

        return

    def _run(self):
        """
        Data processing and stuff
        :return:
        """

        # Record start time
        self.start_time = time.time()

        # Initialize folder structure
        self.article.configure(text='Building folders')
        self.root.update()

        try:
            os.mkdir(self.folder + '/articles')
        except FileExistsError:
            pass

        # Open root page
        self.num_left = 1
        self._scrape_to_file(self.starting_link, depth=0)

        # Go to end screen
        self._page3()

        return

    def _page3(self):
        """
        Ending page
        :return: None
        """

        # Wipe
        for widget in self.root.winfo_children():
            widget.destroy()

        # Finishing label
        end_time = time.time()
        tk.Label(self.root, text='Successfully finished in\n' + to_time(end_time - self.start_time)).pack()

        # Kill button
        tk.Button(self.root, text='Close', command=self.root.destroy).pack()

        return

    """
    Button methods
    """

    def _get_dir(self):
        self.folder = fd.askdirectory()
        return

    def _scrape_to_file(self, url, depth=0):
        self.num_left -= 1
        self.time_left.configure(text=to_time(self.num_left * self.timeout))

        if ':' in url[10:]:
            return

        # Get html from url
        url = url.strip()
        try:
            html = r.get(url, timeout=self.timeout)
        except r.exceptions.ReadTimeout:
            print('Timeout at ' + url)
            return

        if html.status_code != 200:
            return
        html = html.text

        # Get title
        try:
            title = re.search(r'(?<=mw-first-heading">)[^<]+', html).group()
        except AttributeError:
            try:
                title = url.split('/')[-1]
            except AttributeError:
                i = 0
                while os.path.exists(self.folder + '/articles/MISSINGTITLE_' + str(i) + '.txt'):
                    i += 1
                title = 'MISSINGTITLE_' + str(i)
        self.article.configure(text=title)
        self.root.update()

        if depth != 0:
            with open(self.folder + '/index.txt', 'r') as file:
                if re.search(title, file.read()):
                    return

        text = ''.join(re.findall(r'(?<=<p>).+?(?=</p>)', html, flags=re.DOTALL))
        text = '\t' + text
        text = re.sub(r'<.*?>', r'', text, flags=re.DOTALL)
        text = re.sub(r'&[^ ]+', r'', text)
        text = re.sub(r'\n', r'\n\n\t', text)

        # Write to new file
        with open(self.folder + '/articles/' + title + '.txt', 'w') as file:
            for char in text:
                try:
                    file.write(char)
                except UnicodeEncodeError:
                    file.write('-')

        # Add new file to index file
        with open(self.folder + '/index.txt', 'a') as file:
            file.write('\n' + url + ' ' + title)

        # Descend to next level
        if depth < int(self.depth):
            # Update master article label
            self.within.configure(text=title)

            # Get links
            links = re.findall(r'(?<=href="/wiki/)[^"]*', html)
            links.sort()
            links = list(dict.fromkeys(links))
            self.num_left += len(links) ** (int(self.depth) - depth)
            for link in links:
                with open(self.folder + '/index.txt', 'r') as file:
                    if re.search(link, file.read()):
                        continue
                try:
                    link = re.sub(r'\*', r'\*', link)
                    self._scrape_to_file('https://en.wikipedia.org/wiki/' + link, depth + 1)
                #except AttributeError:
                    #print('HTML parsing failed')
                #except UnicodeEncodeError:
                    #print('Non-unicode title')
                except:
                    pass
                    #print('Unknown error thrown')

            # Update
            print(title, 'finished.')
        return
        #https://en.wikipedia.org/wiki/Artificial_intelligence


if __name__ == '__main__':
    Scraper()
