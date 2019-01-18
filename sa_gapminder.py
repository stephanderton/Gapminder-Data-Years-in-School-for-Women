
# Project: Investigate the Gapminder Dataset Indicators for Education
#
# Stephanie Anderton
# June 2018
#
# Support funcions for converting, trimming and cleaning gapminder datasets
# and other miscellaneous functions
#
# Import packages

import numpy as np
import pandas as pd


def convert_xls_to_csv(file_xls, file_csv):
    """
    Read in the original .xls file and convert to .csv.
    Renames the first column label to 'Country' for compatibility with other datasets.
    
    Args:
        file_xls    path/filename of .xls file to convert
        file_csv    path/filename to save in .csv format
        
    Returns:
        df          dataframe with data from the .xlsx file;
                    or None if .xlsx filepath not found, or pathname for .csv location is not found
    """
    # initialize
    df = None

    try:
        df = pd.read_excel(file_xls)
    except:
        print("Error: File not found: '{}'".format(file_xls))
    else:
        # Rename the first column to 'Country'
        df.rename(columns={df.columns[0]: 'Country'}, inplace=True)

        # Save to CSV
        try:
            df.to_csv(file_csv, index=False)
        except:
            print("Error: Path not found: '{}'".format(file_csv))
    
    return df


def valid_args(df, years=None, threshold=20, limit=3):
    """
    Validates argument values.
    
    Args:
        df            required: dataframe
        years         optional: string or list containing year(s) for column in dataframe; or None 
        threshold     optional: % in range [0 - 99%]
        limit         optional: number of NaN entries to be filled using the forward-fill and
                      back-fill method; max = 5
    
    Returns:
        is_valid      True/False
    """
    # initialize
    is_valid = True

    if type(df) is type(pd.DataFrame()):    # df is required
        
        if years is None:    # None: skip check for this argument
            pass
    
        elif type(years) is str:
            if not df.columns.contains(years):
                print("Error: year '{}' does not exist in dataframe.".format(years))
                is_valid = False

        elif type(years) is list:
            for year in years:
                if not df.columns.contains(year):
                    print("Error: year '{}' does not exist in dataframe.".format(year))
                    is_valid = False

    else:
        print("Error: Improper type for dataframe")
        is_valid = False

    if (threshold < 0) | (threshold > 99):
        print("Error: threshold '{}' must be in range [0 - 99%]".format(threshold))
        is_valid = False
        
    if (limit < 0) | (limit > 5):
        print("Error: limit '{}' must be in range [0 - 5]".format(limit))
        is_valid = False
    
    return is_valid


def create_sub_df(df, list_cols, prepend_str):
    """
    Extracts the listed columns from the dataframe, prepends a string and returns a new dataframe.
    
    Args:
        df             dataframe with columns to copy
        list_cols      list with column header names
        prepend_str    string to prepend to the column labels
    
    Returns:
        df_sub         new dataframe with the selected columns; or None if input args invalid
    """
    # ----- CHECK ARGS! -----
    if valid_args(df, years=list_cols) == False:
        return None

    df_sub = df[list_cols].copy()
    df_sub.rename(columns=lambda x: prepend_str + '_' + x, inplace=True)
    
    # undo the rename for the 'Country' column
    str_country = prepend_str + '_Country'
    df_sub.rename(columns={str_country: 'Country'}, inplace=True)

    return df_sub


def print_info(df, year):
    """
    Print summary information for the dataframe from specified year.
    
    Args:
        df      dataframe to get information
        year    (string) column name of year from wich to extract the information
    """
    # ----- CHECK ARGS! -----
    if valid_args(df, years=year) == False:
        return


    print("Details for dataframe starting from year:      ", year)
    print("Shape of dataframe (rows, columns):            ", df.loc[:, year:].shape)
    print("Min and Max values:                            ", 
          df.loc[:, year:].min().min(), ", ", df.loc[:, year:].max().max())
    print("Total number of countries with NaNs:           ", df.loc[:, year:].isnull().any(axis=1).sum())
    print("Total number of years with NaNs:               ", df.loc[:, year:].isnull().any().sum())
    return


