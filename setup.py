# Lint as: python2, python3
# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Setup configuration for the python dsrf modules."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import distutils.spawn
import os
import subprocess
import sys

from setuptools import find_packages
from setuptools import findall
from setuptools import setup
from setuptools.command.build_py import build_py
import six


def _find_protoc_path():
  """Verifies whether the protocol buffer compiler is installed."""
  if 'PROTOC' in os.environ and os.path.exists(os.environ['PROTOC']):
    protoc_path = os.environ['PROTOC']
  else:
    protoc_path = distutils.spawn.find_executable('protoc')

  if protoc_path is None:
    sys.stderr.write(
        'protoc not found. Is protobuf-compiler installed? \n'
        'Please visit https://developers.google.com/protocol-buffers/ for '
        'instructions.')
    sys.exit(-1)
  return protoc_path


def _generate_proto(source):
  """Invoke Protocol Compiler to generate python from given source .proto."""
  if not os.path.exists(source):
    sys.stderr.write('Cannot find required file: %s' % source)
    sys.exit(1)

  output_path = source.replace('.proto', '_pb2.py')
  if os.path.exists(output_path) and (
      os.path.getmtime(source) < os.path.getmtime(output_path)):
    # Proto files were generated since the source was last changed.
    return

  protoc = _find_protoc_path()
  proto_dir = os.path.dirname(source)
  protoc_command = [protoc,
                    '-I=%s' % proto_dir, '--python_out=%s' % proto_dir, source]
  sys.stdout.write('Running command: %s' % ' '.join(protoc_command))
  if subprocess.call(protoc_command) != 0:
    sys.stderr.write(
        'Error encountered while compiling proto file: %s\n'
        % source)
    sys.exit(1)


class MyBuild(build_py):
  """Custom build class that will compile the protobufs first."""

  def run(self):
    base_dir = os.path.dirname(os.path.join(os.path.realpath(__file__)))
    sys.stdout.write('Base dir: %s\n' % base_dir)
    proto_dir = os.path.join(base_dir, 'proto/')
    proto_files = [os.path.join(proto_dir, f)
                   for f in os.listdir(proto_dir)
                   if f.endswith('.proto')]
    for proto_file in proto_files:
      sys.stdout.write('Generating proto: %s\n' % proto_file)
      _generate_proto(proto_file)
    build_py.run(self)


def _find_data_files():
  """Traverses the schema directory to identify all XSDs.

  Returns:
    A list of (target_directory: [files_list]) tuples.
  """
  data_files = collections.defaultdict(list)
  for filepath in findall('schemas'):
    if not six.ensure_str(filepath).endswith('.xsd'):
      continue
    directory, unused_filename = os.path.split(filepath)
    data_files[os.path.join('dsrf', directory)].append(filepath)
  return [(k, v) for k, v in six.iteritems(data_files)]


def _find_dsrf_packages():
  """Traverses the source tree to find the packages.

  A package is a directory containing the file __init__.py.

  Returns:
    A list of package names
  """
  packages = ['dsrf']
  for package in find_packages('.'):
    packages.append('dsrf.%s' % package)
  return packages


setup(name='dsrf',
      version='1.1.0d',
      license='Apache 2.0',
      packages=_find_dsrf_packages(),
      description='DSRF Parsing Library',
      author_email='',
      url='https://github.com/ddexnet',
      package_dir={'dsrf': '../dsrf'},
      cmdclass={'build_py': MyBuild},
      data_files=_find_data_files())
