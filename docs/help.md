---
layout: page
title: User Manual
permalink: /user-manual/
---
## Requirements ##

`MitzaSQL` runs on Linux and requires Python 3.5. No tests were done for versions lower than 3.5 but there's a good change that it will run.  
Supported MySQL versions:
- 5.5
- 5.6
- 5.7
- 8

#### Dependencies

* urwid v2
* mysql-connector-python v8
* appdirs v1.4

## Instalation ##

User installation:

    pip3 install --user mitzasql

System wide installation:

    sudo pip3 install mitzasql

*On systems which have a default Python 3 installation replace `pip3` with `pip`.*

`MitzaSQL` creates by default the following files and folders in your home directory:
- $HOME/.config/mitzasql/sessions.ini
- $HOME/.cache/mitzasql/log/mitzasql.log

You can override the default location of the sessions file using the `--sessions_file` switch. See the [Command line options](#command-line-options) section

## Usage ##

    mitzasql

Run `mitzasql --help` to see all the available options.

## Keyboard shortcuts ##

The user interface supports the following methods for performing actions:

- keyboard shortcuts
- VIM-like keyboard shortcuts
- VIM-like commands
- action keys

**Keyboard shortcuts list**
<table>
    <thead>
        <tr>
            <td>Key(s)</td>
            <td width="50%">Action</td>
            <td>VIM emulation</td>
            <td>Context</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Arrow keys</td>
            <td colspan="2">Scroll / move</td>
            <td>all</td>
        </tr>
        <tr>
            <td>home / end</td>
            <td colspan="2">Scroll to top / bottom</td>
            <td>all</td>
        </tr>
        <tr>
            <td>page up / down</td>
            <td colspan="2">Scroll one page up/down</td>
            <td>all</td>
        </tr>
        <tr>
            <td>ctrl left / right</td>
            <td colspan="2">Go to first / last column</td>
            <td>tables</td>
        </tr>
        <tr>
            <td>j / k / h / l</td>
            <td>Scroll / move down / up / left / right</td>
            <td>yes</td>
            <td>all except text inputs</td>
        </tr>
        <tr>
            <td>ctrl u / d</td>
            <td>Scroll one page up / down</td>
            <td>yes</td>
            <td>all except text inputs</td>
        </tr>
        <tr>
            <td>gg</td>
            <td>Scroll to top</td>
            <td>yes</td>
            <td>tables, lists</td>
        </tr>
        <tr>
            <td>G</td>
            <td>Scroll to bottom</td>
            <td>yes</td>
            <td>tables, lists</td>
        </tr>
        <tr>
            <td>0</td>
            <td>Go to first column</td>
            <td>yes</td>
            <td>tables</td>
        </tr>
        <tr>
            <td>$</td>
            <td>Go to last column</td>
            <td>yes</td>
            <td>tables</td>
        </tr>
        <tr>
            <td>enter</td>
            <td colspan="2">Select / change context</td>
            <td>all</td>
        </tr>
        <tr>
            <td>esc</td>
            <td colspan="2">Exit context / go back</td>
            <td>all</td>
        </tr>
        <tr>
            <td>:</td>
            <td>Enter command mode</td>
            <td>yes</td>
            <td>tables</td>
        </tr>
        <tr>
            <td>q:</td>
            <td>Enter command mode and show last command</td>
            <td>yes</td>
            <td>tables</td>
        </tr>
        <tr>
            <td>ctrl p</td>
            <td>Go back in the command history</td>
            <td>yes</td>
            <td>command mode</td>
        </tr>
        <tr>
            <td>ctrl n</td>
            <td>Go forward in the command history</td>
            <td>yes</td>
            <td>command mode</td>
        </tr>
        <tr>
            <td>n / p</td>
            <td>Go to next or previous search result</td>
            <td>yes</td>
            <td>search mode</td>
        </tr>
        <tr>
            <td>/</td>
            <td>Enter search mode</td>
            <td>yes</td>
            <td>server view, database view</td>
        </tr>
        <tr>
            <td>tab</td>
            <td>Autocomplete command / argument</td>
            <td>yes</td>
            <td>all contexts which support commands</td>
        </tr>
        <tr>
            <td>ctrl o</td>
            <td colspan="2">Open the "change table" popup</td>
            <td>database table</td>
        </tr>
    </tbody>
</table>

Actions keys are equivalent to regular buttons found in a conventional user interface. To perform an action press a specific key highlighted with a different color than the rest of the text. In the example below:

- to quit press `q`
- to show the help press `F1`
- to refresh the current table press `F5`

![Action buttons]({{ "/assets/screenshots/action-buttons.jpg" | relative_url }} "Action buttons")

Some of the VIM-style keys support VIM motions:

- `10l` will scroll 10 columns to the right
- `25j` will scroll down 25 rows

**VIM-like commands**  
Commands support autocompletion for the command name and the first argument. For example, typing `:res` and pressing `tab` will autocomplete the `:resize` command. Pressing `tab` again will autocomplete the column name.  
To exit command mode press `esc`.

<table>
    <thead>
        <tr>
            <td>Command</td>
            <td width="40%">Action</td>
            <td>Context</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>:q / :quit</td>
            <td>Exit program</td>
            <td>all except server view</td>
        </tr>
        <tr>
            <td>/[keyword]</td>
            <td>Search database or table. Press `n` or `p` to go to the next or previous search result</td>
            <td>server view, database view</td>
        </tr>
        <tr>
            <td>:resize [column name] [increment]</td>
            <td>
                Resize [column name] by [increment]. [increment] can be a positive or a negative value:<br /><br />

                <code>
                    :resize date 30
                </code>
                <br />
                <code>
                    :resize date -10
                </code>
            </td>
            <td>tables</td>
        </tr>
        <tr>
            <td>:sort [column name] [asc|desc]</td>
            <td>
                Sort [column name] asceding or descending.
            </td>
            <td>all except server view</td>
        </tr>
        </tbody>
    </table>

The following commands are available only when browsing a MySQL table or view and they act as shortcuts to writing full SQL queries for filtering data. For example, using the command `:eq id 100` is equivalent to writing `SELECT * FROM [current table] WHERE id = 100`. As such **it is important to appropriately quote the value** for the filter in order to avoid SQL syntax errors, using the same `eq` command on a string column will result in an SQL error if the value is not quoted (`'value'`).
<table>
    <thead>
        <tr>
            <td>Command</td>
            <td width="50%">Action</td>
            <td>SQL WHERE clause</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>:eq [column] [value]</td>
            <td>
                Find row where [column] equals [value]. Ex:<br /><br />
                <code>
                :eq id 100<br />
                </code>
                <br />

                Will find the row with id 100. <strong>If the column is of type <em>string</em> make sure you quote the value</strong>
            </td>
            <td>column = value</td>
        </tr>
        <tr>
            <td>:neq [column] [value]</td>
            <td>
                Find row where [column] doesn't equal [value]
            </td>
            <td>column != value</td>
        </tr>
        <tr>
            <td>:lt [column] [value]</td>
            <td>
                Find the rows where [column] is lower than [value]
            </td>
            <td>column < value</td>
        </tr>
        <tr>
            <td>:lte [column] [value]</td>
            <td>
                Find the rows where [column] is lower or equal than [value]
            </td>
            <td>column <= value</td>
        </tr>
        <tr>
            <td>:gt [column] [value]</td>
            <td>
                Find the rows where [column] is greater than [value]
            </td>
            <td>column > value</td>
        </tr>
        <tr>
            <td>:gte [column] [value]</td>
            <td>
                Find the rows where [column] is greater or equal than [value]
            </td>
            <td>column >= value</td>
        </tr>
        <tr>
            <td>:in [column] [value1, value2, value3]</td>
            <td>
                Find the rows where [column] is in set
            </td>
            <td>column in (value1, value2, value3)</td>
        </tr>
        <tr>
            <td>:nin [column] [value1, value2, value3]</td>
            <td>
                Find the rows where [column] is not in set
            </td>
            <td>column not in (value1, value2, value3)</td>
        </tr>
        <tr>
            <td>:null [column]</td>
            <td>
                Find the rows where [column] is null
            </td>
            <td>column is null</td>
        </tr>
        <tr>
            <td>:nnull [column]</td>
            <td>
                Find the rows where [column] is not null
            </td>
            <td>column is not null</td>
        </tr>
        <tr>
            <td>:empty [column]</td>
            <td>
                Find the rows where [column] is empty
            </td>
            <td>column = ''</td>
        </tr>
        <tr>
            <td>:nempty [column]</td>
            <td>
                Find the rows where [column] is not empty
            </td>
            <td>column != ''</td>
        </tr>
        <tr>
            <td>:like [column] [value]</td>
            <td>
                Find the rows where [column] contains [value]. <strong>This command quotes the value automatically. Manually quoting the value will most likely yield unwanted results</strong>. You can use %value% to search for substrings.
            </td>
            <td>column LIKE 'value'</td>
        </tr>
        <tr>
            <td>:nlike [column] [value]</td>
            <td>
                Find the rows where [column] doesn't contains [value]
            </td>
            <td>column NOT LIKE 'value'</td>
        </tr>
        <tr>
            <td>:clearfilters</td>
            <td>
                Clear the previously applied filter command.
            </td>
            <td>&nbsp;</td>
        </tr>
    </tbody>
</table>

## Query editor
Pressing `F2` will open the SQL query editor.

<table>
    <thead>
        <tr>
            <td>Key(s)</td>
            <td>Action</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>f9</td>
            <td>Execute query</td>
        </tr>
        <tr>
            <td>ctrl f9</td>
            <td>Clear editor</td>
        </tr>
        <tr>
            <td>ctrl p / n</td>
            <td>Go back / forward in the query history</td>
        </tr>
        <tr>
            <td>esc</td>
            <td>Close the editor</td>
        </tr>
    </tbody>
</table>

## Text inputs
All the text inputs support basic Emacs keyboard shortcuts.

## Macros
The main use case for the macro functionality is testing the user interface but it can be used to script the interface. The functionality is basic and might be buggy. To create a macro use the [macrofile.txt](https://github.com/vladbalmos/mitzasql/blob/master/macrofile.txt) as template and run the program with the `--macro` option:

    mitzasql --macro /path/to/your-macrofile.txt

To see more macro examples go over the [UI tests](https://github.com/vladbalmos/mitzasql/tree/master/tests/macros).

