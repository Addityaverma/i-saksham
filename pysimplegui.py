import re
import regex
import pandas as pd
import numpy as np
import emoji
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from spacy.lang.hi import STOP_WORDS as STOP_WORDS_HI
import IPython
import kaleido
from tkinter import *
from tkinter import Label
from tkinter import Button
from tkinter import Checkbutton
from tkinter import Tk
from tkinter import filedialog
import sys
import os
import tkinter
from tkinter.constants import *
import PySimpleGUI as sg


# In[91]:


def do(filepath,folderpath,list_users):
    
    sg.popup_notify("Wait for Analysis")
    
    path = folderpath
    
    def date_time(s):
        pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9]+), ([0-9]+):([0-9]+)[ ]?(AM|PM|am|pm)? -'
        result = regex.match(pattern, s)
        if result:
            return True
        return False

    def find_author(s):
        s = s.split(":")
        if len(s)==2:
            return True
        else:
            return False

    def getDatapoint(line):
        splitline = line.split(' - ')
        dateTime = splitline[0]
        date, time = dateTime.split(",")
        message = " ".join(splitline[1:])
        if find_author(message):
            splitmessage = message.split(": ")
            author = splitmessage[0]
            message = " ".join(splitmessage[1:])
        else:
            author= None
        return date, time, author, message
    
    data = []
    #conversation = 'WhatsApp Chat with Jeevika-i-Saksham fellows.txt'
    conversation = filepath
    with open(conversation, encoding="utf-8") as fp:
        fp.readline()
        messageBuffer = []
        date, time, author = None, None, None
        while True:
            line = fp.readline()
            if not line:
                break
            line = line.strip()
            if date_time(line):
                if len(messageBuffer) > 0:
                    data.append([date, time, author, ' '.join(messageBuffer)])
                messageBuffer.clear()
                date, time, author, message = getDatapoint(line)
                messageBuffer.append(message)
            else:
                messageBuffer.append(line)
                
                
    df = pd.DataFrame(data, columns=["Date", 'Time', 'Author', 'Message'])
    df['Date'] = pd.to_datetime(df['Date'])
    #print(df.info())
    
    total_messages = df.shape[0]
    print("total messages : ",total_messages)
    
    media_messages = df[df["Message"]=='<Media omitted>'].shape[0]
    print("media_messages: ", media_messages)
    
    def split_count(text):
        emoji_list = []
        data = regex.findall(r'\X',text)
        for word in data:
            if any(char in emoji.UNICODE_EMOJI['en'] for char in word):
                emoji_list.append(word)
        return emoji_list
    df['emoji'] = df["Message"].apply(split_count)
    emojis = sum(df['emoji'].str.len())
    print("emojis: ", emojis)

    URLPATTERN = r'(https?://\S+)'
    df['urlcount'] = df.Message.apply(lambda x: regex.findall(URLPATTERN, x)).str.len()
    links = np.sum(df.urlcount)

    print("Jeevika Group chat")
    print("Total Messages: ", total_messages)
    print("Number of Media Shared: ", media_messages)
    print("Number of Emojis Shared", emojis)
    print("Number of Links Shared", links)
    
    media_messages_df = df[df['Message'] == '<Media omitted>']
    messages_df = df.drop(media_messages_df.index)
    messages_df['Letter_Count'] = messages_df['Message'].apply(lambda s : len(s))
    messages_df['Word_Count'] = messages_df['Message'].apply(lambda s : len(s.split(' ')))
    messages_df["MessageCount"]=1
    
    
    #button_Select_Authors = Button(window,text = "Click here to select Authors", command = checkbox([messages_df['Author'].unique()]))

    #l = ['Munger Fellow Sonam Bharati', 'i-Saksham Dharm Veer', 'Shravan Jha','Jam Bablu Jio', 'Aditya']
    
    if len(list_users) == 0:
        l = list(messages_df['Author'].unique())
    else:
        l = list_users


    messages_df = messages_df.loc[messages_df['Author'].isin(l)]

    Author_data = []
    for i in range(len(l)):
      # Filtering out messages of particular user
        req_df= messages_df[messages_df["Author"] == l[i]]
      # req_df will contain messages of only one particular user
        #print(f'Stats of {l[i]} -')
        Author_data.append(f'Stats of {l[i]} -')
      # shape will print number of rows which indirectly means the number of messages
        #print('Messages Sent', req_df.shape[0])
        Author_data.append('Messages Sent '+ str(req_df.shape[0]))
      #Word_Count contains of total words in one message. Sum of all words/ Total Messages will yield words per message
        words_per_message = (np.sum(req_df['Word_Count']))/req_df.shape[0]
        #print('Average Words per message', words_per_message.round(2))
        Author_data.append('Average Words per message ' + str(words_per_message.round(2)))
      #media conists of media messages
        media = media_messages_df[media_messages_df['Author'] == l[i]].shape[0]
        #print('Media Messages Sent', media)
        Author_data.append('Media Messages Sent '+str(media))
      # emojis conists of total emojis
        emojis = sum(req_df['emoji'].str.len())
        #print('Emojis Sent', str(emojis))
        Author_data.append('Emojis Sent '+str(emojis))
      #links consist of total links
        links = sum(req_df["urlcount"])   
        #print('Links Sent', str(links))
        Author_data.append('Links Sent '+ str(links))

    f=open(path+'\Authors.txt','w')
    Author_data=map(lambda x:x+'\n', Author_data)
    f.writelines(Author_data)
    f.close()
    
    
    total_emojis_list = list(set([a for b in messages_df.emoji for a in b]))
    total_emojis = len(total_emojis_list)

    total_emojis_list = list([a for b in messages_df.emoji for a in b])
    emoji_dict = dict(Counter(total_emojis_list))
    emoji_dict = sorted(emoji_dict.items(), key=lambda x: x[1], reverse=True)
    for i in emoji_dict:
        #print(i)
        emoji_df = pd.DataFrame(emoji_dict, columns=['emoji', 'count'])
    import plotly.express as px
    fig = px.pie(emoji_df.head(10), values='count', names='emoji', title = "Top Ten Emojis")
    fig.update_traces(textposition='inside', textinfo='percent+label')
    #fig.show()

    fig.write_image(path+"\Top ten emojis.png")
    
   # sg.Image(source = path+"\Top ten emojis.png",size = (500,500))
    
    df = pd.read_csv('stp.csv')
    
    stop_word_hindi = []

    for i in df['stp']:
        stop_word_hindi.append(i)
    stop_word_hindi = set(stop_word_hindi)
    stopwords = set(STOP_WORDS_HI).union(stop_word_hindi)

    stopwords = stopwords.union(STOPWORDS)
    
    messages_df['weekday'] = messages_df['Date'].apply(lambda x: x.day_name())
    # new column month_sent
    messages_df['month_sent'] = messages_df['Date'].apply(lambda x: x.month_name()) 
    #messages_df['hour'] = [d.hour for d in messages_df['Time']]
    
    hour = []
    for i in messages_df['Time']:
        if i.split(" ")[2] == "am":
            hour.append(int((i.split(" ")[1]).split(":")[0]))
        else:
            hour.append(int((i.split(" ")[1]).split(":")[0])+ 12)

    messages_df['hour'] = [i for i in hour]
    
    date_grouped = messages_df.groupby('Date')['Message'].count().plot(kind='line', figsize=(20,10), color='#A26360',title = "Message distribution per day")
    plt.savefig(path+"\messages per day.png")
    
    weekday_grouped_msg =  (messages_df.set_index('weekday')['Message']
                          .groupby(level=0)
                          .value_counts()
                          .groupby(level=0)
                          .sum()
                          .reset_index(name='count'))
    weekday_grouped_msg

    fig = px.line_polar(weekday_grouped_msg, r='count', theta='weekday', line_close=True)
    fig.update_traces(fill='toself')
    fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
        )),
      showlegend=False
    )
    #fig.show()

    fig.write_image(path+'\weekday group message web chart.png')
    
    hour_grouped_msg =  (messages_df.set_index('hour')['Message']
                          .groupby(level=0)
                          .value_counts()
                          .groupby(level=0)
                          .sum()
                          .reset_index(name='count'))
    fig = px.bar(hour_grouped_msg, x='hour', y='count',
                     labels={'hour':'24 Hour Period'}, 
                     height=400)
    fig.update_traces(marker_color='#EDCC8B', marker_line_color='#D4A29C',
                      marker_line_width=1.5, opacity=0.6)
    fig.update_layout(title_text='Total Messages by Hour of the Day')
    #fig.show()

    fig.write_image(path+"\Total Messages by Hour of the day.png")
    
    grouped_by_month_and_day = messages_df.groupby(['month_sent', 'weekday'])['Message'].value_counts().reset_index(name='count')
    grouped_by_month_and_day
    months= ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pt = grouped_by_month_and_day.pivot_table(index= 'month_sent', columns= 'weekday', values='count').reindex(index=months, columns= days)
    fig = px.imshow(pt,
                    labels=dict(x="Day of Week", y="Months", color="Count"),
                    x=days,
                    y=months
                   )
    fig.update_layout(
        width = 700, height = 700)
    #fig.show()

    fig.write_image(path+"\Grouped by moth and day heatmap.png")
    
    #qty_message_author = messages_df['Author'].value_counts().head(10)
    #qty_message_author.plot(kind='barh',figsize=(20,10), color=['#D4A29C', '#E8B298', '#EDCC8B', '#BDD1C5', '#9DAAA2'])
    
    commond_words = messages_df[['Author','Message']].copy()


    stopwords = list(stopwords)
    extra = ["https://"]
    stopwords = stopwords + extra
    commond_words["Message"] = (commond_words["Message"]
                               .str.lower()
                               .str.split()
                               .apply(lambda x: [item for item in x if item not in stopwords])
                               .explode()
                               .reset_index(drop=True)
                     )

    #commond_words['Message']= commond_words['Message'].apply(remove_emoji)
    commond_words['Message']= commond_words['Message'].replace('nan', np.NaN)
    commond_words['Message']= commond_words['Message'].replace('', np.NaN)
    commond_words['Message']= commond_words.Message.str.replace(r"(a|j)?(ja)+(a|j)?", "jaja")
    commond_words['Message']= commond_words.Message.str.replace(r"(a|j)?(jaja)+(a|j)?", "jaja")


    words_dict = dict(Counter(commond_words.Message))
    words_dict = sorted(words_dict.items(), key=lambda x: x[1], reverse=True)

    words_dict = pd.DataFrame(words_dict, columns=['words', 'count'])

    fig = px.bar(words_dict.head(10).dropna(), x='words', y='count',
                     labels={'words':'Common Words'}, 
                     height=400)
    fig.update_traces(marker_color='#EDCC8B', marker_line_color='#D4A29C',
                      marker_line_width=1.5, opacity=0.6)
    fig.update_layout(title_text='Commond Words Chart')
    #fig.show()


    fig.write_image(path+"\Common words by all.png")
    
    TopTen =5
    author_commond_words =  (commond_words.set_index('Author')['Message']
                              .dropna()
                              .groupby(level=0)
                              .value_counts()
                              .groupby(level=0)
                              .head(TopTen)
                              .rename_axis(('Author','words'))
                              .reset_index(name='count'))

    l = author_commond_words.Author.unique()
    for i in range(len(l)):
        dummy_df = author_commond_words[author_commond_words['Author'] == l[i]]
        #print(dummy_df)
        #print('Most Commond Words by', l[i])
        fig = px.bar(dummy_df, x='words', y='count',
                     labels={'words':l[i] + ' Common Words'}, 
                     height=380)
        fig.update_traces(marker_color='#EDCC8B', marker_line_color='#D4A29C',
                      marker_line_width=1.5, opacity=0.6)
        fig.update_layout(title_text=l[i] + ' Commond Words Chart')
        #fig.show()

        fig.write_image(path+"\Common words by"+l[i]+".png")
        
        #function to display wordcloud

    #function to remove urls from text
    def remove_urls(text):
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return url_pattern.sub(r'', text)
    
    font='Lohit-Devanagari.ttf'
  
    for i in l:
        dummy = messages_df[messages_df.Author == i]
        chat_word_cloud = dummy[['Message']].copy()
        chat_word_cloud['Message']= chat_word_cloud['Message'].apply(remove_urls)
        chat_word_cloud['Message']= chat_word_cloud['Message'].replace('nan', np.NaN)
        chat_word_cloud['Message']= chat_word_cloud['Message'].replace('', np.NaN)
        chat_word_cloud['Message']= chat_word_cloud.Message.str.replace(r"(a|j)?(ja)+(a|j)?", "jaja")
        chat_word_cloud['Message']= chat_word_cloud.Message.str.replace(r"(a|j)?(jaja)+(a|j)?", "jaja")
        text = "".join(review for review in chat_word_cloud.Message.dropna())

        wordcloud = WordCloud(
            width=3000,
            height=2000,
            random_state = 1,
            background_color="white", 
            colormap = 'Set1',
            collocations = False,
            stopwords=stopwords,
            regexp=r"[\u0900-\u097F]+", 
            font_path=font
            ).generate(text)
            # Set figure size
        #plt.figure(figsize=(40, 30))
        # Display image
        #plt.imshow(wordcloud) 
        # No axis details
        #plt.axis("off");
        #plt.title(i);

        wordcloud.to_file(path+'\wordcloud for' + i + '.png')


