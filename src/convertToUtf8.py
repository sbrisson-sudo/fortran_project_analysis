#!/usr/bin/env python3

import os, sys
import re

encoding_log = "encodings.log"
source_regex = "'.*.(f|f90|F90|c|h)$'"

os.system(f"for f in $(find . | grep -E  {source_regex}); do file -i $f; done > {encoding_log}")
# os.system(f"for f in $(find . | grep -E  {source_regex}); do encguess $f; done > {encoding_log}")


encoding_regex = r"^(\.[\d\w\/\.]+:)[\w\W]*(charset=[\w\d-]+)$"

files = {}

with open(encoding_log, "r") as io:
    for l in io.readlines():
        search = re.search(encoding_regex, l)
        file = search.group(1)[:-1]
        encod = search.group(2)[8:]
        files[file] = encod
        
encod_in = {
    "iso-8859-1" : "ISO_8859-1"
}
        
encod_out = [
    "us-ascii"
]

for f, encod in files.items():
    
    if not(encod in encod_ok):
  
        print(f"{f} Invalid encoding : {encod}")
        