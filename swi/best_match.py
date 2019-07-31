# coding=utf-8
from fuzzywuzzy import fuzz
from . import schemaorg


class Match:
    def __init__(self, is_css=None, score=0, soup=None, selector=None, attr=None, length_value=0):
        self.is_css = is_css
        self.score = score
        self.soup = soup
        self.meta_selector = selector
        self.attr = attr
        self.length_value = length_value


def find_best_matches(soup, data_schemaorg, value):
    """

    :param soup: a BeautifulSoup object
    :param data_schemaorg: the meta data of the page
    :param value: an element to find in the soup
    :type soup: BeautifulSoup
    :type data_schemaorg: nested dict/list
    :type value: str


    :return: a list containing all the probable matches
    :rtype: [Match]
    """
    matches = []
    meta_matches = __get_meta_matches(value, data_schemaorg)
    for child in soup.findChildren(recursive=True):
        matches.extend(__get_matches(child, value))

    better_best_matches = []
    matches.extend(meta_matches)
    if matches:
        best_matches = __get_best_items(matches)

        for best_match in best_matches:
            best_match.score -= best_match.length_value

        better_best_matches = __get_best_items(best_matches)

    return better_best_matches


def __get_matches(soup, value):
    """

    :param soup: a BeautifulSoup object
    :param value: an element to find in the soup
    :type soup: BeautifulSoup
    :type value: str


    :return: the probable matches based on similarity of value and what we can find in soup
    :rtype: [Match]
    """
    lenValue = len(value)
    matches = []
    text = soup.getText()
    lenText = len(text)
    if lenText >= lenValue:
        match = Match(is_css=True, score=fuzz.partial_ratio(value, text), soup=soup, attr="getText()",
                      length_value=lenText)
        matches.append(match)

    for attr in soup.attrs.keys():
        text = soup.get(attr)
        if type(text) is list:
            continue
        lenText = len(text)
        if lenText >= lenValue and soup.name != "meta":  # meta tags are handled by extruct
            match = Match(is_css=True, score=fuzz.partial_ratio(value, text), soup=soup, attr=attr,
                          length_value=lenText)
            matches.append(match)

    return matches


def __get_meta_matches(value, data_schemaorg):
    """

    :param value: the string we want to find
    :param data_schemaorg: the dictionary where we search the value
    :type value: str
    :type data_schemaorg: {str:str/list/dict}

    :return a list of matches
    :rtype: [match]
    """
    if not value:
        raise ValueError("Value is NULL/empty")
    lenValue = len(value)
    matches = []

    for path in schemaorg.get_pathes(data_schemaorg):
        text = schemaorg.get_value(data_schemaorg, path)
        lenText = len(text)
        if lenText >= lenValue:
            match = Match(is_css=False, score=fuzz.ratio(value, text), selector=path, length_value=lenText)
            matches.append(match)

    return matches


def __get_best_items(matches):
    """
    Get all items with best fuzzy score

    :param matches: list of matches
    :type matches: [Match]
    :return:
    """
    best_matches = []
    matches.sort(key=lambda match: match.score, reverse=True)
    best_score = matches[0].score
    i = 0
    nbMatches = len(matches)
    while i < nbMatches and matches[i].score == best_score:
        best_matches.append(matches[i])
        i += 1
    return best_matches
