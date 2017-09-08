# python 3.4
import sys
import csv
import re
#from read_data import open_lexicon, compare, sort_data, compare_sections

class Article(object):
    def __init__(self, publisher,  date,  year, month, text):
        super(Article, self).__init__()
        self.publisher = publisher
        self.date = date
        self.year = year
        self.month = month
        self.text = text

class Month(object):
    def __init__(self, year, month, text, counter):
        super(Month, self).__init__()
        self.year = year
        self.month = month
        self.text = text
        self.emotions = []
        self.overall = 0
        self.counter = counter
        self.as_string = self.to_string()

    def to_string(self):
        string = '' + str(self.year) + ' ' + str(self.month) + ' ' + str(self.emotions) + ' ' + str(self.overall) + ' ' + str(self.counter)
        return string

def read_articles(file):
    file = open(file , newline = '')
    spamreader = csv.reader(file, delimiter='\t', quotechar='|')
    data_set = []

    for line in spamreader:

        if(len(line) > 2): 
            publisher = line[0]
            date = line[1]
            found = re.search(r"\d\d\d\d[-/]\d\d[-/]\d\d", date) 
            if(not found):
                break

            if(len(line) >= 5):
                
                if(len(line) >= 6):
                    line[4] = line[4] + line[5]

                year = line[2]
                month = line[3]
                text  = line[4]

                article = Article(publisher, date, year, month, text)
                data_set.append(article)

    file.close()
    return data_set

def over_all_emos(data_set):

    text = ''

    for art in data_set:
        #print(art.text)
        text = text + ' ' + art.text

    (emos,_) = compare_articles(open_lexicon(), art.text)
    emos = sort_data(emos)
    return emos

def compare_articles(lexicon, file):
    counter = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    c = 0
    all_emos = 0
    splitted_line = re.split('\W+', file)
       
    for word in splitted_line:
        # if word is in lexicon, add counter up for every '1' in the values of the word 
        try:
            value = lexicon[word]
            is_emotional = False

            for i in value:
                if(i == '1'):
                    counter[c] = counter[c] + 1

                if((i == '1') & (c > 1)):
                    is_emotional = True

                c = c + 1
            c = 0

            if(value != None):
                all_emos = all_emos + 1

        except KeyError:
            pass
    return counter, all_emos

def emotions_monthly(data_set):

    year = data_set[0].year
    month = data_set[0].month
    text = ''
    emos = []
    counter = 0

    for art in data_set:

        if(year != art.year):
            new = Month(year, month, text, counter)
            (new.emotions, new.overall) = compare_articles(open_lexicon(),new.text)
            new.emotions = sort_data(new.emotions)
            emos.append(new)

            text = art.text
            year = art.year
            month = str(1.0)
            counter = 0

        elif(month != art.month):
            new = Month(year, month, text, counter)
            (new.emotions, new.overall) = compare_articles(open_lexicon(),new.text)
            new.emotions = sort_data(new.emotions)
            emos.append(new)

            text = art.text
            month = art.month
            counter = 0
        else:
            text = text + art.text
            counter += len(art.text.split())

    new = Month(year, month, text, counter)
    (new.emotions, new.overall) = compare_articles(open_lexicon(),new.text)
    new.emotions = sort_data(new.emotions)
    emos.append(new)

    return emos

def read_data_set():
    emotions = []

    for i in range(4,8):
        file_loc = '../data/all-the-news/article201'+ str(i) +'.csv'
        data_set = read_articles(file_loc)
        emotions.extend(emotions_monthly(data_set))

    return emotions

def read_data_set(file):
    emotions = []

    
    data_set = read_articles(file)
    emotions.extend(emotions_monthly(data_set))

    return emotions

def sum_data_set(data_set):
    c = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dates = []
    for e in data_set:
        dates.append(e.month + '/' + e.year)
        for i, s in enumerate(e.emotions):
            c[i] = c[i] + s

    return c, dates

def read_file(file_loc):
    file = open(file_loc)
    data = []
    counter = 0
    counter_total = 0

    for line in file:
        line = line.split()
        year = line[0]
        month = line[1]

        emotions = line[2][1:-1]
        for i in range(3,12):
            emotions += ' ' + line[i][:-1]
        overall = line[12]

        counter = line[13]
        counter_total += int(line[13])
        
        month = Month(year, month, 'text', counter)
        month.emotions = list(map(int, emotions.split()))
        month.overall = int(overall)
        data.append(month)
    return data, counter_total

def open_lexicon():
    file = open("../data/lexicon_english.csv", newline = '')
    spamreader = csv.reader(file, delimiter='\t', quotechar='|')
    lexicon = {}

    for line in spamreader:
        liste = [line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10]]
        lexicon[line[0]] = liste
        del liste

    file.close()
    return lexicon

def sort_data(data):

    pos = data[0]
    neg = data[1]
    anger = data[2]
    anticipation = data[3]
    disgust = data[4]
    fear = data[5]
    joy = data[6]
    sadness = data[7]
    surprise = data[8]
    trust  = data[9]

    new_data = [pos, neg, joy, trust, fear, surprise, sadness, disgust, anger, anticipation]
    return new_data