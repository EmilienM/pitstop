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

'''
'''

import os
import re
import subprocess
import sys

_NO_PKG_REGEXP = [
    re.compile(r"^/opt/(?P<pkg>[^/]+)/"),
    re.compile(r"^/var/lib/yum/"),
    re.compile(r"^(/usr)?/lib/python2.7/site-packages/(?P<pkg>oschecks)/"),
    re.compile(r"^(/usr)?/bin/(?P<pkg>oschecks)-"),
]


def chroot(dir_, cmd):
    return subprocess.check_output(['sudo', 'chroot', dir_] + cmd.split(' '))


def file2rpm(stream, assoc, topdir):
    line = stream.readline()
    lis = []
    while line:
        line = line.strip()
        pkg = None
        for regexp in _NO_PKG_REGEXP:
            is_not_pkg = regexp.search(line)
            if is_not_pkg:
                try:
                    pkg = is_not_pkg.group('pkg')
                    sys.stderr.write('EXCEPTION FOUND %s for %s\n'
                                     % (pkg, line))
                except IndexError:
                    sys.stderr.write('IGNORING %s\n' % (line))
                break
        else:
            if line[-5:] == '.real':
                line = line[:-5]
            try:
                pkg = assoc[line]
            except KeyError:
                try:
                    if line[0:4] == '/usr':
                        pkg = assoc[line[4:]]
                    else:
                        pkg = assoc['/usr' + line]
                except KeyError:
                    try:
                        pkg = chroot(topdir,
                                     'rpm -qf %s --qf %%{NAME}' % line)
                        pkg = pkg.strip()
                        sys.stderr.write('FOUND %s for %s\n' % (pkg, line))
                    except subprocess.CalledProcessError:
                        sys.stderr.write('NOTHING FOUND for %s\n' % (line))
                        pkg = line
        if pkg and pkg not in lis:
            lis.append(pkg)
        line = stream.readline()
    return lis


def load_assoc(stream):
    assoc = {}
    line = stream.readline()
    while line:
        fname, rpm = line.strip().split('\t')
        assoc[fname] = rpm
        line = stream.readline()
    return assoc


def main():
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: %s <content filename> <chroot>\n'
                         % sys.argv[0])
        sys.exit(1)
    
    proc_mounted = os.path.isfile(os.path.join(sys.argv[2],
                                               'proc', 'cmdline'))
    if not proc_mounted:
        chroot(sys.argv[2], 'mount -t proc None /proc')
    assoc = load_assoc(open(sys.argv[1]))
    for pkgname in file2rpm(sys.stdin, assoc, sys.argv[2]):
        print pkgname
    if not proc_mounted:
        chroot(sys.argv[2], 'umount /proc')

if __name__ == "__main__":
    main()

# file2rpm.py ends here
