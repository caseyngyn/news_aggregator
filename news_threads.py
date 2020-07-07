"""
Casey Nguyen
app that's a personalized news aggregator. 
The app lets the user choose their news sources,  
get the latest headlines from their news sources, 
and read the news article online. 

using THREADS
"""
from newsapi import NewsApiClient
import tkinter as tk  
import tkinter.messagebox as tkmb
import sys
import threading
import queue
import webbrowser

class MainWindow(tk.Tk):
    def __init__(self,*filenames):
        super().__init__()
        self.newsapi = NewsApiClient(api_key = '1957381a9a8949958ed1e7e331e3bab1')
        self.news_source = self.get_news_source('name')
        self.news_id = self.get_news_source('id')
        option_frame = tk.Frame(self)

        self.cursor = ()
        self.title('Latest Headlines')
        S = tk.Scrollbar(option_frame,orient = "vertical")
        self.Lb = tk.Listbox(option_frame,height = 20,width = 40, selectmode = "multiple",yscrollcommand = S.set)
        S.pack(side = "right",fill = "y")
        self.Lb.pack()
        S.config(command = self.Lb.yview)

        self.Lb.insert(tk.END,*self.news_source)
        self.Lb.bind("<<ListboxSelect>>",self.poll)

        option_frame.pack()

        tk.Button(self,text = "OK", command = self.button_click).pack() #need to change the OK button to link to display button so need to make a display button thing

        self.protocol("WM_DELETE_WINDOW",self.delete)

    def button_click(self):
        """Ok button logic"""
        if len(self.cursor) == 0:
            tkmb.showinfo("Note","Choose one or more news source")
        else:
            user_selected = [self.news_id[i] for i in self.cursor]
            dwin = DisplayWin(self,user_selected,self.newsapi)
            self.wait_window(dwin)
            self.Lb.selection_clear(0,tk.END)

    def get_news_source(self,req):
        sources = self.newsapi.get_sources(language= 'en',country='us')
        source_list = [d[req] for d in sources['sources']]
        return source_list

    def poll(self,*args):
        """get cursor selection"""
        self.cursor = self.Lb.curselection()

    def delete(self):
        """exits the window"""
        self.cursor = ()
        self.selected = None
        self.destroy()



class DisplayWin(tk.Toplevel):
    def __init__(self,master,news_id,news_api):
        super().__init__(master)
        #self.focus_set()     # comment this out to see the effect
        #self.grab_set()      # comment this out to see the effect
        self.transient(master)    # comment this out to see the effect (on Windows system)
        self.news_api = news_api
        self.news_id = news_id
        self.q = queue.Queue()
        threads = []
        self.url_list = []

        str1 = tk.StringVar()
        str1.set("Click on the headline to read the article")
        tk.Label(self,textvariable = str1).pack()

        option_frame = tk.Frame(self)
        #e = threading.Event()
        self.title('Headlines')
        S = tk.Scrollbar(option_frame,orient = "vertical")
        self.Lb = tk.Listbox(option_frame,height = 20,width = 150, selectmode = "single",yscrollcommand = S.set)
        S.pack(side = "right",fill = "y")     
        S.config(command = self.Lb.yview)
        self.Lb.pack()
        self.Lb.bind("<Double-1>",self.open_link)
        option_frame.pack()

        for v in self.news_id:
            """getting all the threads"""
            t =threading.Thread(target= lambda que,arg1,arg2: que.put(self.get_headlines(arg1,arg2)),name = "thread"+str(v), args = (self.q,v,self.url_list))
            #t =threading.Thread(target= self.get_headlines, args = (v,e))
            threads.append(t)
  
        for t in threads:
            t.start()

        for t in threads:
            t.join()
        

        while not self.q.empty():
            temp = self.q.get()
            self.Lb.insert(tk.END,*temp)
        
        #self.protocol("WM_DELETE_WINDOW",self.delete)

    def get_headlines(self,id,url):
        headline = self.news_api.get_everything(sources = id,language='en')
        temp_list = []
        for v in headline['articles']:
            temp_list.append(v['source']['name']+" : "+v['title'])
            url.append(v['url'])
        return temp_list
 
    def open_link(self,event):
        selected = self.Lb.curselection()
        #print(selected)
        webbrowser.open(self.url_list[selected[0]])
'''
    def delete(self):
        """exits the window"""
        self.Lb.selection_clear(0,tk.END)
        self.destroy()
'''
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()