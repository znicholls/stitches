# Define helper functions used through out the package.
import os
import numpy as np
import pkg_resources
import pandas as pd



def combine_df(df1, df2):
    """ Join the data frames together.

    :param df1:   pandas data frame 1.
    :param df2:   pandas data frame 2.

    :return:    a single pandas data frame.
    """
    incommon = df1.columns.intersection(df2.columns)
    if len(incommon) > 0:
        raise TypeError(f"a: df1 and df2 must have unique column names")

    # Combine the two data frames with one another.
    df1["j"] = 1
    df2["j"] = 1
    out = df1.merge(df2)
    out = out.drop(columns="j")

    return out


def list_files(d):
    """ Return the absolute path for all of the files in a single directory with the exception of
    .DS_Store files.


    :param d:   str name of a directory.

    :return:    a list of the files
    """
    files = os.listdir(d)
    ofiles = []
    for i in range(0, len(files)):
        f = files[i]
        if not (".DS_Store" in f):
            ofiles.append(d + '/' + f)
    return ofiles


def selstr(a, start, stop):
    """ Select elements of a string from an array.

    :param a:   array containing a string.
    :param start: int referring to the first character index to select.
    :param stop: int referring to the last character index to select.

    :return:    array of strings
    """
    if type(a) not in [str]:
        raise TypeError(f"a: must be a single string")

    out = []
    for i in range(start, stop):
        out.append(a[i])
    out = "".join(out)
    return out


def check_columns(data, names):
    """ Check to see if a data frame has all of the required columns.

    :param data:   pd data
    :param names: set of the required names

    :return:    an error message if there is a column is missing
    """

    col_names = set(data.columns)
    if not(type(names) == set):
        raise TypeError(f'names must be a set.')

    if not (names.issubset(col_names)):
        raise TypeError(f'Missing columns from "{data}".')


def nrow(df):
    """ Return the number of rows

    :param df:   pd data

    :return:    an integer value that corresponds the number of rows in the data frame.
    """

    return df.shape[0]


def remove_obs_from_match(md, rm):
    """ Return an updated matched data frame. The idea being that this function could be
    useful to prevent envelope collapse between generated and target ensembles 

    :param md:   pd data
    :param rm:   pd data

    :return:    data frame
    """
    rm = rm[['target_year', 'target_start_yr', 'target_end_yr', 'archive_experiment',
             'archive_variable', 'archive_model', 'archive_ensemble',
             'archive_start_yr', 'archive_end_yr']].copy()
    rm["remove"] = True
    mergedTable = md.merge(rm, how="left")
    key = mergedTable["remove"].isnull()
    out = mergedTable.loc[key][['target_variable', 'target_experiment', 'target_ensemble',
                                'target_model', 'target_start_yr', 'target_end_yr', 'target_year',
                                'target_fx', 'target_dx', 'archive_experiment', 'archive_variable',
                                'archive_model', 'archive_ensemble', 'archive_start_yr',
                                'archive_end_yr', 'archive_year', 'archive_fx', 'archive_dx', 'dist_dx',
                                'dist_fx', 'dist_l2']]
    return out


def anti_join(x, y, bycols):
    """ Return a pd.DataFrame of the rows in x that do not appear in Table y.
    Maintains only the columns of x with their names (but maybe a different
    order?)
    Adapted from https://towardsdatascience.com/masteriadsf-246b4c16daaf#74c6

        :param x:   pd.DataFrame object
        :param y:   pd.DataFrame object
        :param bycols:   list-like; columns to do the anti-join on

        :return:    pd.DataFrame object
        """
    # Check the inputs
    check_columns(x, set(bycols))
    check_columns(y, set(bycols))

    # select only the entries of x that are not (['_merge'] == 'left_only') in y
    left_joined = x.merge(y, how = 'left', on=bycols, indicator=True).copy()
    left_only = left_joined.loc[left_joined['_merge'] == 'left_only'].drop('_merge', axis=1).copy()

    # left_only has all the columns of x and y, with _x, _y appended to any that
    # had the same names. Want to return left_only with only the columns of x, but
    # which is bycols + anything _x (I think?)
    #
    # first, identify columns that end in _x, subset left_only to just those, and
    # rename the columns to remove the _x:
    _x_ending_cols = [col for col in left_only if col.endswith('_x')]
    left_only_x_ending_cols = left_only[_x_ending_cols].copy()
    new_names = list(map(lambda z: z.replace('_x', ''),
                         left_only_x_ending_cols.columns))
    left_only_x_ending_cols.columns = new_names
    #
    # concatenate those with the bycols:
    out = pd.concat([left_only[bycols], left_only_x_ending_cols],
                    axis=1)

    # re-order the columns of out so that they are in the same order
    # as the columns of x
    cols_of_x_in_order = x.columns.copy()
    out = out[cols_of_x_in_order].copy()
    return out


def load_data_files(subdir):
    """ Read in a list of data frames.

        :param subdir:   pd.DataFrame str for a sub directory that exists

        :return:    pd.DataFrame object
    """
    # Make sure the sub directory exists.
    path = pkg_resources.resource_filename('stitches', subdir)
    if not os.path.isdir(path):
        raise TypeError(f"subdir does not exist")

    # Find all of the files.
    files_to_process = list_files(path)
    raw_data = []

    # Read in the data & concatenate into a single data frame.
    for f in files_to_process:
        if ".csv" in f:
            d = pd.read_csv(f)
        elif "pkl" in f:
            d = pd.read_pickle(f)
        else:
            d = None
        raw_data.append(d)
    raw_data = pd.concat(raw_data)

    return raw_data
