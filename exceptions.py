#!/usr/bin/python3

class InvalidStartEndDates(Exception):
    " Raised when a negative value shouldn't be used"
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class InvalidMovingAvgs(Exception):
    " Raised when there is InvalidInpt"
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)


class InvalidDays(Exception):
    " Raised when there is an invalid number of days chosen"
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class InvalidIntervals(Exception):
    " Raised when there is an invalid number of days chosen"
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class InvalidThresholds(Exception):
    " Raised when there is InvalidInpt"
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)