# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class RktDynextLib(RacketPackage):
    """Racket library for running a C compiler/linker."""

    git      = "ssh://git@github.com/racket/cext-lib.git"

    maintainers = ['elfprince13']

    version('8.3', commit='cc22e2456df881a9008240d70dd9012ef37395f5')  # tag = 'v8.3'
    depends_on('rkt-base@8.3', type=('build', 'run'), when='@8.3')

    name = 'dynext-lib'
    pkgs = True
    subdirectory = name
