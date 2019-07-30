# coding=utf-8
from soupsieve import escape


def find_selector(child):
    """

    :param child: a BeautifulSoup object
    :type child: BeautifulSoup


    :return: the selector list made of tags and attributes that child has
    :rtype: [[str]]
    """
    if not child:
        return []

    child_attrs = child.attrs
    selector = [escape(child.name)]
    if "id" in child_attrs.keys():
        id_ = child_attrs["id"]
        if id_:
            selector.append('[id="{}"]'.format(escape(id_)))  # we do note use # because there is a bug with soupsieve: if the id starts with a number it wont work with a #
    if "class" in child_attrs.keys():
        class_ = child_attrs["class"]
        if class_:
            selector.extend([".{}".format(escape(cls)) for cls in class_])

    for attr in child_attrs.keys():
        if attr and attr != "class" and attr != "id":
            selector.append("[{}]".format(escape(attr)))

    if not child.parent or child.parent.name == "[document]":
        return [selector]

    sel = find_selector(child.parent)
    sel.append(selector)

    return sel


def clean_selector(fragmented_selector, forbidden_keyword):
    """

    :param fragmented_selector: a fragmented selector
    :param fragmented_selector: [[str]]
    :type forbidden_keyword: list of keywords that would make the selector too precise
    :type forbidden_keyword: [str]


    :return: the fragmented selector with returns removed so BeautifulSoup is happy
    :rtype: [[str]]
    """
    new_frag = []
    for tag in fragmented_selector:
        new_tag = []
        for attribute in tag:
            if '\r' not in attribute and '\n' not in attribute and \
                    (not forbidden_keyword or forbidden_keyword not in attribute):
                new_tag.append(attribute)
        new_frag.append(new_tag)
    if new_frag:
        return new_frag
    else:
        return fragmented_selector


def get_tags(fragmented_selector):
    """

    :param fragmented_selector: a fragmented selector
    :type fragmented_selector: [[str]]

    :return: the selector with only the tag names remaining
    :rtype: [str]
    """
    tags = []
    for tag in fragmented_selector:
        tags.append(tag[0])

    return tags


def simplify_fragmented_selector(soup, fragmented_selector):
    """

    :param soup: a BeautifulSoup object
    :param fragmented_selector: a list of tags
    :type soup: BeautifulSoup
    :type fragmented_selector: [[str]]

    :return: the selector simplified
    :rtype: [[str]]
    
    removes the useless tags from a selector list
    a useless tag is a tag that you can remove from a selector
    and this selector yields the same result that with this tag
    """
    selector = fragmented_selector_to_selector(fragmented_selector)
    if not selector:
        return []
    result = soup.select(selector)
    fragmented_selector = __simplify_fragmented_selector_attributes(soup, fragmented_selector, result)

    return fragmented_selector


def fragmented_selector_to_selector(fragmented_selector):
    """

    :param fragmented_selector: a fragmented selector
    :type fragmented_selector: [[str]]


    :return: the selector defragmented
    :rtype: str
    """
    return " ".join(["".join(tag) for tag in fragmented_selector]).strip()


def __simplify_fragmented_selector_attributes(soup, fragmented_selector, result):
    """
    Removes the useless attributes
    a useless attribute is an attribute that you can remove from a selector
    and this selector yields the same result that with this tag

    :param soup: a BeautifulSoup object
    :param fragmented_selector: a list of tags
    :param result: the wanted result after a soup.select(selector) where selector is the joined selector_list
    :type soup: BeautifulSoup
    :type fragmented_selector: [[str]]
    :type result: [Soup]

    :return: the selector with useless attributes removed
    :rtype: [[str]]
    """

    i = 0
    while i < len(fragmented_selector):
        tag = fragmented_selector[i]
        j = 0
        while j < len(tag):
            prev = tag.pop(j)
            selector = fragmented_selector_to_selector(fragmented_selector)
            if not selector or not __are_results_equals(soup.select(selector), result):
                tag.insert(j, prev)
                j += 1
        if not tag:
            fragmented_selector.pop(i)
        else:
            i += 1
    return fragmented_selector


def __are_results_equals(list1, list2):
    """

    :param list1: a list
    :param list2: another list
    :type list1: [[str]]
    :type list2: [[str]]


    :return: True if the two lists have at least nb_similar first values in common
    :rtype: bool
    """

    if len(list1) != len(list2):
        return False

    for i in range(len(list1)):
        if list1[i] != list2[i]:
            return False

    return True
