import logging

def get_param_in_tree(dic, path, finalkey):
    logging.debug(f'{path}/{finalkey} = ?')
    value = _get_param_in_tree(dic, path, finalkey)
    logging.debug(f'{path}/{finalkey} -> {str(value)[0:50]}...')
    return value

def _get_param_in_tree(dic, path, finalkey):
    """ Read the key in the dic following the path of keys. If finalkey 
    is not found, fall back to the upper lever. Basic inheritance scheme. """
    if not path:
        value = dic[finalkey]
        return value
    try:
        return _get_param_in_tree(dic[path[0]], path[1:], finalkey)
    except KeyError:
       return _get_param_in_tree(dic, path[:-1], finalkey)

def get_param_in_tree_with_countfails(dic, path, finalkey, countfails=0):
    """ Read the key in the dic following the path of keys. If finalkey
    is not found, fall back to the upper lever. Basic inheritance scheme. """
    if not path:
        return dic[finalkey], countfails
    try:
       return get_param_in_tree_with_countfails(dic[path[0]], path[1:], finalkey, countfails)
    except KeyError:
       return get_param_in_tree_with_countfails(dic, path[:-1], finalkey, countfails+1)

def set_param_in_tree(dic, path, finalkey, value, countfails=0):
    """ Write the key in the dic following the path of keys """
    if not path: 
        dic[finalkey] = value
        return
    if not path[0] in dic: dic[path[0]] = {} # create sub-dict if needed
    return set_param_in_tree(dic[path[0]], path[1:], finalkey, value)

def instanciate_keywords(value, keywords):
    """ This function take a dict, list or string as input, it uses a 
    keyword dictionnary to instanciate the values of some keywords in the object.
    Note that if the input is a dict, the dict itself is modified.
    **Examples**

    >>> instanciate_keywords('{name}/static-string/{param}.txt', {'name':'foo', 'param':'bar'})
    'foo/static-string/bar.txt'
    """
    if isinstance(value, dict):
       for k in list(value.keys()):
           v = value[k]
           del value[k]
           newk = instanciate_keywords(k, keywords)
           value[newk] = instanciate_keywords(v, keywords)
    if isinstance(value, list):
       value = [instanciate_keywords(v, keywords) for v in value]
       return value
    if isinstance(value, str):
        value = value.format(**keywords)
        return value
    try: # ensure python2.7 compat ugly.
        if isinstance(value, unicode):
            value = value.format(**keywords)
            return value
    except NameError:
        pass # end-of-ugly
    return value

def instanciate_datetime(value, date):
    """ Similar to instanciate_keywords. This function take a dict, list
     or string as input, it uses a date to instanciate the value in the object. 
     Note that if the input is a dict, the dict itself is modified.
    Examples:

    >>> from datetime import datetime
    >>> instanciate_datetime('%Y/%d/%m/HDF_%Y_%d_%m', datetime(2017,5,12))
    '2017/12/05/HDF_2017_12_05'
    >>> instanciate_datetime({'brdf': 'BRDF_FILENAME_%Y_%d_%m', 'albedo': 'ALBEDO_FILENAME_%Y_%d_%m'}, datetime(2017,5,12))
    {'brdf': 'BRDF_FILENAME_2017_12_05', 'albedo': 'ALBEDO_FILENAME_2017_12_05'}

    """
    if isinstance(value, dict):
       for k in list(value.keys()):
           v = value[k]
           del value[k]
           newk = instanciate_datetime(k, date)
           value[newk] = instanciate_datetime(v, date)
    if isinstance(value, list):
       value = [instanciate_datetime(v, date) for v in value]
       return value
    if isinstance(value, str):
        value = date.strftime(value)
        return value
    try: # ensure python2.7 compat ugly.
        if isinstance(value, unicode):
            value = date.strftime(value)
            return value
    except NameError:
        pass # end-of-ugly
    return value

if __name__ == "__main__":
    # this doctest allows some automated testing of the funcions based 
    # on the comments (called docstring) in triple quotes below the 
    # function. See https://docs.python.org/2/library/doctest.html fro details.
    import doctest
    doctest.testmod()
