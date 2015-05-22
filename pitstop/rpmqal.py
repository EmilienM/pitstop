#!/usr/bin/env python

import rpm

ts = rpm.TransactionSet()
mi = ts.dbMatch()
for h in mi:
    fi = h.fiFromHeader()
    for f in fi:
        print '%s\t%s' % (f[0], h['NAME'])
