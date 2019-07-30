# coding=utf-8
import Levenshtein
import re


def get_regex(formatted, raw):
    """

    :param formatted: the value we want to find
    :param raw: the value we found with the selector
    :type formatted: str
    :type raw: str

    :return: a regular expression hopefully matching the value we need to find
    :rtype: str
    """
    if not raw:
        return None

    raw = raw.strip()
    rawlen = len(raw)
    formattedlen = len(formatted)
    if formattedlen > 50 and rawlen > 5*formattedlen or not __is_in_order(formatted, raw):
        return None
    start_offset, end_offset, to_remove_list = __intersect(formatted, raw)

    if to_remove_list:
        remove = "".join([re.escape(c) for c in to_remove_list])
        regex = r"(?<=.{{{}}})([^{}]+)(?=.{{{}}})".format(start_offset, remove, end_offset)
    else:
        regex = r"(?<=.{{{}}})(.+)(?=.{{{}}})".format(start_offset, end_offset)
    return regex


def __intersect(formatted, raw):
    """

    :param raw: the string to format
    :param formatted: the string we want to find
    :type raw: str
    :type formatted: str

    :return the boundaries of the interesting part and the characters to remove from the string
    :rtype: (int, int, list)
    """
    rawLen = len(raw)
    start_index, end_index = __get_indexes(formatted, raw)
    to_remove_list = []

    sel = raw[start_index:end_index]
    for c in sel:
        if c not in formatted:
            to_remove_list.append(c)
    to_remove_list = list(set(to_remove_list))

    end_offset = rawLen - end_index
    return start_index, end_offset, to_remove_list


def __get_indexes(formatted, raw):
    """

    :param formatted: the value we want to find
    :param raw: the value we found with the selector
    :type formatted: str
    :type raw: str

    :return: the best indexes corresponding to the boundaries of the slice of what we are looking for
    :rtype: (int, int)
    """
    forLen = len(formatted)
    rawLen = len(raw)
    shorterDist = float("inf")
    bestStart = 0
    bestEnd = rawLen
    for i in range(rawLen):
        for j in range(i, rawLen + 1):
            if forLen <= j - i + 1:
                dist = Levenshtein.distance(formatted, raw[i:j])
                if dist < shorterDist and __is_in_order(formatted, raw[i:j]):
                    shorterDist = dist
                    bestStart = i
                    bestEnd = j
    return bestStart, bestEnd


def __is_in_order(formatted, sel):
    """

    :param formatted: the value we want to find
    :param sel: the value we found with the selector
    :type formatted: str
    :type sel: str

    :return: can we find each character of formated in sel and in the same order ?
    :rtype: bool
    """
    i = 0
    for c in formatted:
        i = sel.find(c, i)
        if i == -1:
            return False
        i += 1
    return True
