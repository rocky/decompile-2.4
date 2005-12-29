#!/usr/bin/env python

"""Setup script for the 'decompyle' distribution."""

____revision__ = "$Id: setup.py,v 1.2 2005/12/29 20:23:04 dan Exp $"

from distutils.core import setup, Extension

setup (name = "decompyle",
       version = "2.3",
       description = "Python byte-code to source-code converter",
       author = "Hartmut Goebel",
       author_email = "hartmut@oberon.noris.de",
       url = "http://www.goebel-consult.de/decompyle/",
       packages=['decompyle'],
       scripts=['scripts/decompyle'],
       ext_modules = [Extension('decompyle/marshal_20',
                                ['decompyle/marshal_20.c'],
                                define_macros=[]),
                      Extension('decompyle/marshal_22',
                                ['decompyle/marshal_22.c'],
                                define_macros=[]),
                      Extension('decompyle/marshal_23',
                                ['decompyle/marshal_23.c'],
                                define_macros=[]),
                      Extension('decompyle/marshal_24',
                                ['decompyle/marshal_24.c'],
                                define_macros=[]),
                      ]
      )