# In[92]:


def get_Authors(filepath):
    def date_time(s):
        pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9]+), ([0-9]+):([0-9]+)[ ]?(AM|PM|am|pm)? -'
        result = regex.match(pattern, s)
        if result:
            return True
        return False

    def find_author(s):
        s = s.split(":")
        if len(s)==2:
            return True
        else:
            return False
            
    def getDatapoint(line):
        splitline = line.split(' - ')
        dateTime = splitline[0]
        date, time = dateTime.split(",")
        message = " ".join(splitline[1:])
        if find_author(message):
            splitmessage = message.split(": ")
            author = splitmessage[0]
            message = " ".join(splitmessage[1:])
        else:
            author= None
        return date, time, author, message

    data = []
        #conversation = 'WhatsApp Chat with Jeevika-i-Saksham fellows.txt'
    conversation = filepath
    with open(conversation, encoding="utf-8") as fp:
        fp.readline()
        messageBuffer = []
        date, time, author = None, None, None
        while True:
            line = fp.readline()
            if not line:
                break
            line = line.strip()
            if date_time(line):
                if len(messageBuffer) > 0:
                    data.append([date, time, author, ' '.join(messageBuffer)])
                    messageBuffer.clear()
                    date, time, author, message = getDatapoint(line)
                    messageBuffer.append(message)
            else:
                messageBuffer.append(line)


    df = pd.DataFrame(data, columns=["Date", 'Time', 'Author', 'Message'])
        
    return(list(df['Author'].unique()))

