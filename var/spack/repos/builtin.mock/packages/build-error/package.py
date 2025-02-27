# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class BuildError(Package):
    """This package has an install method that fails in a build script."""

    homepage = "http://www.example.com/trivial_install"
    url      = "http://www.unit-test-should-replace-this-url/trivial_install-1.0.tar.gz"

    version('1.0', '0123456789abcdef0123456789abcdef')

    def install(self, spec, prefix):
        with open('configure', 'w') as f:
            f.write("""#!/bin/sh\n
echo 'checking build system type... x86_64-apple-darwin16.6.0'
echo 'checking host system type... x86_64-apple-darwin16.6.0'
echo 'checking for gcc... /Users/gamblin2/src/spack/lib/spack/env/clang/clang'
echo 'checking whether the C compiler works... yes'
echo 'checking for C compiler default output file name... a.out'
echo 'checking for suffix of executables...'
echo 'configure: error: in /path/to/some/file:'
echo 'configure: error: cannot run C compiled programs.'
exit 1
""")
        configure()
