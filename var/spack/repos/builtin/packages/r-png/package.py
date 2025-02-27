# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class RPng(RPackage):
    """Read and write PNG images.

    This package provides an easy and simple way to read, write and display
    bitmap images stored in the PNG format. It can read and write both files
    and in-memory raw vectors."""

    cran = "png"

    version('0.1-7', sha256='e269ff968f04384fc9421d17cfc7c10cf7756b11c2d6d126e9776f5aca65553c')

    depends_on('r@2.9.0:', type=('build', 'run'))
    depends_on('libpng')
