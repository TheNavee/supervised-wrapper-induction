# coding=utf-8
from bs4 import BeautifulSoup
from .best_match import find_best_matches
from .wrapper import WrapperCss, WrapperMeta, Wrappers, WrapperGroup
import extruct
from uuid import uuid4
from .css_selectors import get_tags


class PageExtractor:
    def __init__(self, page_content, train_set, id_=None):
        if not id_:
            id_ = str(uuid4())
        self.id_ = id_

        self.soup = BeautifulSoup(page_content, "lxml")
        self.data_schemaorg = extruct.extract(page_content)
        self.train_set = train_set
        self.wrappers_dict = dict()
        self.train()

    def train(self):
        """

        :return: a dictionary with the trained wrappers for the page
        :rtype: {str:Wrapper}
        """

        for label, value in self.train_set.items():
            if not (value and value[0]):  # check if not null and not empty list or string
                raise ValueError("Values in train set should not be null or empty")

            if type(value) is list and len(value) > 1:  # group everything to get a final Wrapper (herited class Wrappers)
                wrappers = self.__get_wrappers_from_values(values=value)
                groups = []
                for wrapper in wrappers:
                    has_group = False
                    for wrapper_group in groups:
                        if wrapper_group.belongs_to_group(wrapper):
                            wrapper_group.add_wrapper(wrapper)
                            has_group = True
                            break
                    if not has_group:
                        new_wrapper_group = WrapperGroup(get_tags(wrapper.fragmented_selector))
                        new_wrapper_group.add_wrapper(wrapper)
                        groups.append(new_wrapper_group)

                wrapper = Wrappers([])
                for group in groups:
                    group.fill_common_parent(self.soup)
                    wrapper.wrappers.append(group)
                wrappers = [wrapper]

            else:
                if type(value) is list:  # and len(value) == 1 implicit with previous if
                    value = value[0]

                wrappers = self.__get_wrappers_from_value(value=value)

            self.wrappers_dict[label] = wrappers

        return self.wrappers_dict
    
    def __get_wrappers_from_value(self, value):
        """

        :param value: value to be find in the soup
        :type value: str


        :return: a list containing one selector for each value
        :rtype: [WrapperCss/WrapperMeta]
        """
        wrappers = []
        matches = find_best_matches(self.soup, self.data_schemaorg, value)
        for index, match in enumerate(matches):
            #  match is a path in the schema.org data
            if not match.is_css:
                wrapper = WrapperMeta()
                selector = match.meta_selector
                wrapper.build(data_schemaorg=self.data_schemaorg, value=value, selector=selector)

            #  match is a css selector associated with its attribute
            else:
                wrapper = WrapperCss()
                wrapper.build(soup=self.soup, value=value, best_match=match.soup, attr_best_match=match.attr)

            wrappers.append(wrapper)

        return wrappers
    
    def __get_wrappers_from_values(self, values):
        """

        :param values: a list containing values to find in the soup
        :type values: [str]


        :return: a list containing one selector for each value
        :rtype: [Wrapper]
        """
        wrappers = []
        for value in values:
            match = find_best_matches(self.soup, self.data_schemaorg, value)[0]

            #  match is a css selector associated with its attribute
            if match.is_css:
                wrapper = WrapperCss()
                wrapper.build(soup=self.soup, value=value, best_match=match.soup, attr_best_match=match.attr)
                wrappers.append(wrapper)

        return wrappers

    def __str__(self):
        res = "ID: {}".format(self.id_)
        res += "train_set: {}".format(self.train_set)
        res += "wrappers_dict: {}".format(self.wrappers_dict)
        return res
