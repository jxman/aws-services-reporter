# Test file to demonstrate pre-commit hooks
# This file has intentionally bad formatting


import json
import os
import sys


def badly_formatted_function(x, y):
    """This function has bad formatting."""
    result = x + y
    return result


if __name__ == "__main__":
    print("Testing pre-commit hooks")
