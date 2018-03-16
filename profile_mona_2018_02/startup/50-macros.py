print(__file__)

"""
functions converted from macros_2bmb.py (PyEpics macros from Xianghui)
"""

# HDF5 File Writer Plugin configuration for 2-BM-B
# -5: means create maximum 5 directories as needed
MAX_DIRECTORIES_TO_CREATE = -5


def auto_increment_prefix_number():
    """increment the prefix number if permitted"""
    if cpr_auto_increase.value == 'Yes':
        cpr_prefix_num.put(str(int(cpr_prefix_num.value)+1))


def string_by_index(choices_str, index, delim=" "):
    """
    pick a substring from a delimited string using the index as reference
    
    choices_str : str
        string with possible choices, separated by delimiter
    delim : str
        string delimiter
    index : int
        number (0-based) of label to be selected
    """
    choices = choices_str.split(delim)
    if index in range(len(choices)):
        return choices[index]
    return None


def make_timestamp(the_time=None):
    """
    such as: 2018-01-12 15:40:46 is FriJan12_15_40_46_2018
    
    the_time : str
        string representation of the time
        default time.asctime()
        example: Sun Jan 4 18:59:31 1959
        result:  SunJan4_18_59_31_1959
        
    """
    the_time = the_time or time.asctime()
    timestamp = [x for x in the_time.rsplit(' ') if x!='']
    timestamp = ''.join(timestamp[0:3]) \
                + '_' + timestamp[3].replace(':','_') \
                + '_' + timestamp[4]
    return timestamp


def trunc(v, n=3):
    """truncate `v` (a float) to `n` digits precision"""
    factor = pow(10, n)
    return int(v*factor)/factor

