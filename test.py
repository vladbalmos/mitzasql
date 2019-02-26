import urwid
import sys
from faker import Faker

from mitzasql.ui import theme
from mitzasql.ui.widgets.action_bar import ActionBar
from mitzasql.ui.widgets.table import Table
from mitzasql.ui.widgets.mysql_table import MysqlTable
from mitzasql.db.connection import Connection
from mitzasql.db.model import (DatabasesModel, DBTablesModel, TableModel, Model)

def make_data(rows=10, cols=14):
    fake = Faker()
    columns = {}
    for i in range(0, cols):
        name = fake.color_name() + ' ' + str(i)
        columns[name] = {
                'type': 'string',
                'max_size': sys.maxsize
                }

    data = []
    for i in range(0, rows):
        row = []
        for j in range(0, cols):
            row.append(fake.color_name() + ' ' + str(i) + u':' + str(j))
        data.append(row)

    return (data, columns)


if __name__ == '__main__':
    # data, columns = make_data(50, 50)
    # model = Model(data, columns)
    con, err = Connection.factory({
        'host': 'tcp://localhost',
        'port': '3306',
        'username': 'root',
        'password': '',
        'database': 'papucei_app'
        })

    # model = DBTablesModel(con)
    # model = DatabasesModel(con)
    model = TableModel(con, 'orders')

    header = urwid.Text('Not connected')
    footer = urwid.AttrMap(ActionBar({
        ('F1', 'F1 Help')
        }), 'action_bar')

    body = MysqlTable(model)

    frame = urwid.Frame(body, header, footer)
    top_widget = frame
    loop = urwid.MainLoop(top_widget, palette=theme.get_palette(),
            handle_mouse=False)
    loop.run()
