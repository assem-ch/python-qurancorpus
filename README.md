# Quran Corpus Python Parser 
Python library to read and extract information from the [Quranic Arabic Corpus](http://corpus.quran.com/).

### Requirments 

- pyparsing:
            
            sudo pip install pyparsing
- [quranic-corpus-morpology.xml](http://corpus.quran.com/download/) , version 0.1


### Install
    
    sudo pip install qurancorpus
or

    sudo python setup.py install

### Usage
- Parse a morphology line

        >>> from qurancorpus import MorphologyParser
        >>> MorphologyParser.parse("fa+ POS:INTG LEM:maA l:P+")
        {'prefixes': [{'token': 'fa', 'type': '--undefined--'}], 'base': [{'lemma': 'maA', 'arabiclemma': u'\u0645\u064e\u0627', 'arabicpos': u'\u062d\u0631\u0641 \u0627\u0633\u062a\u0641\u0647\u0627\u0645', 'type': 'Particles', 'pos': 'Interogative particle'}], 'suffixes': []}

- List corpus words:
        
        >>> from qurancorpus import API
        >>> A = API(source="data/quranic-corpus-morpology.xml")
        A.all_words_generator()  # all words
        A.unique_words() # unique only
        