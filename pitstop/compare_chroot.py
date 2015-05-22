#!/usr/bin/env python
#
# Copyright (C) 2015 eNovance SAS <licensing@enovance.com>
#
# Author: Frederic Lepied <frederic.lepied@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

'''compare 2 chroots and print all changed files.
'''

import subprocess
import sys


def compare_chroots(old, new):
    lis = []
    cmd = "sudo rsync -n -aik %s/ %s/ | egrep '^>f'" % (new, old)
    for line in subprocess.check_output(cmd, shell=True).split('\n'):
        lis.append('/' + line[12:])
    return lis


def main():
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: %s <old chroot> <new chroot>' % sys.argv[0])
        sys.exit(1)
    for fname in compare_chroots(sys.argv[1], sys.argv[2]):
        print fname

if __name__ == "__main__":
    main()

# compare_chroot.py ends here