par = [1,2,3]

def file_browser():
    sg.theme("DarkTeal2")
    layout = [[sg.T("")], [sg.Text("Choose a file: "), sg.Input(), sg.FileBrowse(key="-IN-")],[sg.Button("Submit")]]

    ###Building Window
    window = sg.Window('My File Browser', layout, size=(600,150))

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            break
        elif event == "Submit":
            par[0] = values["-IN-"]
            window.close()

def folder_browser():
    sg.theme("DarkTeal2")
    layout = [[sg.T("")], [sg.Text("Choose a folder: "), sg.Input(key="-IN2-" ,change_submits=True), sg.FolderBrowse(key="-IN-")],[sg.Button("Submit")]]

    ###Building Window
    window = sg.Window('My File Browser', layout, size=(600,150))

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            break
        elif event == "Submit":
            par[1] = values["-IN-"]
            window.close()


# In[93]:


def checkbox():
    sg.SetOptions(element_padding=(0,1))

    lines = []
    
    n = len(get_Authors(par[0]))

    for x in get_Authors(par[0]):
        cb = sg.CB(text = x, key = x)
        lines.append([cb])
    
    #layout = [[sg.T('Author Lists', font='Any 15')],
              #*lines]

    layout = [[sg.T('Author Lists', font='Any 15')],
              [sg.Column(lines,size = (300,300),scrollable = True)]]
    form = sg.Window("USERS", layout, size = (300,300),resizable = True,)

    button, values = form.read()

    lst = []
    for val in values:
        if form.find_element(val).get()==True:
            lst.append(val)
    par[2] = lst


# In[94]:


file_browser()
folder_browser()
checkbox()
do(par[0],par[1],par[2])

sg.popup("Analytics Done!!", "Check Selected Folder For Analysis")


# In[ ]:




