# -*- coding: utf-8 -*-
"""
Created on Fri May  3 15:55:59 2019

@author: 依蒨
"""

import nltk
from bs4 import BeautifulSoup as bs
import requests
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import defaultdict
from pattern.en import lemma
from nltk.corpus import brown


#nltk.download('brown')




"""
[A]

Purpose: Function for Creating Bigram Dictionary
Input: Article in form of list after removing stop words
Output: Bigram dictionary of the filtered (removing stop words) article and the frequency of each word pair
"""
def bigramDict(word_list):
    bigram_list = []
    bigram_dict = dict()
    
    for i in range(0, len(word_list) - 2):
        bigram_list.append([word_list[i], word_list[i + 1]])
    
       
    for (w_1, w_2) in bigram_list:
        
        if w_1 not in bigram_dict:    
            bigram_dict[w_1] = {}
        
        if w_2 not in bigram_dict[w_1]:
            bigram_dict[w_1][w_2] = 1
        else:
            bigram_dict[w_1][w_2] += 1
     
        
    return bigram_dict


"""
[B]

Purpose: Function for determining the category of the website article
Input: Send lemmatized dictionary of collected text
Output: Category of the text from website
Description: If the lemmatized words in web_dict matches the lemmatized words in dictionary of 
each category, scores --(frequency in the specific category / total words in the specific category) * the frequency of the word in web_dict --
will be added. The one who gives the highest score is the category of the web article.
"""
def getCategory(web_dict):
    
    br_categories = brown.categories()
    cat_dict = defaultdict(int)
    stop_words = set(stopwords.words('english'))
    
    max_score = 0 #max_score stores the current highest score of the matching process
    max_cat = '' #max_cat stores the name of category with current highest max_score
    
    for category in br_categories:
        cur_score = 0
        for word in brown.words(categories = category):
            if not re.search(r"[.\,:;""\-''?!]", word) and word not in stop_words:
                word = word.lower()
                word = lemma(word)
                cat_dict[word] += 1
    
        cat_wds = sum(cat_dict.values())
        
        for web_wd in web_dict.keys():
            if web_wd in cat_dict.keys():
                cur_score += (cat_dict[web_wd] / cat_wds) * web_dict[web_wd]
        
        if cur_score > max_score:
            max_score = cur_score 
            max_cat = category
              
        
    return max_cat



"""
[C]

Crawl content from given link and stored the content into lists and dictionaries
"""

link = input('Enter a link: ')
r = requests.get(link)


# Whether or not is downloaded successfully
if r.status_code == requests.codes.ok:
    
    #Parse HTML code with BeautifulSoup
    soup = bs(r.text, 'html.parser')
    
    #Crawl the content
    cnn_tag_name = 'div.zn-body__paragraph'
    content = soup.select(cnn_tag_name)
    index = 0
    tag_pattern = re.compile('<[^>]*>') #remove all the html tags
    
    sym_pattern = re.compile('[.\,:;""\-''?!\d]') #remove all the symbols
    
    #filtered and unfiltered article; data type --> lsit
    filtered_art = []
    unfiltered_art = []
    art_sent = [] #take [SENTENCE] as a unit / UNfiltered
    
    #Unfiltered uni_gram freq dict
    all_words_freq = defaultdict(int)
    
    #Filtered uni_gram freq dict
    uni_gram_freq = defaultdict(int)
    
    #Lemmatized uni_gram freq dict
    lemma_uni_gram = defaultdict(int)
    
    stop_words = set(stopwords.words('english'))
    

    for paragraph in content: 
        paragraph = tag_pattern.sub("", str(paragraph))
        
        #Count sentence number
        for sent in paragraph.split('.')[:-1]:
            
            sent = sent + '.'
            art_sent.append(sent) #add untokenized sentence to art_sent(list)
            
            
            #Remove stop words
            #sentence is now tokenized into words
            sent = sym_pattern.sub("", sent)
            tokenized_sent = word_tokenize(sent.lower()) #Data_type --> list
            unfiltered_art.append(tokenized_sent) #append every tokenized [SENTENCE]
           
            for word in tokenized_sent:
                if word not in stop_words:
                    filtered_art.append(word) #append [WORDS] to this list
                   
        
    #Create unfiltered uni_gram dictionary and LEMMATIZED uni_gram freq dict
    for sent in unfiltered_art:
        for word in sent:
            if not re.search(r"[.\,:;""\-''?!]", word):
                lower_word = word.lower()
                all_words_freq[lower_word] += 1
            
    
    #Create uni_gram and lemma_uni_gram dictionary -- filtered article 
    for word in filtered_art:
        if not re.search(r"[.\,:;""\-''?!]", word):
            uni_gram_freq[word] += 1
            lemma_uni_gram[lemma(word)] += 1
    
    art_bigram_dict = bigramDict(filtered_art)

"""
[D]

Purpose: Determine the topic of this article: Freq of unigram and bigram
Description:
Retrieve the word and word pair with the highest frequency. If the frequency of the single word equals to
that of the word pair, it is possible that a phrase rather than single words is the topic of this article.
Therefore, if this happen, set the phrase as the topic of the sentence. If not, print the one with higher frequency.

"""

uni_max_freq = max(uni_gram_freq.values())
uni_max_wrd = [k for k, v in uni_gram_freq.items() if v == uni_max_freq]



bi_max_freq = 0
for fst_wd, snd_wd_and_freq in art_bigram_dict.items():
    if max(art_bigram_dict[fst_wd].values()) > bi_max_freq:
        bi_max_freq = max(art_bigram_dict[fst_wd].values())
        for snd_wd, freq in snd_wd_and_freq.items():
            if freq == bi_max_freq:
                bi_max_wds = [fst_wd, snd_wd]

#If the frequencies of uni_gram and bi_gram are the same, the two words might co-occur
                
topic_str = "  ".join(uni_max_wrd) #Default
if uni_max_freq == bi_max_freq:
    for (wd_1, wd_2) in bi_max_wds:
        if not re.search(r"[.\,:;""\-''?!]", wd_1) and re.search(r"[.\,:;""\-''?!]", wd_2):
            for sent in unfiltered_art:
                wd_between = sent.index(wd_2) - sent.index(wd_1)
                if wd_between > 0 and wd_between < 5:
                    topic_str = "  ".join(sent[sent.index(wd_1):sent.index(wd_1) + 1])
"""
[E]

Call "getCategory" function.
web_cat is a variable that stores the category of this article
"""

web_cat = getCategory(lemma_uni_gram)


print("This article is about %s." % topic_str)
print("Category of this article: %s" % web_cat)

                    
            
