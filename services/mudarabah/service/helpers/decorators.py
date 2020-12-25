import json
import werkzeug
from flask import Flask, jsonify, request
from functools import wraps

from helpers.exceptions import JSONObjectExpected, SomeOtherArgsRequired


def need_args(*needed_args_list):
    def real_decorator(func):
        @wraps(func)
        def inner(*args, **kws):
            try:
                posted_json = request.get_json()
            except werkzeug.exceptions.BadRequest:
                raise JSONObjectExpected
            kwargs = {}
            for key in needed_args_list:
                try:
                    if key == 'addition':
                        kwargs[key] = posted_json[key]
                    else:
                        kwargs[key] = posted_json["addition"][key]
                except KeyError:
                    raise SomeOtherArgsRequired
            return func(**kwargs)
        return inner
    return real_decorator