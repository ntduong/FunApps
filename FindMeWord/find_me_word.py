"""
    Created on 2014/05/25
    @Author: Duong Nguyen 
    @Email: ntduong268@gmail.com

    @Problem: Given an English word, find the most probable previous word.
    E.g: Find the top 10 most probable adjectives that might come right before "book"
    Here is the answer from my program along with their scores.
        comic book: 0.079216
        each book: 0.017782
        guest book: 0.010254
        wonderful book: 0.006445
        rare book: 0.006061
        sport book: 0.004989
        excellent book: 0.004824
        upcoming book: 0.004552
        latest book: 0.004399
        printed book: 0.004124
    
    @Dataset: 
        1. Modified Google Corpus at http://norvig.com/ngrams/
        2. Part of speech word lists at http://www.ashley-bovan.co.uk/words/partsofspeech.html
    
    @Version: The 0-th naive version
"""

import os
from collections import defaultdict

DATAFOLDER = "./data"

## Utilities
def gen_data(fname, sep="\t"):
    """ Generate key, count pairs from file."""
    
    with open(fname, "r") as fin:
        for line in fin:
            yield line.strip().split(sep)
            
def handle_unk_long_words(w, total):
    """ Estimate the probability of an unknown long word.
        Discount the probability by a factor of 10, proportional to its length.
    """
    return 10./(total * 10**len(w))
    

class WordDist(object):
    """ Simple language model that estimates the probability of a word based on its count.""" 
    
    def __init__(self, data, total=None, handle_missing=None):
        
        self.wcount = defaultdict(int)
        for k, v in data:
            self.wcount[k] += int(v)
        
        if total == None:
            self.total = float(sum(self.wcount.itervalues()))
        else:
            self.total = float(total) 
            
        self.handle_missing = handle_missing or (lambda k, total: 1./total)
        
    def prob(self, w):
        """ Estimate the probability of the given word w."""
        
        if w in self.wcount:
            return self.wcount[w] / self.total
        else:
            return self.handle_missing(w, self.total)
        
class SimpleModel(object):
    """ Simple language model consisting of unigram and bigram distributions."""
    
    def __init__(self, ufile, bfile, n_tokens=None):
        
        if n_tokens == None:
            self.n_tokens = 1024908267229 # total number of tokens in the corpus
        else:
            self.n_tokens = n_tokens
            
        self.unigram_dist = WordDist(gen_data(ufile), self.n_tokens, handle_unk_long_words)
        self.bigram_dist = WordDist(gen_data(bfile), self.n_tokens, handle_unk_long_words)
        
    def cond_prob(self, word, prev):
        """ Estimate the conditional probability of a word, given previous word.
            If not found bigram prev-word then falling back to unigram word. 
        """
        bigram = " ".join((prev, word))
        if (bigram in self.bigram_dist.wcount) and (prev in self.unigram_dist.wcount):
            return self.bigram_dist.wcount[bigram] / float(self.unigram_dist.wcount[prev])
        else:
            return self.unigram_dist.prob(word)
            
def get_model(ufname="count_1w.txt", bfname="count_2w.txt"):
    """ Return a count-based language model from given corpus files."""
    
    ufile = os.path.join(DATAFOLDER, ufname)
    bfile = os.path.join(DATAFOLDER, bfname)
    m_Model = SimpleModel(ufile, bfile)
    return m_Model
    
## DEMO APPLICATIONS
def find_your_adjectives(noun, k=5):
    """ Suggest the top k most probable adjective which might come right before the given noun."""
    
    # First, load the list of all possible adjective from file
    adj_list = []
    with open(os.path.join(DATAFOLDER, "adjectives", "28k_adjectives.txt")) as adjs:
        for line in adjs:
            adj_list.append(line.strip().lower())
    
    # Obtain our language model        
    m_Model = get_model()
    
    score = map(lambda a: m_Model.cond_prob(noun, a), adj_list)
    score_2_adj = zip(score, adj_list)
    return sorted(score_2_adj, reverse=True, key=lambda item: item[0])[:k]
    
def main():
    noun = "student"
    top_probable_adjs = find_your_adjectives(noun, k=10)
    for ans in top_probable_adjs: # print adj-noun and its score
        print "%s: %f" %(ans[1] + " " + noun, ans[0])
    
    
if __name__ == "__main__":
    main()
    
    
    