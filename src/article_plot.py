# python 3.4
import re
import sys
import csv
import math
import os.path
import numpy as np
# change backend
import matplotlib
matplotlib.use('TkAgg')
from pylab import *
import matplotlib.pyplot as plt 
from matplotlib import gridspec
import matplotlib.path as mpath
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.image as mpimg
from matplotlib.collections import PatchCollection
from matplotlib.cbook import get_sample_data
from matplotlib.widgets import Button
from matplotlib.widgets import SpanSelector

from read_data import read_data_set, sum_data_set, Month, read_file

#global variables
explode = [ 0, 0, 0, 0, 0, 0, 0, 0]
counter = []
dates = []
pos = 0
neg = 0

flower_patches = []

emos = []
emo_words_all = 0
words_total = 0

handler = None
span = None
span_min, span_max, span_id = 0, 0, None
emos_clicked, mood_clicked = True, False
emos_mood = 0 # 0 = emos, 1 = mood

y_label = 'Emotions [%]'

fig = None

plain_img = plt.imread('../data/legend.png', format='png')

plt.ion()

class FlowerEventHandler:
    global explode, handler, flower_patches, span, emos_clicked, mood_clicked 

    def __init__(self,p):
        self.fig = p
        self.ax = p.axes

        self.fig.canvas.mpl_connect('button_press_event', self.onpress)
        self.fig.canvas.mpl_connect('key_press_event', self.onkey)

    def onpress(self, event):
        global explode, flower_patches, span, handler, emos_clicked, mood_clicked, emos_mood, y_label

        ax = event.inaxes

        if(self.ax[-1] == ax):
            if(mood_clicked):
                emos_clicked = True
                mood_clicked = False
                emos_mood = 0
                y_label = 'Emotions [%]'
                self.update()
                return
            else:
                emos_clicked = False
                mood_clicked = True
                emos_mood = 1
                y_label = 'Positive/Negative [%]'
                self.update()
                return
        else:
            for i in range(1,9):

                w = flower_patches[i]
                
                hit = w.get_path().contains_point([event.xdata, event.ydata])

                if hit: 

                    if(explode[i-1] == 0):
                        explode[i-1] = 1
                    else:
                        explode[i-1] = 0

                    self.update()
                    return

            self.update()
            return

    def onkey(self,event):
        if(event.key == 'q'):
            plt.close()

    def update(self):
        global explode, handler, flower_patches, span
        self.fig.clear()
        (plot, stacked) = make_flower()
        span = SpanSelector(stacked, onselect, 'horizontal', useblit=True,
                rectprops=dict(alpha=0.5, facecolor='red'))
        handler = FlowerEventHandler(plot)

def make_pct(values, i):
    global emo_words_all
    val = values[i]
    pct = val/emo_words_all*100.0
    return '{p:0.2f}% \n({v:d})'.format(p=pct,v=val)

def map_colors(values):

    percentages = []
    total = sum(values)

    for el in values :
        percentages.append(el/total)

    joy = [('#c3bb30'),('#e5db33'),('#f4ec63'),('#FFF999')]
    anticipation = [('#bd6000'),('#ea7f14'),('#ffb060'),('#ffdbb6')]
    anger = [('#660000'),('#9f2524'),('#c36666'),('#CD9B9B')]
    disgust = [('#4B0082'),('#852ab8'),('#BA55D3'),('#DDA0DD')]
    sadness = [('#0c4981'),('#1c76c7'),('#63b4ff'),('#b2daff')]
    surprise = [('#5f8c9c'),('#8bb4c3'),('#b7d8e3'),('#d8eaf0')]
    fear = [('#284710'),('#507236'),('#87ae6a'),('#bed4ad')]
    trust = [('#83b817'),('#9fdb28'),('#c1f260'),('#ddff99')] 

    colors = [joy[select(percentages[0])], trust[select(percentages[1])], fear[select(percentages[2])],
     surprise[select(percentages[3])], sadness[select(percentages[4])], disgust[select(percentages[5])], 
     anger[select(percentages[6])], anticipation[select(percentages[7])]]

    return colors

def make_flower():
    global counter, fig, pos, neg, init, flower_patches, emo_words_all, words_total


    fig = plt.figure('Visualization of Emotions in News Articles', figsize=(16,9), dpi=120, facecolor='white', edgecolor='blue')
    ax = fig.add_subplot(223)

    generate_path()

    collection = PatchCollection(flower_patches)
    colors = map_colors(counter)
    colors_flower = ['white'] + colors
    collection.set_color(colors_flower)
    ax.add_collection(collection)
    plt.axis('equal')
    plt.axis('off')

    num_shapes = 8
    center = [0,0]
    r1 = 1.5
    r2 = 3
    angle = (math.pi * 2 / num_shapes)
    labels = 'Joy', 'Trust', 'Fear', 'Surprise', 'Sadness', 'Disgust', 'Anger', 'Anticipation'
    r_l = 3.9
    for i in range(0, num_shapes):
        x = math.cos((i-6) * (angle)) 
        y = math.sin((i-6) * (angle)) 
        label_str = labels[i] + '\n' + make_pct(counter, i)
        plt.text((x*r_l) -0.55, y*r_l-0.5 , label_str)

    make_bar(pos, neg)
    make_legend()
    axes = make_stacked(colors)
    make_buttons()

    text_bottom_left = ax.text(-6, 4.4, 'Emotion words: ' + str(emo_words_all) + '\nWords in total:  ' + str(words_total))
    text_bottom_left.set_fontsize(9)

    text1 = plt.text(-3.83, 20.75, 'Visualization of Emotions in News Articles from 2014 to 2017', weight = 'bold', fontsize=20)
    text2 = plt.text(-2.4, 7, 'Click on the flower to deselect/select an\n'
        'emotion from the right plots or select a\n'
        'range in the upper right plot to be shown\n'
        'in the lower right plot.\n\n'
        'Click on the MOOD/EMOTIONS button\n'
        'to switch between the visualization of\n'
        'positiv and negativ or emotion words.\n\n'
        'You can see the legend of colors and\n'
        'the ratio between positv and negativ\n'
        'words over all given years.')

    return fig, axes

def generate_path():
    global explode, flower_patches

    center = [0,0]
    r1 = 2
    r2 = r3 = 3
    num_shapes = 8
    angle = (math.pi * 2 / num_shapes)
    c = 0.4
    wide = 0.3

    flower_patches = []
    circle = mpatches.Circle(center, 3.3, visible=False)
    flower_patches.append(circle)

    for i in range(0,num_shapes):
        Path = mpath.Path
        if(explode[i] == 0):
            path_data = [
                (Path.MOVETO, center),
                (Path.CURVE4, [math.cos(((i-6) * angle)-c) * r1, math.sin(((i-6) * angle)-c) * r1]),
                #(Path.CURVE4, [math.cos((i-6) * (angle)-c) * r2, math.sin((i-6) * (angle)-c) * r2]),
                (Path.CURVE4, [math.cos((i-6) * (angle)) * r3, math.sin((i-6) * (angle)) * r3]),

                (Path.MOVETO, [math.cos((i-6) * (angle)) * r3, math.sin((i-6) * (angle)) * r3]),

                #(Path.CURVE4, [math.cos(((i-6) * angle)+c) * r2, math.sin(((i-6) * angle)+c) * r2]),
                (Path.CURVE4, [math.cos(((i-6) * angle)+c) * r1, math.sin(((i-6) * angle)+c) * r1]),
                (Path.CURVE4, center),

                (Path.MOVETO, center),
                (Path.CLOSEPOLY, center)
                ]
        else:
            r_explode = 0.3
            x = math.cos((i-6)*angle)
            x_c1 = math.cos(((i-6) * angle)-c+0.05)
            x_c2 = math.cos(((i-6) * angle)+c-0.05)
            y = math.sin((i-6)*angle)
            y_c1 = math.sin(((i-6) * angle)-c+0.05)
            y_c2 = math.sin(((i-6) * angle)+c-0.05)
            center2 = [x * r_explode, y * r_explode]

            path_data = [
                (Path.MOVETO, center2),
                (Path.CURVE4, [x_c1 * (r1+r_explode), y_c1 * (r1+r_explode)]),
                (Path.CURVE4, [x * (r2+r_explode), y  * (r2+r_explode)]),
                (Path.MOVETO, [x * (r2+r_explode), y * (r2+r_explode)]),
                (Path.CURVE4, [x_c2 * (r1+r_explode), y_c2 * (r1+r_explode)]),
                (Path.CURVE4, center2),
                (Path.MOVETO, center2),
                (Path.CLOSEPOLY, center2)
                ]

        codes, verts = zip(*path_data)
        path = mpath.Path(verts, codes)
        patch = mpatches.PathPatch(path)
        
        flower_patches.append(patch)


def make_bar(pos, neg):
    global fig

    ax = fig.add_subplot(30,9,92)
    ax.set_yticks([])
    ax.set_xlim([0, 100])
    ax.set_title('Negative/Positive emotion words')

    summ = pos + neg
    # the bar doesn't add up, it overlaps, for that we have to summ up the neg to the pos (=100)
    ax.barh(0, 100, color='#68ae66') 
    ax.barh(0, (neg/summ)*100, color='#a93f3b')

def make_legend():
    global plain_img, fig
    ax = fig.add_subplot(331)
    img_plot = ax.imshow(plain_img)
    ax.axis('off')

def make_buttons():
    global fig, emos_clicked, mood_clicked

    ax_mood = fig.add_subplot(31,17,246)
    ax_mood.bar(0,1, color='w')
    ax_mood.axis('off')
    if(mood_clicked):
        ax_mood.text(-0.35,0.1,'EMOTIONS',bbox={'facecolor':'#aeaeae', 'edgecolor':'black', 'boxstyle':'round', 'pad':0.3})
    else:
        ax_mood.text(-0.35,0.1,'   MOOD   ',color='w',bbox={'facecolor':'#696969', 'edgecolor':'black', 'boxstyle':'round', 'pad':0.3})

def make_stacked(colors):
    global fig, emos, span_min, span_max, span_id, emos_mood, y_label, dates
    ax1 = fig.add_subplot(222)
    span_id = len(fig.axes)
    ax2 = fig.add_subplot(224) 

    show_emos = []
    show_colors = []
    if(emos_mood == 0): # emos
        for i, e in enumerate(explode):
            if(e == 0):
                show_emos.append(emos[i+2])
                show_colors.append(colors[i])

    else:
        show_emos.append(emos[0])
        show_emos.append(emos[1])

        show_colors.append('#68ae66')
        show_colors.append('#a93f3b')


    if(len(show_emos) == 0):
        ax1.set_xlim(0,45)
        return

    if(len(show_emos) == 1):
        ax1.set_ylim(0,max(show_emos[0]))
        ax2.set_ylim(0,max(show_emos[0]))


    ax1.stackplot(range(len(emos[1])), show_emos, colors=show_colors)
    ax1.set_xlim(0,len(emos[0])-1) 
    ax1.set_xticks(np.arange(0,len(emos[0]), 5))
    ax1.set_xticklabels(dates[0::5])
    ax1.set_ylabel(y_label)
    ax1.set_xlabel('Month')

    ax2.stackplot(range(len(emos[1])), show_emos, colors=show_colors)
    if(span_max == 0):
        span_max = len(emos[0])-1

    ax2.set_xticks(np.arange(0,len(emos[0]), 5))
    ax2.set_xticklabels(dates[0::5])
    ax2.set_xlim(span_min,span_max) # update with slider
    ax2.set_ylabel(y_label)
    ax2.set_xlabel('Month')

    return ax1


def onselect(xmin, xmax):
    global fig, span_min, span_max, span_id, dates
    ax_list = fig.axes
    ax2 = ax_list[span_id]
    span_min, span_max = xmin, xmax
    dif = int(span_max - span_min)
    if(dif < 5):
        dif = 1
    elif(dif < 10):
        dif = 2
    elif(dif < 20):
        dif = 3
    elif(dif < 30):
        dif = 4
    else:
        dif = 5
    ax2.set_xticks(np.arange(0,len(emos[0]), dif))
    ax2.set_xticklabels(dates[0::dif])
    ax2.set_xlim(xmin, xmax)


def set_emos(data):
    global emos, emo_words_all

    emos = [[] for _ in range(10)]
    for el in data:
        emo_words_all += el.overall
        summe = sum(el.emotions[0]+el.emotions[1])
        emos[0].append((el.emotions[0]/summe)*100)
        emos[1].append((el.emotions[1]/summe)*100)
        for i in range(2,10):
            emos[i].append((el.emotions[i]/el.overall)*100)


def select(num):
    if (num <= 0.05):
        return 3
    elif (num <= 0.1):
        return 2
    elif (num <= 0.15):
        return 1
    else:
        return 0


def main2():
    global explode, pos, neg, emos, counter, handler, span, dates, words_total
    
    (data_set, words_total) = read_file('../data/article_compact.txt')
    (counter, dates) = sum_data_set(data_set)
    set_emos(data_set)
    pos = counter.pop(0)
    neg = counter.pop(0)

    (plot, stacked) = make_flower()
    handler = FlowerEventHandler(plot)
    span = SpanSelector(stacked, onselect, 'horizontal', useblit=True,
                rectprops=dict(alpha=0.5, facecolor='red'))

    subplots_adjust(left=0.0, bottom=0.1, right=0.95, top=0.91, wspace=0.04, hspace=0.22)
    plt.show(block = True)

def main(file_loc):
    global explode, pos, neg, emos, counter, handler, span, dates, words_total

    if('.txt' not in file_loc):
        file_txt = file_loc[:-3] + 'txt'

        if not os.path.exists(file_txt):
            data_set = read_data_set(file_loc)

            file = open(file_txt, 'w')
            for month in data_set:
                file.write(month.to_string() + '\n')
            file.close()
        
        file_loc = file_txt

    (data_set, words_total) = read_file(file_loc)
    (counter, dates) = sum_data_set(data_set)
    set_emos(data_set)
    pos = counter.pop(0)
    neg = counter.pop(0)

    (plot, stacked) = make_flower()
    handler = FlowerEventHandler(plot)
    span = SpanSelector(stacked, onselect, 'horizontal', useblit=True,
                rectprops=dict(alpha=0.5, facecolor='red'))

    subplots_adjust(left=0.0, bottom=0.1, right=0.95, top=0.91, wspace=0.04, hspace=0.22)
    plt.show(block = True)


if __name__ == '__main__':
    if(len(sys.argv) != 2):
        main2()
    else:
        main(sys.argv[1])