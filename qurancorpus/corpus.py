#!/usr/bin/env python2
# encoding:utf-8

"""
@author: Assem Chelli
@contact: assem.ch [at] gmail.com
@license: GPL
"""

# import libxml2#,xpath
import xml.etree.ElementTree
from pyparsing import Keyword, Word, Group, Literal, CharsNotIn, alphas
from pyparsing import SkipTo, ZeroOrMore, Optional, OneOrMore

from constants import BUCKWALTER2UNICODE
from constants import DERIV, PREFIX, PGN, POS, VERB, NOM, PRON
from constants import DERIVclass, NOMclass, PGNclass, VERBclass, PREFIXclass, POSclass


def reverse_class(dictionary):
    """ invert a dictionary """
    newdict = {}
    for key, value in dictionary.iteritems():
        if type(value) is not list:
            value = [value]
        for v in value:
            if v in newdict:
                newdict[v].append(key)
            else:
                newdict[v] = [key]
    return newdict


def buck2uni(string):
    """ decode buckwalter """
    result = ""
    for ch in string:
        result += BUCKWALTER2UNICODE[ch]
    return result


def tag_keywords(list_tags):
    """a specific pyparsing term to match tags return Keywords
     """
    res = list_tags[0]
    for item in list_tags[1:]:
        res |= Keyword(item)
    return res


def tag_literals(list_tags):
    """a specific pyparsing term to match tages return Literals"""

    res = list_tags[0]
    for item in list_tags[1:]:
        res |= Literal(item)
    return res

class MorphologyParser:
        """ parse the Morphology tags """

        def __init__(self):
            pass

        @staticmethod
        def parse_step1(morph):
            """parse the field morphology of qurany corpus

            """

            string = "$ " + str(morph).replace("POS:", "£ POS:") \
                .replace("PRON:", "µ PRON:") \
                .replace("&lt;", "<") \
                .replace("&gt;", ">") + " #"
            # regular expressions
            begin = Keyword('$').suppress()
            center = Keyword('£').suppress()
            last = Keyword('µ').suppress()
            end = Keyword('#').suppress()
            skip = SkipTo(end).suppress()

            prefix = Word(alphas + "+" + ":")
            prefixes = Group(ZeroOrMore(~center + prefix))

            genderK = tag_keywords(["M", "F"])
            numberK = tag_keywords(["S", "D", "P"])
            # personK = tag_keywords(["1", "2", "3"])

            genderL = tag_literals(["M", "F"])
            numberL = tag_literals(["S", "D", "P"])
            personL = tag_literals(["1", "2", "3"])

            person_ = personL + Optional(genderL) + Optional(numberL)
            gender_ = genderL + numberL

            gen = person_ | gender_ | numberK | genderK
            pos = "POS:" + Word(alphas)
            lem = "LEM:" + CharsNotIn(" ")
            root = "ROOT:" + CharsNotIn(" ")
            sp = "SP:" + CharsNotIn(" ")
            mood = "MOOD:" + CharsNotIn(" ")

            aspect = tag_keywords(["PERF", "IMPF", "IMPV"])

            voice = tag_keywords(["ACT", "PASS"])
            form = tag_keywords(
                ["(I)", "(II)", "(III)", "(IV)", "(V)", "(VI)", "(VII)", "(VIII)", "(IX)", "(X)", "(XI)", "(XII)"])
            verb = aspect | voice | form

            voc = Keyword("+voc").suppress()

            deriv = tag_keywords(["ACT", "PCPL", "PASS", "VN"])

            state = tag_keywords(["DEF", "INDEF"])
            case = tag_keywords(["NOM", "ACC", "GEN"])
            nom = case | state

            tag = lem | root | sp | mood | gen | verb | deriv | nom | voc | skip
            part = Group(center + pos + ZeroOrMore(~center + ~last + ~end + tag))

            base = Group(OneOrMore(~end + ~last + part))

            pron = "PRON:" + Group(gen)
            suffixes = Group(ZeroOrMore(~end + last + pron))

            whole = begin + prefixes + base + suffixes + end

            parsed = whole.parseString(string)

            return parsed

        @staticmethod
        def parse_step2(parsedlist):
            """ return a dict """
            Dict = {}
            # prefixes
            prefixes = parsedlist[0]
            Dict["prefixes"] = []
            if prefixes:
                for prefix in prefixes:
                    prefixDict = {
                        "token": PREFIX[prefix][1],
                        "arabictoken": PREFIX[prefix][0],
                        "type": reverse_class(PREFIXclass)[prefix][0]
                    }
                    Dict["prefixes"].append(prefixDict)

            # word base
            parts = parsedlist[1]
            Dict["base"] = []
            for part in parts:
                partDict = {}
                for i in range(len(part)):
                    tag = part[i]
                    if tag[-1] == ":":
                        nexttag = part[i + 1]
                        if tag == "POS:":
                            partDict["type"] = reverse_class(POSclass)[nexttag][0]
                            partDict["pos"] = POS[nexttag][1]
                            partDict["arabicpos"] = POS[nexttag][0]
                        elif tag == "ROOT:":
                            partDict["root"] = nexttag
                            partDict["arabicroot"] = buck2uni(nexttag)
                        elif tag == "LEM:":
                            partDict["lemma"] = nexttag
                            partDict["arabiclemma"] = buck2uni(nexttag)
                        elif tag == "SP:":
                            partDict["special"] = nexttag
                            partDict["arabicspecial"] = buck2uni(nexttag)
                        elif tag == "MOOD:":
                            partDict["mood"] = VERB[nexttag][1]
                            partDict["arabicmood"] = VERB[nexttag][0]
                        else:
                            print "new tag!! " + tag
                        i += 1
                    else:
                        if tag in PGN:
                            partDict[reverse_class(PGNclass)[tag][0]] = PGN[tag]
                        elif tag in ["ACT", "PASS"]:
                            nexttag = part[i + 1] if i + 1 < len(part) else None
                            if nexttag == "PCPL":
                                partDict[reverse_class(DERIVclass)[tag + " PCPL"][0]] = DERIV[tag + " PCPL"][1]
                                i += 1
                        elif tag in VERB:
                            partDict[reverse_class(VERBclass)[tag][0]] = VERB[tag][1]

                        elif tag in NOM:
                            def arabize(x):
                                return "arabicstate" if x == "state" else "arabiccase"

                            partDict[reverse_class(NOMclass)[tag][0]] = NOM[tag][1]
                            partDict[arabize(reverse_class(NOMclass)[tag][0])] = NOM[tag][0]

                        elif tag == "VN":
                            partDict[reverse_class(DERIVclass)[tag][0]] = DERIV[tag][1]

                Dict["base"].append(partDict)

            # suffixes
            suffixes = parsedlist[2]
            Dict["suffixes"] = []
            if suffixes:
                for i in range(len(suffixes)):
                    tag = suffixes[i]
                    if tag == "PRON:":
                        pronDict = {}
                        Pset = set(PRON["*"])
                        pronprops = suffixes[i + 1]
                        for tag in pronprops:
                            if tag in PGN:
                                pronDict[reverse_class(PGNclass)[tag][0]] = PGN[tag]
                                Pset &= PRON[tag]

                        pronDict["arabictoken"] = Pset.pop() if Pset else ""
                        Dict["suffixes"].append(pronDict)

            return Dict

        @staticmethod
        def parse(string):
            return MorphologyParser.parse_step2(MorphologyParser.parse_step1(string))



