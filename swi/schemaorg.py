# coding=utf-8
import warnings


def get_value(nested_dict, path):
    """

    :param nested_dict: a dictionary containing lists and/or other dictionaries
    :param path: the path where the value is suposedly located
    :type nested_dict: {str:str/list/dict}
    :type path: [str, int]

    :return the found value inside the nested dictionary
    :rtype: str
    """
    for item in path:
        if not nested_dict or (type(nested_dict) is list and (type(item) is not int or len(nested_dict) <= item)) or (
                type(nested_dict) is dict and item not in nested_dict.keys()):
            warnings.warn("Cannot find value in schema.org, nested_dict is different")
            return None
        nested_dict = nested_dict[item]
    return str(nested_dict)


def get_pathes(nested_dict):
    """

    :param nested_dict: a dictionary containing lists and/or other dictionaries
    :type nested_dict: {str:str/list/dict}

    :return the list of the pathes found for all values in nested_dict
        an int means an index in a list and an str means a key in a dictionary
    :rtype: [[str, int]]
    """
    pathes = []
    __reccursive_get_pathes(nested_dict, "", pathes)

    results = []
    for path in pathes:
        path = path.split(',')[1:]
        for index, item in enumerate(path):
            if "index:" in item:
                item = item.replace("index:", "")
                path[index] = int(item)
        results.append(path)
    return results


def __reccursive_get_pathes(nested_dict, prevpath, pathes):
    """

    :param nested_dict: the dictionary where we want to find the values
    :param prevpath: the accumulator of the path
    :param pathes: the list of all pathes leading to all values
    :type nested_dict: {str:value/dict/list}
    :type prevpath: str
    :type pathes: [str]
    """
    if type(nested_dict) == list:
        for index, item in enumerate(nested_dict):
            path = "{},index:{}".format(prevpath, index)
            __reccursive_get_pathes(item, path, pathes)

    elif type(nested_dict) == dict:
        for key, item in nested_dict.items():
            path = "{},{}".format(prevpath, key)
            __reccursive_get_pathes(item, path, pathes)

    else:
        pathes.append(prevpath)
