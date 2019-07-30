# coding=utf-8
from .css_selectors import find_selector, clean_selector, fragmented_selector_to_selector
from .css_selectors import simplify_fragmented_selector, get_tags
from .regex import get_regex
import re
from . import schemaorg
from fuzzywuzzy import fuzz
from uuid import uuid4
from abc import ABC, abstractmethod


class AbstractWrapper(ABC):
    def __init__(self):
        self.value = None
        self.selector = None
        self.regex = ""

    @abstractmethod
    def build(self, **kwargs):
        pass

    def simplify(self, value):
        """
        Apply regex to value

        :param value: the value we found with the selector
        :type value: str

        :return: the list of all values found with the selector
        :rtype: str
        """
        if not value:
            return None
        if not self.regex:
            return value.strip()

        match = "".join(re.findall(self.regex, value.strip().replace('\n', '\\n'))).strip()

        if not match:
            return value.strip()
        return match


class WrapperCss(AbstractWrapper):
    def __init__(self):
        super().__init__()
        self.fragmented_selector = None
        self.attr = None
        self.index = 0

    def build(self, soup, best_match, attr_best_match=None, value=''):
        """

        :param soup: the BeautifulSoup object
        :param best_match: the match if we have already a match
        :param attr_best_match: the attribute where to look
        :param value: the value we search for
        :type soup: BeautifulSoup
        :type best_match: BeautifulSoup
        :type attr_best_match: str
        :type value: str

        this method builds the selector for the value we search for or the match we already have
        """
        self.value = value
        self.attr = attr_best_match
        fragmented_selector = find_selector(child=best_match)
        fragmented_selector_cleaned = clean_selector(fragmented_selector, forbidden_keyword=value)
        self.fragmented_selector = simplify_fragmented_selector(soup=soup,
                                                                fragmented_selector=fragmented_selector_cleaned)
        self.selector = fragmented_selector_to_selector(self.fragmented_selector)
        values = self.__get_values_from_selector(soup=soup)

        # to calculate index
        if values:
            best_score = (0, 0)
            lenValue = len(value)
            for i, value_i in enumerate(values):
                if value_i and lenValue <= len(value_i):
                    score = fuzz.partial_ratio(value, value_i)
                    if best_score[0] < score:
                        best_score = (score, i)

            self.index = best_score[1]
            raw = values[self.index]
            self.regex = get_regex(formatted=self.value, raw=raw)

    def extract(self, soup, data_schemaorg):
        """
        :param soup: the soup object where to find the values
        :param data_schemaorg: the meta data of the page
        :type soup: BeautifulSoup
        :type data_schemaorg: dict/list
        
        
        :return: the list of values found with the selector and then formated with the regex
        :rtype: [str]/str
        """
        extracted = [self.simplify(value) for value in self.__get_values_from_selector(soup=soup) if value]

        if not extracted:
            return extracted
        else:
            if self.index < len(extracted):
                return extracted[self.index]
            else:
                return extracted[0]

    def __get_values_from_selector(self, soup):
        """

        :param soup: the soup object where to find the values
        :type soup: BeautifulSoup

        :return: the list of all values found with the selector
        :rtype: [str]
        """
        values = []
        if not self.selector:
            return values

        selections = soup.select(self.selector)
        for selection in selections:
            if self.attr == "getText()":
                values.append(selection.getText())
            else:
                values.append(selection.get(self.attr))

        return values


class WrapperMeta(AbstractWrapper):
    """
    Wrapper for schema.org data and selection
    """
    def build(self, data_schemaorg, selector, value=''):
        """

        :param data_schemaorg: the meta data extracted with extruct
        :param selector: selector
        :param value: the value we search for
        :type data_schemaorg: {str:str/list/dict}
        :type selector: [str/int]
        :type value: str

        this method builds the selector for the value we search for or the match we already have
        """
        self.value = value

        if data_schemaorg is None:
            raise ValueError("No metadata found")

        self.selector = selector
        raw = self.__get_values_from_selector(data_schemaorg)[0]
        regex = get_regex(formatted=self.value, raw=raw)

        self.regex = regex

    def extract(self, soup, data_schemaorg):
        return self.simplify(self.__get_values_from_selector(data_schemaorg=data_schemaorg)[0])

    def __get_values_from_selector(self, data_schemaorg):
        """

        :param data_schemaorg: the value we found with the selector
        :type data_schemaorg: {str:str/list/dict}

        :return: the list of all values found with the selector
        :rtype: [str]
        """
        if not self.selector:
            return []
        
        return [schemaorg.get_value(data_schemaorg, self.selector)]


