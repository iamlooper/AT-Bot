import threading

class PageCache:

    """ 
    A class that saves the page source code
    The key is (<url>, <url parameters>), and the value is the page source code
    Embedding the PageCache object into the CheckUpdate.request_url method
    You can check before requesting whether it has been requested (check two elements: url, url parameters)
    If not, continue to request, and after the request is successful, save the url, url parameters, and page source code to this object
    If so, take out the source code obtained from the previous request from this object, which can avoid repeated requests

    Why not use the lru_cache decorator?
    Because url parameters may be dictionaries,
    And dictionaries are not hashable, so lru_cache cannot be used.
    In PageCache, dictionary parameters will be properly processed.
    """

    def __init__(self):
        self.__page_cache = dict()
        self.threading_lock = threading.RLock()

    @staticmethod
    def __params_change(params):
        if params is None:
            return None
        if isinstance(params, dict):
            return frozenset(params.items())
        raise TypeError("'params' must be a dict or None")

    def read(self, url, params):
        params = self.__params_change(params)
        with self.threading_lock:
            return self.__page_cache.get((url, params))

    def save(self, url, params, page_source):
        params = self.__params_change(params)
        with self.threading_lock:
            self.__page_cache[(url, params)] = page_source

    def clear(self):
        with self.threading_lock:
            self.__page_cache.clear()