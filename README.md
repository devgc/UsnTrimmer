# UsnTrimmer
A tool to trim a USN Journal file extracted by other tools

```
UsnTrimmer.py -h
usage: UsnTrimmer.py [-h] -j USNJRNL [-v]

UsnTrimmer v0.1

This tool iterates backwards through the USN Journal file to find the last block (32768 bytes in size) with no USN Records, then locates the first relative v2 or v3 journal entry and outputs the rest of the journal to standard out.

Example to output trimmed file:
UsnTrimmer.py -j USN_JOURNAL > trimmed.usn

optional arguments:
  -h, --help            show this help message and exit
  -j USNJRNL, --usnjrnl USNJRNL
                        The USN Journal file to trim.
  -v, --verbose         log the offsets being searched to stderr.
```

## How it works
This tools starts at the end of the USN Journal file and works its way back by searching for the start of the USN record buffer. For more on how USN records are stored see: https://technet.microsoft.com/en-us/library/cc788042(v=ws.11).aspx.

Why does it start from the end and work itself back? This is because the record area will always be at the end of the file and when you have a many gig USN Journal, its faster to start at the end then work your way though many gigs of 0x00s.
