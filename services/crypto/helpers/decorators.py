from functools import wraps
import json
from flask import Flask, jsonify, request
import helpers.exceptions as e
import werkzeug


def need_args(*needed_args_list):
    def real_decorator(func):
        @wraps(func)
        def inner(*args, **kws):
            print("in needed args", flush=True)
            try:
                posted_json = request.get_json()
            except werkzeug.exceptions.BadRequest:
                raise e.JSONObjectExpected
            print(f"posted json: {posted_json}", flush=True)
            kwargs = {}
            for key in needed_args_list:
                try:
                    if key == 'addition':
                        kwargs[key] = posted_json[key]
                    else:
                        kwargs[key] = posted_json["addition"][key]
                except KeyError:
                    raise e.SomeOtherArgsRequired
            print(f"extracted: {kwargs}", flush=True)
            return func(**kwargs)
        return inner
    return real_decorator

def safe_run(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        print("in safe run", flush=True)
        try:
           return func(*args, **kwargs)

        except Exception as exc:
            print(exc, args, kwargs)
            return e.handle_exception(exc, None)

    return func_wrapper