def trim_cols(df, list_cols, verbose=False):
    """
    Trim specified columns from dataframe.
    
    Args:
        df           dataframe to remove columns from
        list_cols    list with column header names
        verbose      optional: display detailed output of cleaning; default is False
        
    Returns:
        df           trimmed dataframe; or None if input args invalid
    """
    # ----- CHECK ARGS! -----
    if valid_args(df, years=list_cols) == False:
        return None


    # Check the verbose argument, if it's not valid then assume False
    if type(verbose) is not bool:
        verbose = False


    if type(list_cols) is list:
        df.drop(list_cols, axis=1, inplace=True)

        if verbose == True:
            print("Number of years trimmed:                       ", len(list_cols))
            print("Number of countries still with NaNs:           ", df.isnull().any(1).sum())
            print("Shape of trimmed dataframe:                    ", df.shape)
    else:
        pass    # do nothing

    return df


def transpose_df(df, column_type):
    """
    Transposes the dataframe: 
    - when column type is country, use names in row [1] as the column header,
    - when column type is year, put country names back in column [0], not as index.
    Use the dataframe's name attribute to save the column type.
    
    Args:
        df             Input dataframe to transpose
        column_type    'country': use first row [0] with country names to reset column headers
                       'year': transforms dataframe to original shape with years in columns, and
                       shifts country names into column [0], not as index
    
    Returns:
        df_T           Transposed dataframe; or None if input args invalid
    """
    # ----- CHECK ARGS! -----
    if valid_args(df) == False:
        return None


    df_T = df.transpose()

    if column_type == 'country':
        # the country column with names ends up in the first row of the dataframe,
        # but we want them as column headers instead; essentially shift all rows up by 1
        header = df_T.iloc[0]
        df_T = df_T[1:]
        df_T.columns = header

        # fix datatype of numeric data, transpose() changes it to object type (float)
        df_T = df_T.apply(lambda x: pd.to_numeric(x))
        df_T.name = 'col_type_country'    # use name attribute to save the column type

    elif column_type == 'year':
        # fix datatype of numeric data, transpose() changes it to object type (float)
        df_T = df_T.apply(lambda x: pd.to_numeric(x))

        # reset index, moving country names to first column, [0]
        df_T = df_T.reset_index()
        df_T.name = 'col_type_year'    # use name attribute to save the column type

    else:
        df_T.name = 'col_type_other'
    
    return df_T


def clean_missing_data(df, threshold, limit, verbose=False):
    """
    Clean dataframe steps: 
    (Trimming steps 1 & 2 have already been done in trim_and_clean())
    3.  Drop rows for countries with NaN counts above the set threshold %:  
        some are missing too much data, or they no longer exist. This list is displayed.
    4.  Fill rows for countries with NaN counts below the set threshold %, using the back-fill 
        and forward-fill methods, up to the set limit (default: 3) Some NaNs may remain.
    
    Transposes the input dataframe to simplify the search for NaNs by country: country data 
    is in column format, this avoids the 'Country' label from being used as fill in later code.

    Args:
        df              dataframe
        threshold       threshold of NaNs at which a column will be dropped; range [0 - 99%]
        limit           max number of missing data entries to be filled using the forward-fill 
                        and back-fill method
        verbose         optional: display detailed output of cleaning; default is False

    Returns:
        df              cleaned dataframe; or None if input args invalid
        b_data_trimmed  True/False, indicates if rows were dropped
    """
    # ----- CHECK ARGS! -----
    if valid_args(df, threshold=threshold, limit=limit) == False:
        return None


    # Check the verbose argument, if it's not valid then assume False
    if type(verbose) is not bool:
        verbose = False


    df_T = transpose_df(df, 'country')
    b_data_trimmed = False

    if df_T is not None:

        # ----- step: 3 ----- Drop rows for countries with NaN counts above the set threshold

        list_above_threshold = df_T.isnull().sum()/len(df_T) > threshold/100
        if list_above_threshold.any():

            country_drop_list = df_T.columns[list_above_threshold]
            len_list = len(country_drop_list)
            if verbose == True:
                print("Countries with NaN counts above threshold:     ", len_list)

            if len_list > 0:

                df_T.drop(country_drop_list, axis=1, inplace=True)
                b_data_trimmed = True

                if verbose == True:
                    print(country_drop_list)    # print list of countries
                    print("...Countries dropped")

        # ----- step: 4 ----- Fill rows for countries with NaN counts below the set threshold

        country_NaN_total = df_T.isnull().any().sum()
        if verbose == True:
            print("Countries with NaN counts below threshold:     ", country_NaN_total)
        
        if country_NaN_total > 0:
            if verbose == True:
                # print list of countries with NaN count
                country_NaN_list = df_T.columns[df_T.isnull().sum() > 0]
                print(df_T[country_NaN_list].isnull().sum())


            df_T = df_T.fillna(method='bfill', limit=limit)
            df_T = df_T.fillna(method='ffill', limit=limit)


            if verbose == True:
                country_NaN_total = df_T.isnull().any().sum()
                print("Countries with NaN counts remaining after filling: ", country_NaN_total)

                if country_NaN_total > 0:
                    # print list of countries with NaN count
                    country_NaN_list = df_T.columns[df_T.isnull().sum() > 0]
                    print(df_T[country_NaN_list].isnull().sum())
        else:
            pass

        df = transpose_df(df_T, 'year')    # back to columns with years, countries by row

    else:
        pass
    
    return df, b_data_trimmed