class API:
    def __init__(self, source="./data/quranic-corpus-morpology.xml"):
        """
        init the API based on XMLfile
        @param source: the path of the xml file
        """
        self.corpus = xml.etree.ElementTree.parse(source)
        # libxml2.parseFile(source)
        # print xpath.find('//item', source)


    def unique_words(self):
        """return a dictionary: the keys is word tokens and the values is the properties"""
        D = {}
        for chapter in self.corpus.findall(".//chapter"):
            for verse in chapter.findall("verse"):
                for word in verse.findall("word"):
                    D[word.attrib["token"]] = MorphologyParser.parse(word.attrib["morphology"])
        return D

    def all_words_generator(self):
        """
        Generate words properties ,word by word
        """
        for chapter in self.corpus.findall(".//chapter"):
            for verse in chapter.findall("verse"):
                for word in verse.findall("word"):
                    res = word.attrib
                    res["sura_id"] = int(chapter.attrib["number"])
                    res["aya_id"] = int(verse.attrib["number"])
                    res["word_id"] = int(word.attrib["number"])
                    res["word"] = word.attrib["token"]
                    res["morphology"] = MorphologyParser.parse(word.attrib["morphology"])
                    yield res


if __name__ == "__main__":
    A = API(source="data/quranic-corpus-morpology.xml")
    # for item in A.all_words_generator():
    #     print "(sura,aya,word):({0},{1},{2})".format(item["sura_id"], item["aya_id"], item["word_id"])

    # for item in A.unique_words():
    #      print item

    # print MorphologyParser.parse("fa+ POS:INTG LEM:&lt;maA ROOT:qawol l:P+ ")
    # print A.corpus.findtext("@number=’114’")
