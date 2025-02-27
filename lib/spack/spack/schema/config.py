# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

"""Schema for config.yaml configuration file.

.. literalinclude:: _spack_root/lib/spack/spack/schema/config.py
   :lines: 13-
"""
import six

from llnl.util.lang import union_dicts

import spack.schema.projections

#: Properties for inclusion in other schemas
properties = {
    'config': {
        'type': 'object',
        'default': {},
        'properties': {
            'shared_linking': {
                'type': 'string',
                'enum': ['rpath', 'runpath']
            },
            'install_tree': {
                'anyOf': [
                    {
                        'type': 'object',
                        'properties': union_dicts(
                            {'root': {'type': 'string'}},
                            {'padded_length': {'oneOf': [
                                {'type': 'integer', 'minimum': 0},
                                {'type': 'boolean'}]}},
                            spack.schema.projections.properties,
                        ),
                    },
                    {'type': 'string'}  # deprecated
                ],
            },
            'install_hash_length': {'type': 'integer', 'minimum': 1},
            'install_path_scheme': {'type': 'string'},  # deprecated
            'build_stage': {
                'oneOf': [
                    {'type': 'string'},
                    {'type': 'array',
                     'items': {'type': 'string'}}],
            },
            'test_stage': {'type': 'string'},
            'extensions': {
                'type': 'array',
                'items': {'type': 'string'}
            },
            'template_dirs': {
                'type': 'array',
                'items': {'type': 'string'}
            },
            'module_roots': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'tcl': {'type': 'string'},
                    'lmod': {'type': 'string'},
                    'dotkit': {'type': 'string'},
                },
                'deprecatedProperties': {
                    'properties': ['dotkit'],
                    'message': 'specifying a "dotkit" module root has no '
                               'effect [support for "dotkit" has been '
                               'dropped in v0.13.0]',
                    'error': False
                },
            },
            'source_cache': {'type': 'string'},
            'misc_cache': {'type': 'string'},
            'connect_timeout': {'type': 'integer', 'minimum': 0},
            'verify_ssl': {'type': 'boolean'},
            'suppress_gpg_warnings': {'type': 'boolean'},
            'install_missing_compilers': {'type': 'boolean'},
            'debug': {'type': 'boolean'},
            'checksum': {'type': 'boolean'},
            'deprecated': {'type': 'boolean'},
            'locks': {'type': 'boolean'},
            'dirty': {'type': 'boolean'},
            'build_language': {'type': 'string'},
            'build_jobs': {'type': 'integer', 'minimum': 1},
            'ccache': {'type': 'boolean'},
            'concretizer': {
                'type': 'string',
                'enum': ['original', 'clingo']
            },
            'db_lock_timeout': {'type': 'integer', 'minimum': 1},
            'package_lock_timeout': {
                'anyOf': [
                    {'type': 'integer', 'minimum': 1},
                    {'type': 'null'}
                ],
            },
            'allow_sgid': {'type': 'boolean'},
            'binary_index_root': {'type': 'string'},
            'url_fetch_method': {
                'type': 'string',
                'enum': ['urllib', 'curl']
            },
            'additional_external_search_paths': {
                'type': 'array',
                'items': {'type': 'string'}
            }
        },
    },
}


#: Full schema with metadata
schema = {
    '$schema': 'http://json-schema.org/draft-07/schema#',
    'title': 'Spack core configuration file schema',
    'type': 'object',
    'additionalProperties': False,
    'properties': properties,
}


def update(data):
    """Update the data in place to remove deprecated properties.

    Args:
        data (dict): dictionary to be updated

    Returns:
        True if data was changed, False otherwise
    """
    # currently deprecated properties are
    # install_tree: <string>
    # install_path_scheme: <string>
    # updated: install_tree: {root: <string>,
    #                         projections: <projections_dict}
    # root replaces install_tree, projections replace install_path_scheme
    changed = False

    install_tree = data.get('install_tree', None)
    if isinstance(install_tree, six.string_types):
        # deprecated short-form install tree
        # add value as `root` in updated install_tree
        data['install_tree'] = {'root': install_tree}
        changed = True

    install_path_scheme = data.pop('install_path_scheme', None)
    if install_path_scheme:
        projections_data = {
            'projections': {
                'all': install_path_scheme
            }
        }

        # update projections with install_scheme
        # whether install_tree was updated or not
        # we merge the yaml to ensure we don't invalidate other projections
        update_data = data.get('install_tree', {})
        update_data = spack.config.merge_yaml(update_data, projections_data)
        data['install_tree'] = update_data
        changed = True

    use_curl = data.pop('use_curl', None)
    if use_curl is not None:
        data['url_fetch_method'] = 'curl' if use_curl else 'urllib'
        changed = True

    return changed
