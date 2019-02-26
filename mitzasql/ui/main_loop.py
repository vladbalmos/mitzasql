import os

'''Some widgets need to access the main loop in order to refresh the screen.
In some cases importing mitzasql.ui in widgets causes a circular dependency
(pytest issue) so we store a reference to the loop in this module and require
it in the widgets modules
'''
mutable = {
        'loop': None
        }

def refresh():
    if os.getenv('TEST_MODE') == '1':
        return
    mutable['loop'].draw_screen()