def trim_and_clean(df_raw, start_year, threshold, limit, verbose=False):
    """
    Trim and clean a copy of the raw dataframe in four steps:
    
    1.  Trim the columns (years) prior to start_year
    2.  Trim rows for countries that contain ALL NaNs (missing data)
    3.  Drop rows for countries with NaN counts above the set threshold %
    4.  Fill rows for countries with NaN counts below the set threshold %
    
    Display list of any countries left with missing data.

    Args:
        df_raw        original dataframe
        start_year    year for first column in trimmed dataframe
        threshold     % of NaNs to drop a country : range [0 - 99%]
        limit         number of NaN entries to be filled using the forward-fill and back-fill method
        verbose       optional: display detailed output of cleaning; default is False
    
    Returns:
        df            the trimmed and cleaned dataframe; or None if input arguments are invalid
    """
    # ----- CHECK ARGS! -----
    if valid_args(df_raw, years=start_year, threshold=threshold, limit=limit) == False:
        return None


    # Check the verbose argument, if it's not valid then assume False
    if type(verbose) is not bool:
        verbose = False


    # Make a COPY of the dataframe to work on
    df = df_raw.copy(deep=True)

    b_data_trimmed = False
    b_data_cleaned = False

    if verbose == True:
        print("First year for trimmed dataset:                ", start_year)
        print("Threshold of NaNs for dropping countries:      ", threshold, "%")
        print("Limit for forward and back fill:               ", limit)
        print("Shape of original dataframe:                   ", df.shape)

    # ----- step: 1 ----- Trim the year columns prior to start_year
    # Note: ignore column[0] with contains country names
    
    index_year = df.columns.get_loc(start_year)
    if index_year > 1:

        df.drop(df.columns[1: index_year], axis=1, inplace=True)
        b_data_trimmed = True

        if verbose == True:
            print("Number of years trimmed:                       ", index_year-1)

    country_NaN_total = df.isnull().any(axis=1).sum()
    if country_NaN_total > 0:

        if verbose == True:
            print("Number of countries with NaNs:                 ", country_NaN_total)

        # ----- step: 2 ----- Trim rows for countries that contain ALL NaNs (missing data)

        df.dropna(how='all', subset=df.columns[1:], inplace=True)

        # ----- step: 3 & 4 -----

        df, b_data_cleaned = clean_missing_data(df, threshold, limit, verbose=verbose)

        # ----- summary -----

        if verbose == True:
            if df is not None:
                year_NaNs_list = df.columns[df.isnull().sum() > 0]
                
                if len(year_NaNs_list) > 0:
                    print("Years containing NaNs (cleaned data): ")
                    print(df[year_NaNs_list].isnull().sum())

                if b_data_trimmed == True or b_data_cleaned == True:
                    print("Shape of trimmed dataframe:                    ", df.shape)
                else:
                    print("No trimming required.")

    else:    # dataframe does not have any NaNs
        print("Number of countries with NaNs:                 ", 0)

    print("------")
    return df


def version():
    print("sa_gapminder - build 38")

def main():
    version()

if __name__ == "__main__":
    main()
