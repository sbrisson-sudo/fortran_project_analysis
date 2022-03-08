#!/usr/bin/env python3

import os, sys
import re

from aiohttp import DefaultResolver

# REGEXES

re_directory = r"([\.\w]+)$"

re_fortran = r".[fF](90)?$"
re_c_source = r".c$"
re_c_header = r".h$"

re_source = re.compile('|'.join([re_fortran, re_c_source, re_c_header])) 

re_function = r'(function|FUNCTION)[\s]*(\b[\w\d]+\b)\(([\s\w,]*)\)'
re_subroutine = r'(subroutine|SUBROUTINE)[\s]*(\b[\w\d]+\b)\(([\s\w,]*)\)'
re_program = r'^[\s]*(program|PROGRAM)'

# CLASSES

class SourceDirectory:
    def __init__(self, name, path, pDir):
        self.name = name
        self.path = os.path.join(path, name)
        self.pDir = pDir
        self.dirs = []
        self.files = []
        self.contains_source_code = False
        
    def __repr__(self):
        return f"d - {self.name}"
    
    def set_as_source(self):
        self.contains_source_code = True
        if self.pDir: self.pDir.set_as_source()

languages = {
    "f90"   : "fortran 90",
    "F90"   : "fortran 90",
    "f"     : "fortran 77",
    "c"     : "C source",
    "h"     : "C header",
}        
        
def get_language(fname):
    ext = fname.split(".")[-1]
    return languages[ext]

class SourceFile:
    def __init__(self, name, dir):
        self.name = name
        self.dir = dir
        self.lang = get_language(name)
        self.main = False
        self.procedures = []

    def __repr__(self):
        out = "\033[1;32m" + self.dir.name + "\033[1;00m" + " : " + colors_lang[self.lang] + self.name
        for p in self.procedures:
            out += "\n" + p.__repr__()
        return out
    
    def path(self):
        return os.path.join(self.dir.path, self.name)
    
class Procedure:
    def __init__(self, file, name, args, nature):
        self.file = file
        self.name = name
        self.args = args
        self.nature = nature
    def __repr__(self):
        return "\033[1;97m"+self.name+"\033[1;00m"+f"({self.args})"

colors_lang = {
    "fortran 90" : "\033[1;36m",
    "fortran 77" : "\033[1;35m",
    "C source" : "\033[1;34m",
    "C header" : "\033[1;33m",
}

class SourceCodeProject:
    
    def __init__(self, root):
        
        self.root = root
        
        self.source_directories = {}
        self.source_files = []
        self.procedures = []
        
        self.init_project()
        
        self.get_files()
        
        self.get_procedures()
        
    def init_project(self):
    
        root_directory_name = re.search(re_directory, self.root).group(1)

        self.root_dir = SourceDirectory(
            root_directory_name,
            os.path.dirname(self.root),
            None
        )
        
        self.source_directories[self.root_dir.path] = self.root_dir
        
        
    def get_files(self):
                    
        # parcours top bottom : association des parents aux enfants

        for root, d_names, f_names in os.walk(self.root):
                            
            parent_dir = self.source_directories[root]
            
            for d in d_names:
                root_d = os.path.join(root, d)
                self.source_directories[root_d] = SourceDirectory(d, root, parent_dir)
                
            for f in f_names:
                if re.search(re_source, f):
                    self.source_files.append(SourceFile(f, parent_dir))
                    
        # parcours sens inverse : association des enfants aux parents

        for f in self.source_files:
            self.source_directories[f.dir.path].files.append(f)
        for d in self.source_directories.values():
            if d.pDir: self.source_directories[d.pDir.path].dirs.append(d)
            
        # parcours sens inverse pour éliminer directories ne contenant pas de code
        for f in self.source_files:
            if not(f.dir.contains_source_code):
                f.dir.set_as_source()
                    
    def get_procedures(self):
        
        for f in self.source_files:
                
            with open(f.path(), "r", errors='ignore') as io:
                for l in io.readlines():
                    
                    if re.search(re_program, l):
                        f.main = True
                    
                    match = re.search(re_function, l)
                    if match:
                        name = match.group(2)
                        args = match.group(3)
                        self.procedures.append(Procedure(f,name,args, "function"))
                        f.procedures.append(self.procedures[-1])
                        
                    match = re.search(re_subroutine, l)
                    if match:
                        name = match.group(2)
                        args = match.group(3)
                        self.procedures.append(Procedure(f,name,args, "subroutine"))
                        f.procedures.append(self.procedures[-1])
    
# PRINTING

    def print_files(self):
        
        SourceCodeProject.print_files_r(self.root_dir, 0)

    def print_files_r(dir, n):
                    
        if not(dir.contains_source_code): return
        
        print("\n" + n*"   " + "\033[1;32m" + dir.name)
        for d in dir.dirs:
            SourceCodeProject.print_files_r(d, n+1)
        print()
        for f in dir.files:
            print((n+1)*"   " + colors_lang[f.lang] + f.name+ ("\033[1;91m (main)" if f.main else ""))
            
        if n == 0: print("\033[1;00m")
        
    def print_all(self):
        
        SourceCodeProject.print_all_r(self.root_dir, 0)

    def print_all_r(dir, n):
                
        if not(dir.contains_source_code): return
        
        print("\n" + n*"   " + "\033[1;32m" + dir.name)
        for d in dir.dirs:
            SourceCodeProject.print_all_r(d, n)
        print()
        for f in dir.files:
            if f.name in hide_files: continue
            print((n+1)*"   " + colors_lang[f.lang] + f.name + ("\033[1;91m (main)" if f.main else ""))
            for p in f.procedures:
                print((n+2)*"   " + "\033[1;00m", p)
    
    
if __name__ == "__main__":
    

    project_source = SourceCodeProject(os.getcwd())

    hide_files = [
        "nrutil.f90"
    ]
    
    # project_source.print_files()
    project_source.print_all()
    