# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

def token_is_parsed(needle, haystack):
    expected_ttype, expected_value, *rest = needle
    for item in haystack:
        actual_ttype, actual_value, *rest = item

        if actual_ttype == expected_ttype and actual_value == expected_value:
            return True

    return False

def walk_ast(root, callback):
    if not root:
        return

    callback(root)

    for child in root.children:
        walk_ast(child, callback)


def dfs(root, padding_left=0):
    if not root:
        return

    if padding_left == 0:
        print('\n')

    print(''.rjust(padding_left, ' ') + str(root))

    for child in root.children:
        dfs(child, padding_left + 5)

