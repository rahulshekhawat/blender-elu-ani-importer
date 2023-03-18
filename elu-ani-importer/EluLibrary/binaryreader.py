#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703

"""
Contains functions to read binary data from elu/ani files
"""

import datetime
import struct

"""
Functions to read binary data directly by passing the filestream object
"""


def read_int(file_stream, num_of_ints, offset=None, endian='<'):
    """
    Reads integers from filestream and returns them in a tuple\n
    Little endian by default\n
    @param file_stream Binary file stream to read ints from.\n
    @param num_of_ints Number of integers to read\n
    @param offset Cursor offset to read binary data in FileStream from. default=None.\n
    @param endian little or big endian method to use for struct unpacking\n
    @return Returns the tuple of integers\n
    """
    if offset is not None:
        file_stream.seek(offset)
    else:
        pass

    # If an exception occurs while unpacking, it should be handled in upper level function
    data = struct.unpack(endian + num_of_ints * 'i', file_stream.read(num_of_ints * 4))
    return data


def read_unsigned_int(file_stream, num_of_unsigned_ints, offset=None, endian='<'):
    """
    Reads unsigned integers from filestream and returns them in a tuple\n
    Little Endian by default\n
    @param file_stream Binary file stream to read unsigned ints from.\n
    @param num_of_unsigned_ints Number of unsigned integers to read\n
    @param offset Cursor offset to read binary data in FileStream from. default=None.\n
    @param endian little or big endian method to use for struct unpacking\n
    @return Returns the tuple of unsigned integers\n
    """
    if offset is not None:
        file_stream.seek(offset)
    else:
        pass

    # If an exception occurs while unpacking, it should be handled in upper level function
    data = struct.unpack(endian + num_of_unsigned_ints * 'I', file_stream.read(num_of_unsigned_ints * 4))
    return data


def read_word(file_stream, offset=None, endian='<'):
    """
    Reads a string from filestream. This function assumes that the\n
    first 4 bytes in FileStream represent an integer.\n
    This integer is used to determine the size of string to be read.\n
    Assumes characters to be ascii\n

    @param file_stream Binary file stream to read word from.\n
    @param offset Cursor offset to read binary data in FileStream from. default=None.\n
    @param endian little or big endian method to use for struct unpacking\n
    @return Returns the string read\n
    """
    if offset is not None:
        file_stream.seek(offset)
    else:
        pass

    string_size = read_int(file_stream, 1, offset, endian)[0]
    word = ''
    for i in range(string_size):
        # If an exception occurs while unpacking, it should be handled in upper level function
        # Character read will be b''
        character = struct.unpack('c', file_stream.read(1))[0]
        if ord(character) != 0:
            word += character.decode('ascii')
    return word


def read_short(file_stream, num_of_shorts, offset=None, endian='<'):
    """
    Reads short integers from filestream and returns them in a tuple\n
    Little endian by default\n
    @param file_stream Binary file stream to read shorts from.\n
    @param num_of_shorts Number of short integers to read\n
    @param offset Cursor offset to read binary data in FileStream from. default=None.\n
    @param endian little or big endian method to use for struct unpacking\n
    @return Returns the tuple of short integers\n
    """
    if offset is not None:
        file_stream.seek(offset)
    else:
        pass

    # If an exception occurs while unpacking, it should be handled in upper level function
    data = struct.unpack(endian + num_of_shorts * 'h', file_stream.read(num_of_shorts * 2))
    return data
    

def read_unsigned_short(file_stream, num_of_unsigned_shorts, offset=None, endian='<'):
    """
    Reads unsigned short integers from filestream and returns them in a tuple\n
    Little endian by default\n
    @param file_stream Binary file stream to read unsigned shorts from.\n
    @param num_of_unsigned_shorts Number of unsigned short integers to read\n
    @param offset Cursor offset to read binary data in FileStream from. default=None.\n
    @param endian little or big endian method to use for struct unpacking\n
    @return Returns the tuple of unsigned short integers\n
    """
    if offset is not None:
        file_stream.seek(offset)
    else:
        pass

    # If an exception occurs while unpacking, it should be handled in upper level function
    data = struct.unpack(endian + num_of_unsigned_shorts * 'H', file_stream.read(num_of_unsigned_shorts * 2))
    return data


def read_float(file_stream, num_of_floats, offset=None, endian='<'):
    """
    Reads floats from filestream and returns them in a tuple\n
    Little endian by default\n
    @param file_stream Binary file stream to read floats from.\n
    @param num_of_floats Number of floats to read\n
    @param offset Cursor offset to read binary data in FileStream from. default=None.\n
    @param endian little or big endian method to use for struct unpacking\n
    @return Returns the tuple of floats\n
    """
    if offset is not None:
        file_stream.seek(offset)
    else:
        pass

    # If an exception occurs while unpacking, it should be handled in upper level function
    data = struct.unpack(endian + num_of_floats * 'f', file_stream.read(num_of_floats * 4))
    return data
