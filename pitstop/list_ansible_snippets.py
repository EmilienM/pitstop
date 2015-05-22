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

import subprocess
import sys

import yaml


def chroot(dir_, cmd):
    return subprocess.check_output(['sudo', 'chroot', dir_] + cmd.split(' '))

DEPS = {}


def deps(dir_, pkg, aliases):
    if pkg in DEPS:
        #sys.stderr.write('got cache for %s: %s\n' % (pkg, DEPS[pkg]))
        return DEPS[pkg]
    #sys.stderr.write('processing dep for %s\n' % (pkg,))

    def cache_values(val, key, aliases, lst):
        lst[key] = val
        for alias in aliases:
            lst[alias] = val

    try:
        output = chroot(dir_, 'rpm -q --requires %s' % pkg)
    except subprocess.CalledProcessError:
        sys.stderr.write('Package %s not present\n' % pkg)
        cache_values([], pkg, aliases, DEPS)
        return []
    list_ = []
    for line in output.split('\n'):
        prov = line.split(' ')[0]
        #sys.stderr.write('%s dep is %s\n' % (pkg, prov,))
        if prov[:6] == 'rpmlib' or prov == '':
            continue
        dep_list = chroot(dir_, 'rpm -q --whatprovides %s' % prov).strip()
        for dep in dep_list.split('\n'):
            #sys.stderr.write('%s dep is %s provided by %s\n' %
            #                 (pkg, prov, dep))
            if dep == pkg:
                if prov not in aliases:
                    aliases.append(prov)
            elif dep not in list_:
                list_.append(dep)
                # to break loops: put what we have so far
                cache_values(list_, pkg, aliases, DEPS)
                for recdep in deps(dir_, dep, [prov]):
                    if recdep not in list_:
                        list_.append(recdep)
    cache_values(list_, pkg, aliases, DEPS)
    return list_


def get_all_deps(dir_, assoc, new):
    for pkg in assoc:
        for dep in deps(dir_, pkg, []):
            if dep not in assoc:
                new[dep] = assoc[pkg]
    for pkg in new:
        if pkg in assoc:
            for snippet in new[pkg]:
                assoc[pkg].append(snippet)
        else:
            assoc[pkg] = new[pkg]


def main():
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: %s <yaml file> <chroot top dir>\n' %
                         sys.argv[0])
        sys.exit(1)
    assoc = yaml.load(open(sys.argv[1]).read())
    new = {}
    length = 1
    while length != 0:
        new = {}
        get_all_deps(sys.argv[2], assoc, new)
        length = len(new)
        sys.stderr.write('%d\n' % length)
    print yaml.dump(assoc)
    sys.stderr.write('%d packages' % len(assoc))

main()

# list_ansible_snippets.py ends here
