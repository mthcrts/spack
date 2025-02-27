# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import argparse
import os

import pytest

import spack.cmd.create
import spack.util.editor
from spack.main import SpackCommand
from spack.url import UndetectableNameError

create = SpackCommand('create')


@pytest.fixture(scope='module')
def parser():
    """Returns the parser for the module"""
    prs = argparse.ArgumentParser()
    spack.cmd.create.setup_parser(prs)
    return prs


@pytest.mark.parametrize('args,name,expected', [
    # Basic package cases
    (['test-package'], 'test-package',
     [r'TestPackage(Package)', r'def install(self']),
    (['-n', 'test-named-package', 'file://example.tar.gz'],
     'test-named-package',
     [r'TestNamedPackage(Package)', r'def install(self']),
    (['file://example.tar.gz'], 'example',
     [r'Example(Package)', r'def install(self']),

    # Template-specific cases
    (['-t', 'autoreconf', 'test-autoreconf'], 'test-autoreconf',
     [r'TestAutoreconf(AutotoolsPackage)', r"depends_on('autoconf",
      r'def autoreconf(self', r'def configure_args(self']),
    (['-t', 'autotools', 'test-autotools'], 'test-autotools',
     [r'TestAutotools(AutotoolsPackage)', r'def configure_args(self']),
    (['-t', 'bazel', 'test-bazel'], 'test-bazel',
     [r'TestBazel(Package)', r"depends_on('bazel", r'bazel()']),
    (['-t', 'bundle', 'test-bundle'], 'test-bundle',
     [r'TestBundle(BundlePackage)']),
    (['-t', 'cmake', 'test-cmake'], 'test-cmake',
     [r'TestCmake(CMakePackage)', r'def cmake_args(self']),
    (['-t', 'intel', 'test-intel'], 'test-intel',
     [r'TestIntel(IntelPackage)', r'setup_environment']),
    (['-t', 'makefile', 'test-makefile'], 'test-makefile',
     [r'TestMakefile(MakefilePackage)', r'def edit(self', r'makefile']),
    (['-t', 'meson', 'test-meson'], 'test-meson',
     [r'TestMeson(MesonPackage)', r'def meson_args(self']),
    (['-t', 'octave', 'test-octave'], 'octave-test-octave',
     [r'OctaveTestOctave(OctavePackage)', r"extends('octave",
      r"depends_on('octave"]),
    (['-t', 'perlbuild', 'test-perlbuild'], 'perl-test-perlbuild',
     [r'PerlTestPerlbuild(PerlPackage)', r"depends_on('perl-module-build",
      r'def configure_args(self']),
    (['-t', 'perlmake', 'test-perlmake'], 'perl-test-perlmake',
     [r'PerlTestPerlmake(PerlPackage)', r"depends_on('perl-",
      r'def configure_args(self']),
    (['-t', 'python', 'test-python'], 'py-test-python',
     [r'PyTestPython(PythonPackage)', r"depends_on('py-",
      r'def global_options(self', r'def install_options(self']),
    (['-t', 'qmake', 'test-qmake'], 'test-qmake',
     [r'TestQmake(QMakePackage)', r'def qmake_args(self']),
    (['-t', 'r', 'test-r'], 'r-test-r',
     [r'RTestR(RPackage)', r"depends_on('r-", r'def configure_args(self']),
    (['-t', 'scons', 'test-scons'], 'test-scons',
     [r'TestScons(SConsPackage)', r'def build_args(self']),
    (['-t', 'sip', 'test-sip'], 'py-test-sip',
     [r'PyTestSip(SIPPackage)', r'def configure_args(self']),
    (['-t', 'waf', 'test-waf'], 'test-waf',
     [r'TestWaf(WafPackage)', r'configure_args()'])
])
def test_create_template(parser, mock_test_repo, args, name, expected):
    """Test template creation."""
    repo, repodir = mock_test_repo

    constr_args = parser.parse_args(['--skip-editor'] + args)
    spack.cmd.create.create(parser, constr_args)

    filename = repo.filename_for_package_name(name)
    assert os.path.exists(filename)

    with open(filename, 'r') as package_file:
        content = ' '.join(package_file.readlines())
        for entry in expected:
            assert entry in content


@pytest.mark.parametrize('name,expected', [
    (' ', 'name must be provided'),
    ('bad#name', 'name can only contain'),
])
def test_create_template_bad_name(
        parser, mock_test_repo, name, expected, capsys):
    """Test template creation with bad name options."""
    constr_args = parser.parse_args(['--skip-editor', '-n', name])
    with pytest.raises(SystemExit):
        spack.cmd.create.create(parser, constr_args)

    captured = capsys.readouterr()
    assert expected in str(captured)


def test_build_system_guesser_no_stage(parser):
    """Test build system guesser when stage not provided."""
    guesser = spack.cmd.create.BuildSystemGuesser()

    # Ensure get the expected build system
    with pytest.raises(AttributeError,
                       match="'NoneType' object has no attribute"):
        guesser(None, '/the/url/does/not/matter')


def test_build_system_guesser_octave(parser):
    """
    Test build system guesser for the special case, where the same base URL
    identifies the build system rather than guessing the build system from
    files contained in the archive.
    """
    url, expected = 'downloads.sourceforge.net/octave/', 'octave'
    guesser = spack.cmd.create.BuildSystemGuesser()

    # Ensure get the expected build system
    guesser(None, url)
    assert guesser.build_system == expected

    # Also ensure get the correct template
    args = parser.parse_args([url])
    bs = spack.cmd.create.get_build_system(args, guesser)
    assert bs == expected


@pytest.mark.parametrize('url,expected', [
    ('testname', 'testname'),
    ('file://example.com/archive.tar.gz', 'archive'),
])
def test_get_name_urls(parser, url, expected):
    """Test get_name with different URLs."""
    args = parser.parse_args([url])
    name = spack.cmd.create.get_name(args)
    assert name == expected


def test_get_name_error(parser, monkeypatch, capsys):
    """Test get_name UndetectableNameError exception path."""
    def _parse_name_offset(path, v):
        raise UndetectableNameError(path)

    monkeypatch.setattr(spack.url, 'parse_name_offset', _parse_name_offset)

    url = 'downloads.sourceforge.net/noapp/'
    args = parser.parse_args([url])

    with pytest.raises(SystemExit):
        spack.cmd.create.get_name(args)
    captured = capsys.readouterr()
    assert "Couldn't guess a name" in str(captured)
