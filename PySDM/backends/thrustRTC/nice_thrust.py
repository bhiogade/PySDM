"""
Created at 18.05.2020

@author: Piotr Bartman
@author: Sylwester Arabas
"""

import ThrustRTC as trtc


def nice_thrust(*, wait=False, debug_print=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if debug_print:
                print(func.__name__)
            result = func(*args, **kwargs)
            if wait:
                trtc.Wait()
            return result
        return wrapper
    return decorator
