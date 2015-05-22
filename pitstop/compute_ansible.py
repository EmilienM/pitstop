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

'puppet partial resource_list --resource package --tag cloud::monitoring::server::sensu os-ci-test10.ring.enovance.com'

import subprocess
import sys
import yaml

puppet2ansible = yaml.load(open(sys.argv[1]).read())
pkg2ansible = {}
for puppet_module in puppet2ansible:
    sys.stderr.write('PUPPET: %s\n' % puppet_module)
    try:
        res = subprocess.check_output('puppet partial resource_list '
                                      '--resource package --tag %s %s' %
                                      (puppet_module, sys.argv[2]), shell=True)
    except Exception as excpt:
        print excpt
        continue
    pkgs = []
    for pkg in res.split('\n'):
        sys.stderr.write('PKG: %s\n' % pkg)
        if ' ' in pkg or pkg == '':
            continue
        try:
            pkg2ansible[pkg] = pkg2ansible[pkg] + puppet2ansible[puppet_module]['snippet']
        except KeyError:
            pkg2ansible[pkg] = puppet2ansible[puppet_module]['snippet']
        pkgs.append(pkg)
    if len(pkgs) == 0:
        sys.stderr.write('NO PKG FOR %s\n' % puppet_module)
print yaml.dump(pkg2ansible)

# compute_ansible.py ends here
