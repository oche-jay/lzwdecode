"""
Created on 13 July 2017
@author: Oche Ejembi
Simple LZW Decoder for StarLeaf Assessment
"""

import argparse
import os.path  as ospath


def fileParser(filename):
    '''
    Generator method which parses the raw binary file and yields a single code
    from a 12-bit chunk of data from the
    raw file
    '''
    with open(filename, "rb") as rawFile:
        bytesArr = rawFile.read()

        charString = "";

        for i, byte in enumerate(str(bytesArr)):
            if byte == "":
                break
            hexVal = (ord(byte))

            # Because we have fixed 12-bit width structures,
            # we need to split every other byte into two halves
            # and append each half to either the previous byte or the
            # next byte, and then yeild that 12-bit code which will then be
            # used as a key to the ASCII and extended LZW dictionaries
            if (i + 1) % 3 == 0:
                charString += '%x' % (hexVal >> 4) or 0  # get alphanumeric representation of the 4 MSBs
                charString += '%x' % (hexVal & 0x0f) or 0  # get alphanumeric representation of the 4 LSBs
                yield charString
                charString = ""
            else:
                charString += '%x' % (hexVal >> 4) or 0
                if (i + 1) % 3 == 2:
                    yield charString
                    charString = ""
                charString += '%x' % (hexVal & 0x0f) or 0


def lzw_decode(filename):
    lzw_dict = {}
    prev = ""
    current = ""
    result = ""
    index = 256
    basen = ospath.basename(filename)
    base = ospath.splitext(basen)[0]

    # for really large files it may make sense to the write to file as we go along,
    # rather than store a large amount of data in memory. For this assessment, I am
    # doing both, but an optimized version could take file size into consideration.

    savefile = open(str(base) + "_uncompressed.txt", "wb")

    for v in fileParser(filename):
        decVal = int(v, 16)
        if decVal < 255:
            current = chr(decVal)
            # the base dictionary is ASCII so we leverage the in-built chr method for this

            savefile.write(current)
            result += current

            if prev != "":
                lzw_dict[index - 1] = prev + current
            index += 1
        elif decVal < 4096:
            #if the decVal is greater than 255 then it doesn't exist in ASCII
            # so we need to create and/or retrieve it
            if index - 1 == decVal:
                current = prev + prev[:1]
            else:
                current = lzw_dict[decVal]

            savefile.write(current)
            result += current

            if prev != "":
                lzw_dict[index - 1] = prev + current[:1]
            index += 1

        # reset dictionary index and start again if we have used more than 4096 (2^12) dictionary spaces
        if index == 4096:
            lzw_dict.clear()
            index = 256

        prev = current

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="LZW_Decode: A simple LZW decoder for StarLeaf's assessment.",
                                     epilog="This tool will write uncompressed data to console,and store the output"
                                            "to a file <filename_base>_uncompressed.txt")
    parser.add_argument("file", metavar="FILE", help="path of the file to decode")
    args = parser.parse_args()
    filename = args.file

    print lzw_decode(filename)

