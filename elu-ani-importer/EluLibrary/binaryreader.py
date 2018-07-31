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
def ReadInt(FileStream, NumOfInts, Offset=None, Endian='<'):
    """
    Reads integers from filestream and returns them in a tuple\n
    Little endian by default\n
    @param NumOfInts Number of integers to read\n
    @param Offset Cursor offset to read binary data in FileStream from. default=None.\n
    @return Returns the tuple of integers\n
    """
    if Offset != None:
        FileStream.seek(Offset)
    else:
        pass

    # If an exception occurs while unpacking, it should be handled in upper level function
    Data = struct.unpack(Endian + NumOfInts * 'i', FileStream.read(NumOfInts * 4))
    return Data


def ReadUInt(FileStream, NumOfUInts, Offset=None, Endian='<'):
    """
    Reads unsigned integers from filestream and returns them in a tuple\n
    Little Endian by default\n
    @param NumOfUInts Number of unsigned integers to read\n
    @param Offset Cursor offset to read binary data in FileStream from. default=None.\n
    @return Returns the tuple of unsigned integers\n
    """
    if Offset != None:
        FileStream.seek(Offset)
    else:
        pass

    # If an exception occurs while unpacking, it should be handled in upper level function
    Data = struct.unpack(Endian + NumOfUInts * 'I', FileStream.read(NumOfUInts * 4))
    return Data


def ReadWord(FileStream, Offset=None, Endian='<'):
    """
    Reads a string from filestream. This function assumes that the first\n
    first 4 bytes in FileStream represent an integer.\n
    This integer is used to determine the size of string to be read.\n
    Assumes characters to be ascii\n

    @param Offset Cursor offset to read binary data in FileStream from. default=None.\n
    @return Returns the string read\n
    """
    if Offset != None:
        FileStream.seek(Offset)
    else:
        pass

    StringSize = ReadInt(FileStream, 1, Offset, Endian)[0]
    Word = ''
    for i in range(StringSize):
        # If an exception occurs while unpacking, it should be handled in upper level function
        # Character read will be b''
        Char = struct.unpack('c', FileStream.read(1))[0]
        if ord(Char) != 0:
            Word += Char.decode('ascii')
    return Word


def ReadShort(FileStream, NumOfShorts, Offset=None, Endian='<'):
    """
    Reads short integers from filestream and returns them in a tuple\n
    Little endian by default\n
    @param NumOfShorts Number of short integers to read\n
    @param Offset Cursor offset to read binary data in FileStream from. default=None.\n
    @return Returns the tuple of short integers\n
    """
    if Offset != None:
        FileStream.seek(Offset)
    else:
        pass

    # If an exception occurs while unpacking, it should be handled in upper level function
    Data = struct.unpack(Endian + NumOfShorts * 'h', FileStream.read(NumOfShorts * 2))
    return Data
    

def ReadUShort(FileStream, NumOfUShorts, Offset=None, Endian='<'):
    """
    Reads unsigned short integers from filestream and returns them in a tuple\n
    Little endian by default\n
    @param NumOfUShorts Number of unsigned short integers to read\n
    @param Offset Cursor offset to read binary data in FileStream from. default=None.\n
    @return Returns the tuple of unsigned short integers\n
    """
    if Offset != None:
        FileStream.seek(Offset)
    else:
        pass

    # If an exception occurs while unpacking, it should be handled in upper level function
    Data = struct.unpack(Endian + NumOfUShorts * 'H', FileStream.read(NumOfUShorts * 2))
    return Data


def ReadFloat(FileStream, NumOfFloats, Offset=None, Endian='<'):
    """
    Reads floats from filestream and returns them in a tuple\n
    Little endian by default\n
    @param NumOfFloats Number of floats to read\n
    @param Offset Cursor offset to read binary data in FileStream from. default=None.\n
    @return Returns the tuple of floats\n
    """
    if Offset != None:
        FileStream.seek(Offset)
    else:
        pass

    # If an exception occurs while unpacking, it should be handled in upper level function
    Data = struct.unpack(Endian + NumOfFloats * 'f', FileStream.read(NumOfFloats * 4))
    return Data
