""" 
Copyright 2015 Benjamin Alt 
benjaminalt@arcor.de
    
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>. 

"""

import multiprocessing as MP
from sys import exc_info
from time import clock

DEFAULT_TIMEOUT = 60

################################################################################

def timeout(limit=None):
    if limit is None:
        limit = DEFAULT_TIMEOUT
    if limit <= 0:
        raise ValueError()
    def wrapper(function):
        return _Timeout(function, limit)
    return wrapper

class TimeoutError(Exception): pass

################################################################################

def _target(queue, function, *args, **kwargs):
    try:
        queue.put((True, function(*args, **kwargs)))
    except:
        queue.put((False, exc_info()[1]))

class _Timeout:

    def __init__(self, function, limit):
        self.__limit = limit
        self.__function = function
        self.__timeout = clock()
        self.__process = MP.Process()
        self.__queue = MP.Queue()

    def __call__(self, *args, **kwargs):
        self.cancel()
        self.__queue = MP.Queue(1)
        args = (self.__queue, self.__function) + args
        self.__process = MP.Process(target=_target, args=args, kwargs=kwargs)
        self.__process.daemon = True
        self.__process.start()
        self.__timeout = self.__limit + clock()

    def cancel(self):
        if self.__process.is_alive():
            self.__process.terminate()

    @property
    def ready(self):
        if self.__queue.full():
            return True
        elif not self.__queue.empty():
            return True
        elif self.__timeout < clock():
            self.cancel()
        else:
            return False

    @property
    def value(self):
        if self.ready is True:
            flag, load = self.__queue.get()
            if flag:
                return load
            raise load
        raise TimeoutError()

    def __get_limit(self):
        return self.__limit

    def __set_limit(self, value):
        if value <= 0:
            raise ValueError()
        self.__limit = value

    limit = property(__get_limit, __set_limit)