class WrapperGroup(WrapperCss):  # Wrapper group does not support meta selectors
    def __init__(self, tags=[]):
        super().__init__()
        self.wrappers = []
        self.tags = tags
        self.id_ = str(uuid4())

    def add_wrapper(self, wrapper):
        """
        :param wrapper: the selector to add to the group
        :type wrapper: Wrapper
        """
        self.wrappers.append(wrapper)

    def extract(self, soup, data_schemaorg):
        """
        :return: the list of values found with the selector and then formated with the regex
        :rtype: [str]/str
        """
        return [self.simplify(value) for value in
                self.__get_values_from_selector(soup=soup, data_schemaorg=data_schemaorg) if value]

    def belongs_to_group(self, wrapper):
        """

        :param wrapper: the wrapper that could belong to the group
        :type wrapper: Wrapper

        :return: does the wrapper belongs to the group ?
        :rtype: bool
        """
        wrapper_tags = get_tags(wrapper.fragmented_selector)
        if len(wrapper_tags) != len(self.tags):
            return False

        for i in range(len(wrapper_tags)):
            if wrapper_tags[i] != self.tags[i]:
                return False
        return True

    def fill_common_parent(self, soup):
        """

        :param soup: A soup
        :type soup: BeautifulSoup

        creates a wrapper to the common parent found
        """
        if len(self.wrappers) > 1:
            common_parent = self.__find_common_parent(soup)
        else:
            wrap = self.wrappers[0]
            if soup and wrap.selector:
                common_parent = soup.select_one(wrap.selector)
            else:
                common_parent = None

        self.build(soup, best_match=common_parent, attr_best_match=self.wrappers[0].attr)
        self.regex = self.wrappers[0].regex

    def __get_values_from_selector(self, soup, data_schemaorg):
        """

        :param soup: the soup object where to find the values
        :param data_schemaorg: the value we found with the selector
        :type soup: BeautifulSoup
        :type data_schemaorg: {str:str/list/dict}

        :return: the list of all values found with the selector
        :rtype: [str]
        """
        values = []
        if not self.selector:
            return values
        
        selectors = [wrapper.selector for wrapper in self.wrappers]
        selections = soup.select(self.selector)
        children = []
        children.extend(selections)

        for selection in selections:
            for selector in selectors:
                children.extend(selection.select(selector))

        for child in children:
            value = child.get(self.attr)
            if value not in values:
                values.append(value)

        return values
    
    def __find_common_parent(self, soup):
        """

        :param soup: A soup
        :type soup: BeautifulSoup

        :return: the common parent found
        :rtype: BeautifulSoup
        """
        wrap = self.wrappers[0]
        if not wrap.selector:
            return None
        soup = soup.select_one(wrap.selector)
        while not self.__is_common_parent(soup):
            if not soup.parent:
                return None
            soup = soup.parent
        return soup

    def __is_common_parent(self, soup):
        """

        :param soup: A soup
        :type soup: BeautifulSoup

        :return: whether we can find all values pointed to by wrappers from the current soup object
        :rtype: bool
        """
        # for each wrapper check that we find its value in soup's children
        for wrap in self.wrappers:
            roots = soup.select(wrap.selector)
            val = ""

            children = roots
            for root in roots:
                children.extend(root.findChildren(recursive=True))

            for child in children:
                tmp = child.get(wrap.attr)
                if fuzz.partial_ratio(wrap.value, tmp) >= 98:
                    val = tmp
                    break
            if not val:
                return False
        return True


class Wrappers:
    def __init__(self, wrappers):
        self.wrappers = wrappers

    def build(self, **kwargs):
        raise Exception("build method unavailable for 'Wrappers' class")

    def extract(self, soup, data_schemaorg):
        """
        :return: the list of values found with the wrappers and then formated with the regex
        :rtype: [str]
        """
        results = []
        for wrapper in self.wrappers:
            results.extend(wrapper.extract(soup=soup, data_schemaorg=data_schemaorg))

        return results
