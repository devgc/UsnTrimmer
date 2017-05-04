import re
import os
import sys
import argparse
import logging

if sys.platform == "win32":
    import msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

USN_RECORD_SIG = '..\x00\x00(\x02|\x03)\x00\x00\x00'
BUFFER_SIZE = 32768

def GetOptions():
    usage = "UsnTrimmer v0.1\n\n"\
            "This tool iterates backwards through the USN Journal file to find the "\
            "last block ({} bytes in size) with no USN Records, then locates the first "\
            "relative v2 or v3 journal entry and outputs the rest of the journal to standard out.\n\n"\
            "Example to output trimmed file:\n{} -j USN_JOURNAL > trimmed.usn".format(
                BUFFER_SIZE,
                os.path.basename(sys.argv[0])
            )
    
    options = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(usage)
    )
    
    options.add_argument(
        '-j',
        '--usnjrnl',
        dest='usnjrnl',
        action="store",
        type=unicode,
        required=True,
        help='The USN Journal file to trim.'
    )
    
    options.add_argument(
        '-v',
        '--verbose',
        dest='verbose',
        action="store_true",
        default=False,
        help='log the offsets being searched to stderr.'
    )
    
    return options

def Main():
    # Get options
    arguements = GetOptions()
    options = arguements.parse_args()
    
    # Check for verbose flag
    if options.verbose:
        logging.basicConfig(
            level=logging.DEBUG
        )
    
    # Set a start search offset for later use
    _start_search_offset = 0
    
    # Open the journal file
    with open(options.usnjrnl,'rb') as usnfh:
        # Get file size
        usnfh.seek(0,2)
        filesize = usnfh.tell()
        
        # Work our way backwards from the start of the file BUFFER_SIZE at a time
        for block_start_offset in range(filesize - BUFFER_SIZE, 0, -BUFFER_SIZE):
            logging.debug(u"block_start_offset: {}".format(block_start_offset))
            
            # Seek to starting offset of this block
            usnfh.seek(block_start_offset)
            # Read block into buffer
            raw_buffer = usnfh.read(BUFFER_SIZE)
            
            # Search raw buffer for record
            match = re.search(USN_RECORD_SIG,raw_buffer)
            if not match:
                # This is our first empty block. Stop here.
                _start_search_offset = block_start_offset
                break
            
        logging.debug(u"start_search_offset: {}".format(_start_search_offset))
        
        # Seek to start search offset
        usnfh.seek(_start_search_offset)
        # Read BUFFER_SIZE * 2 into our raw buffer
        raw_buffer = usnfh.read(BUFFER_SIZE + BUFFER_SIZE)
        
        # Search raw buffer for first record
        for match in re.finditer(USN_RECORD_SIG, raw_buffer):
            # The start offset of this match
            start_offset = match.regs[0][0]
            
            # Insure the start offset is on an 8 byte boundary
            if start_offset % 8 == 0:
                # The absolute offset to the start of this record
                record_start_offset = _start_search_offset + start_offset
                
                logging.debug(u"record_start_offset: {}".format(record_start_offset))
                
                # Seek to record buffer start offset
                usnfh.seek(record_start_offset,0)
                
                # Iterate through record buffer and write to stdout
                bytes_read = 0
                while bytes_read < filesize - record_start_offset:
                    raw_buffer = usnfh.read(BUFFER_SIZE)
                    sys.stdout.write(raw_buffer)
                    bytes_read+=len(raw_buffer)
                
                break

if __name__ == "__main__":
    Main()