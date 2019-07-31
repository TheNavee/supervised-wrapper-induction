# coding=utf-8
from .page_extractor import PageExtractor
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import extruct
import pickle
from .wrapper import WrapperCss, WrapperMeta, WrapperGroup, Wrappers


class SupervisedWrapperExtractor:
    def __init__(self):
        self.extracted_pages = []
        self.best_wrappers = dict()
        self.retrain_best_wrappers = False

    def add_train_page(self, content, train_set, page_id=None):
        """

        :param content: the page content
        :param train_set: labels associated with the values we want to find on the page
        :param page_id: url of the page
        :type content: str
        :type train_set: {str:[str]}
        :type page_id: str
        """
        if not content:
            raise ValueError("Content should not be empty")

        page_extractor = PageExtractor(page_content=content, id_=page_id, train_set=train_set)
        self.extracted_pages.append(page_extractor)
        self.retrain_best_wrappers = True

    def predict(self, page):
        """

        :param page: the page content
        :type page: str

        :return: the extracted data from the page
        :rtype: {str:[str]/str}
        """
        if not page:
            raise ValueError("Given page is NULL/empty")

        if self.retrain_best_wrappers:
            self.__fill_best_wrappers()
            self.retrain_best_wrappers = False

        soup = BeautifulSoup(page, "lxml")
        data_schemaorg = extruct.extract(page)
        results = {}
        for label, wrapper in self.best_wrappers.items():
            results[label] = wrapper.extract(soup, data_schemaorg)

        return results

    def __fill_best_wrappers(self):
        """
        Gets the best wrappers from all trained pages and put them
        in self.best_wrappers
        """
        self.best_wrappers = self.__get_best_wrappers()
        self.retrain_best_wrappers = False

    def __get_best_wrappers(self):
        """
        :return: the best wrappers associated with labels
        :rtype: {str:Wrapper}

        Returns a dictionary containing the wrappers that worked the
        best compared to each page and train_set.
        For the images we take all the wrappers, not only the bests.
        """
        best_wrappers = dict()
        for page in self.extracted_pages:
            for label, wrappers in page.wrappers_dict.items():
                if label not in best_wrappers.keys():
                    best_wrappers[label] = [0, wrappers[0]]

                for wrapper in wrappers:
                    efficiency = 0
                    for page2 in self.extracted_pages:
                        train_set2 = page2.train_set

                        if not isinstance(train_set2[label], list):
                            expected_values = [train_set2[label]]
                        else:
                            expected_values = train_set2[label]

                        predicted_values = wrapper.extract(page2.soup, page2.data_schemaorg)
                        if type(predicted_values) is not list:
                            predicted_values = [predicted_values]
                        for expected_value in expected_values:
                            for predicted_value in predicted_values:
                                if fuzz.partial_ratio(expected_value, predicted_value) == 100:
                                    efficiency += 1
                                    break
                                else:
                                    efficiency -= 0.5

                    if efficiency > best_wrappers[label][0]:
                        best_wrappers[label][0] = efficiency
                        best_wrappers[label][1] = wrapper

        return {label: wrapper[1] for label, wrapper in best_wrappers.items()}

    def fill_best_wrappers_from_dictionary(self, dictionary):
        """

        :param dictionary: dictionary containing wrappers associated to labels
        :type dictionary: dict

        fills best wrappers with the ones from dictionary
        the if there is Wrappers (the class) they must be inside another list (see 'images' below)
        example input: {"price":[".price", "value", ".*", 0], "images":[[[".lazyImg"], "src", ".*, 0]]}
        """
        for label, value in dictionary.items():
            isGroup = False
            if len(value) < 2 or type(value[1]) is not str:  # value[1] is always the regex
                isGroup = True
            if not isGroup:
                if len(value) == 4:  # regular css_selector
                    if isGroup:
                        wrapper = WrapperGroup()
                    else:
                        wrapper = WrapperCss()
                    wrapper.selector, wrapper.attr, wrapper.regex, wrapper.index = value
                else:  # schema.org
                    wrapper = WrapperMeta()
                    wrapper.selector, wrapper.regex, _ = value

                self.best_wrappers[label] = wrapper
            else:
                wrappers = []
                for wrapper_attributes in value:
                    wrapper = WrapperGroup()
                    wrapper.selector, wrapper.attr, wrapper.regex, wrapper.index = wrapper_attributes
                    wrappers.append(wrapper)
                self.best_wrappers[label] = Wrappers(wrappers)

    # load best_wrappers
    def load(self, path):
        """

        :param path: the path of the wrappers to load
        :type path: str
        """
        f = open(path, 'rb')
        self.best_wrappers = pickle.load(f)

    # save best_wrappers
    def save(self, path):
        """

        :param path: the file where to save the best wrappers
        :type path: str
        """
        f = open(path, 'w')
        pickle.dump(self.best_wrappers, f)

    def __str__(self):
        res = "Number of trained pages: {}\n".format(len(self.extracted_pages))
        for i in range(len(self.extracted_pages)):
            res += "############### PAGE NUMBER {} ###############\n".format(i)
            res += str(self.extracted_pages[i]) + '\n'
        return res
