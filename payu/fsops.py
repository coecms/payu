# coding: utf-8
"""
Basic file system operations for Payu
-------------------------------------------------------------------------------
Contact: Marshall Ward <marshall.ward@anu.edu.au>
-------------------------------------------------------------------------------
Distributed as part of Payu, Copyright 2011 Marshall Ward
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
"""

import errno
import os
import re
import shutil

# Lustre target paths for symbolic paths cannot be 60 characters (yes, really)
# Delete this once this bug in Lustre is fixed
CHECK_LUSTRE_PATH_LEN = True

#---
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as ec:
        if ec.errno != errno.EEXIST:
            raise


#---
def make_symlink(src_path, lnk_path):

    # Check for Lustre 60-character symbolic link path bug
    for f_path in (src_path, lnk_path):
        if CHECK_LUSTRE_PATH_LEN and len(f_path) == 60:
            if os.path.isabs(f_path):
                f_path = '/.' + f_path
            else:
                f_path = './' + f_path

    try:
        os.symlink(src_path, lnk_path)
    except OSError as ec:
        if ec.errno != errno.EEXIST:
            raise
        elif not os.path.islink(lnk_path):
            # Warn the user, but do not interrput the job
            print("Warning: Cannot create symbolic link to {p}; a file named "
                  "{f} already exists.".format(p=src_path, f=lnk_path))
        else:
            # Overwrite any existing symbolic link
            if os.path.realpath(lnk_path) != src_path:
                os.remove(lnk_path)
                os.symlink(src_path, lnk_path)


#---
def patch_nml(nml_path, pattern, replace):
    """Replace lines matching ``pattern`` with ``replace`` of the Fortran
    namelist file located at ``nml_path``. If the file does not exist, then do
    nothing."""

    temp_path = nml_path + '~'

    try:
        with open(nml_path) as nml, open(temp_path, 'w') as temp:

            re_pattern = re.compile(pattern, re.IGNORECASE)
            for line in nml:
                if re_pattern.match(line):
                    temp.write(replace)
                else:
                    temp.write(line)

        shutil.move(temp_path, nml_path)

    except IOError as ec:
        if ec.errno != errno.ENOENT:
            raise
