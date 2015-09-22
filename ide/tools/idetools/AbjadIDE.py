# -*- coding: utf-8 -*-
from __future__ import print_function
import codecs
import datetime
import glob
import inspect
import os
import shutil
import sys
import time
from abjad.tools import datastructuretools
from abjad.tools import lilypondfiletools
from abjad.tools import mathtools
from abjad.tools import sequencetools
from abjad.tools import stringtools
from abjad.tools import systemtools
from ide.tools.idetools.AbjadIDEConfiguration import AbjadIDEConfiguration
from ide.tools.idetools.Command import Command
configuration = AbjadIDEConfiguration()


class AbjadIDE(object):
    r'''Abjad IDE.
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_io_manager',
        '_session',
        )

    _abjad_import_statement = 'from abjad import *'

    _secondary_names = (
        '__init__.py',
        '__metadata__.py',
        '__views__.py',
        '__abbreviations__.py',
        )

    _tab = 4 * ' '

    _unicode_directive = '# -*- coding: utf-8 -*-'

    ### INITIALIZER ###

    def __init__(self, session=None, is_test=False):
        from ide.tools import idetools
        if session is None:
            session = idetools.Session()
            session._is_test = is_test
        self._session = session
        io_manager = idetools.IOManager(session=session)
        self._io_manager = io_manager

    ### SPECIAL METHODS ###

    def __repr__(self):
        r'''Gets interpreter representation of asset controller.

        Returns string.
        '''
        return '{}()'.format(type(self).__name__)

    ### PRIVATE PROPERTIES ###

    @property
    def _command_name_to_command(self):
        result = {}
        methods = self._get_commands()
        for method in methods:
            result[method.command_name] = method
        return result

    ### PRIVATE METHODS ###

    def _add_metadatum(self, directory, metadatum_name, metadatum_value):
        assert os.path.isdir(directory)
        assert ' ' not in metadatum_name, repr(metadatum_name)
        metadata = self._get_metadata(directory)
        metadata[metadatum_name] = metadatum_value
        self._write_metadata_py(directory, metadata)

    def _call_lilypond_on_file_ending_with(self, directory, string):
        file_path = self._get_file_path_ending_with(directory, string)
        if file_path:
            self._io_manager.run_lilypond(file_path)
        else:
            message = 'file ending in {!r} not found.'
            message = message.format(string)
            self._io_manager._display(message)

    def _clear_view(self, directory):
        assert os.path.isdir(directory), repr(directory)
        self._add_metadatum(directory, 'view_name', None)

    def _coerce_name(self, directory, name):
        dash_case_prototype = ('build', 'distribution', 'etc')
        package_prototype = ('scores', 'materials', 'segments')
        if self._is_score_directory(directory, 'scores'):
            name = self._to_package_name(name)
        elif self._is_score_directory(directory, dash_case_prototype):
            name = self._to_dash_case_file_name(name)
        elif self._is_score_directory(directory, 'makers'):
            name = self._to_classfile_name(name)
        elif self._is_score_directory(directory, package_prototype):
            name = self._to_package_name(name)
        elif self._is_score_directory(directory, 'stylesheets'):
            name = self._to_stylesheet_name(name)
        elif self._is_score_directory(directory, 'test'):
            name = self._to_test_file_name(name)
        else:
            raise ValueError(directory)
        return name

    def _collect_similar_directories(self, directory, example_scores=False):
        assert os.path.isdir(directory), repr(directory)
        directories = []
        scores_directories = [configuration.composer_scores_directory]
        if example_scores:
            scores_directory = configuration.abjad_ide_example_scores_directory
            scores_directories.append(scores_directory)
        if self._is_score_directory(directory, 'scores'):
            return scores_directories
        score_directories = []
        for scores_directory in scores_directories:
            for name in os.listdir(scores_directory):
                if not name[0].isalpha():
                    continue
                score_directory = os.path.join(scores_directory, name)
                if not os.path.isdir(score_directory):
                    continue
                score_directories.append(score_directory)
        if self._is_score_directory(directory, 'outer'):
            return score_directories
        outer_score_directories = score_directories
        score_directories = []
        for outer_score_directory in outer_score_directories:
            base_name = os.path.basename(outer_score_directory)
            score_directory = os.path.join(
                outer_score_directory,
                base_name,
                )
            if not os.path.isdir(score_directory):
                continue
            score_directories.append(score_directory)
        if self._is_score_directory(directory, ('inner', 'score')):
            return score_directories
        if self._is_score_directory(directory, ('material', 'segment')):
            directories = []
            parent_directory = os.path.dirname(directory)
            parent_directories = self._collect_similar_directories(
                parent_directory,
                example_scores=example_scores,
                )
            for parent_directory in parent_directories:
                for name in os.listdir(parent_directory):
                    if not name[0].isalpha():
                        continue
                    directory_ = os.path.join(parent_directory, name)
                    if not os.path.isdir(directory_):
                        continue
                    directories.append(directory_)
            return directories
        base_name = os.path.basename(directory)
        for score_directory in score_directories:
            directory_ = os.path.join(score_directory, base_name)
            if os.path.isdir(directory_):
                directories.append(directory_)
        return directories

    def _confirm_segment_names(self, score_directory):
        segments_directory = os.path.join(score_directory, 'segments')
        view_name = self._read_view_name(segments_directory)
        view_inventory = self._read_view_inventory(segments_directory)
        if not view_inventory or view_name not in view_inventory:
            view_name = None
        segment_paths = self._list_visible_paths(segments_directory)
        segment_paths = segment_paths or []
        segment_names = []
        for segment_path in segment_paths:
            segment_name = os.path.basename(segment_path)
            segment_names.append(segment_name)
        messages = []
        if view_name:
            message = 'the {!r} segment view is currently selected.'
            message = message.format(view_name)
            messages.append(message)
        if segment_names:
            message = 'will assemble segments in this order:'
            messages.append(message)
            for segment_name in segment_names:
                message = '    ' + segment_name
                messages.append(message)
        else:
            message = 'no segments found:'
            message += ' will generate source without segments.'
            messages.append(message)
        self._io_manager._display(messages)
        result = self._io_manager._confirm()
        if not result:
            return False
        return segment_names

    def _copy_boilerplate(
        self,
        source_file_name,
        destination_directory,
        candidacy=True,
        replacements=None,
        ):
        replacements = replacements or {}
        source_path = os.path.join(
            configuration.abjad_ide_boilerplate_directory,
            source_file_name,
            )
        destination_path = os.path.join(
            destination_directory,
            source_file_name,
            )
        base_name, file_extension = os.path.splitext(source_file_name)
        candidate_name = base_name + '.candidate' + file_extension
        candidate_path = os.path.join(
            destination_directory,
            candidate_name,
            )
        messages = []
        with systemtools.FilesystemState(remove=[candidate_path]):
            shutil.copyfile(source_path, candidate_path)
            for old in replacements:
                new = replacements[old]
                self._replace_in_file(candidate_path, old, new)
            if not os.path.exists(destination_path):
                shutil.copyfile(candidate_path, destination_path)
                message = 'wrote {}.'.format(destination_path)
                messages.append(message)
            elif not candidacy:
                message = 'overwrite {}?'
                message = message.format(destination_path)
                result = self._io_manager._confirm(message)
                if not result:
                    return False
                shutil.copyfile(candidate_path, destination_path)
                message = 'overwrote {}.'.format(destination_path)
                messages.append(message)
            elif systemtools.TestManager.compare_files(
                candidate_path,
                destination_path,
                ):
                messages_ = self._make_candidate_messages(
                    True,
                    candidate_path,
                    destination_path,
                    )
                messages.extend(messages_)
                message = 'preserved {}.'.format(destination_path)
                messages.append(message)
            else:
                shutil.copyfile(candidate_path, destination_path)
                message = 'overwrote {}.'.format(destination_path)
                messages.append(message)
            self._io_manager._display(messages)
            return True

    def _directory_to_asset_identifier(self, directory):
        assert os.path.isdir(directory), repr(directory)
        file_prototype = (
            'build',
            'distribution',
            'etc',
            'makers',
            'material',
            'segment',
            'stylesheets',
            'test',
            )
        package_prototype = (
            'materials',
            'segments',
            )
        if self._is_score_directory(directory, 'scores'):
            return 'package'
        elif self._is_score_directory(directory, file_prototype):
            return 'file'
        elif self._is_score_directory(directory, package_prototype):
            return 'package'
        else:
            raise ValueError(directory)

    def _directory_to_file_extension(self, directory):
        file_extension = ''
        if self._is_score_directory(directory, 'makers'):
            file_extension = '.py'
        elif self._is_score_directory(directory, 'stylesheets'):
            file_extension = '.ily'
        elif self._is_score_directory(directory, 'test'):
            file_extension = '.py'
        return file_extension

    def _directory_to_name_predicate(self, directory):
        file_prototype = ('build', 'distribution', 'etc')
        package_prototype = ('materials', 'segments', 'scores')
        if self._is_score_directory(directory, 'scores'):
            return self._is_package_name
        elif self._is_score_directory(directory, ('score', 'inner')):
            return self._is_package_name
        elif self._is_score_directory(directory, file_prototype):
            return self._is_dash_case_file_name
        elif self._is_score_directory(directory, 'makers'):
            return self._is_classfile_name
        elif self._is_score_directory(directory, package_prototype):
            return self._is_package_name
        elif self._is_score_directory(directory, ('material', 'segment')):
            return self._is_module_file_name
        elif self._is_score_directory(directory, 'stylesheets'):
            return self._is_stylesheet_name
        elif self._is_score_directory(directory, 'test'):
            return stringtools.is_snake_case
        else:
            raise ValueError(directory)

    def _directory_to_package_contents(self, directory):
        if self._is_score_directory(directory, 'material'):
            return {
                'optional_directories': (
                    '__pycache__',
                    ),
                'optional_files': (
                    '__illustrate__.py',
                    'illustration.ly',
                    'illustration.pdf',
                    ),
                'required_directories': (),
                'required_files': (
                    '__init__.py',
                    '__metadata__.py',
                    'definition.py',
                    ),
                }
        elif self._is_score_directory(directory, 'inner'):
            return {
                'optional_directories': (
                    '__pycache__',
                    ),
                'optional_files': (),
                'required_directories': (
                    'build',
                    'distribution',
                    'etc',
                    'makers',
                    'materials',
                    'segments',
                    'stylesheets',
                    'test',
                    ),
                'required_files': (
                    '__init__.py',
                    '__metadata__.py',
                    os.path.join('makers', '__init__.py'),
                    os.path.join('materials', '__abbreviations__.py'),
                    os.path.join('materials', '__init__.py'),
                    os.path.join('segments', '__init__.py'),
                    os.path.join('segments', '__metadata__.py'),
                    os.path.join('segments', '__views__.py'),
                    ),
                }
        elif self._is_score_directory(directory, 'segment'):
            return {
                'optional_directories': (
                    '__pycache__',
                    ),
                'optional_files': (
                    'illustration.ly',
                    'illustration.pdf',
                    ),
                'required_directories': (),
                'required_files': (
                    '__init__.py',
                    '__metadata__.py',
                    'definition.py',
                    ),
                }
        else:
            raise ValueError(directory)

    def _filter_by_view(self, directory, entries):
        assert os.path.isdir(directory), repr(directory)
        view = self._read_view(directory)
        if view is None:
            return entries
        entries = entries[:]
        filtered_entries = []
        for pattern in view:
            if ':ds:' in pattern:
                for entry in entries:
                    if self._match_display_string_view_pattern(pattern, entry):
                        filtered_entries.append(entry)
            elif 'md:' in pattern:
                for entry in entries:
                    if self._match_metadata_view_pattern(pattern, entry):
                        filtered_entries.append(entry)
            elif ':path:' in pattern:
                for entry in entries:
                    if self._match_path_view_pattern(pattern, entry):
                        filtered_entries.append(entry)
            else:
                for entry in entries:
                    display_string, _, _, path = entry
                    if pattern == display_string:
                        filtered_entries.append(entry)
        return filtered_entries

    @staticmethod
    def _find_first_file_name(directory):
        for entry in sorted(os.listdir(directory)):
            if not entry.startswith('.'):
                path = os.path.join(directory, entry)
                if (os.path.isfile(path) and not '__init__.py' in path):
                    return entry

    @staticmethod
    def _format_messaging(inputs, outputs, verb='interpret'):
        messages = []
        if not inputs and not outputs:
            message = 'no files to {}.'
            message = message.format(verb)
            messages.append(message)
            return messages
        message = 'will {} ...'.format(verb)
        messages.append(message)
        if outputs:
            input_label = '  INPUT: '
        else:
            input_label = '    '
        output_label = ' OUTPUT: '
        if not outputs:
            for path_list in inputs:
                if isinstance(path_list, str):
                    path_list = [path_list]
                for path in path_list:
                    messages.append('{}{}'.format(input_label, path))
        else:
            for inputs_, outputs_ in zip(inputs, outputs):
                if isinstance(inputs_, str):
                    inputs_ = [inputs_]
                assert isinstance(inputs_, (tuple, list)), repr(inputs_)
                for path_list in inputs_:
                    if isinstance(path_list, str):
                        path_list = [path_list]
                    for path in path_list:
                        messages.append('{}{}'.format(input_label, path))
                for path_list in outputs_:
                    if isinstance(path_list, str):
                        path_list = [path_list]
                    for path in path_list:
                        messages.append('{}{}'.format(output_label, path))
                messages.append('')
        return messages

    def _gather_segment_files(self, score_directory, file_name):
        segments_directory = os.path.join(score_directory, 'segments')
        build_directory = os.path.join(score_directory, 'build')
        directory_entries = sorted(os.listdir(segments_directory))
        source_file_paths, target_file_paths = [], []
        _, file_extension = os.path.splitext(file_name)
        for directory_entry in directory_entries:
            segment_directory = os.path.join(
                segments_directory,
                directory_entry,
                )
            if not os.path.isdir(segment_directory):
                continue
            source_file_path = os.path.join(
                segment_directory,
                file_name,
                )
            if not os.path.isfile(source_file_path):
                continue
            score_package = os.path.basename(score_directory)
            score_name = score_package.replace('_', '-')
            directory_entry = directory_entry.replace('_', '-')
            target_file_name = directory_entry + file_extension
            target_file_path = os.path.join(
                build_directory,
                target_file_name,
                )
            source_file_paths.append(source_file_path)
            target_file_paths.append(target_file_path)
        if source_file_paths:
            messages = []
            messages.append('will copy ...')
            pairs = zip(source_file_paths, target_file_paths)
            for source_file_path, target_file_path in pairs:
                message = ' FROM: {}'.format(source_file_path)
                messages.append(message)
                message = '   TO: {}'.format(target_file_path)
                messages.append(message)
            self._io_manager._display(messages)
            if not self._io_manager._confirm():
                return
        if not os.path.exists(build_directory):
            os.mkdir(build_directory)
        pairs = zip(source_file_paths, target_file_paths)
        return pairs

    def _get_added_asset_paths(self, path):
        paths = []
        git_status_lines = self._get_git_status_lines(path)
        for line in git_status_lines:
            line = str(line)
            if line.startswith('A'):
                path = line.strip('A')
                path = path.strip()
                root_directory = self._get_repository_root_directory(path)
                path = os.path.join(root_directory, path)
                paths.append(path)
        return paths

    def _get_available_path_in_directory(self, directory):
        asset_identifier = self._directory_to_asset_identifier(directory)
        while True:
            default_prompt = 'enter {} name'
            default_prompt = default_prompt.format(asset_identifier)
            getter = self._io_manager._make_getter()
            getter.append_string(default_prompt)
            name = getter._run(io_manager=self._io_manager)
            if not name:
                return
            name = stringtools.strip_diacritics(name)
            words = stringtools.delimit_words(name)
            words = [_.lower() for _ in words]
            name = '_'.join(words)
            if not stringtools.is_snake_case_package_name(name):
                continue
            path = os.path.join(directory, name)
            if os.path.exists(path):
                line = 'path already exists: {!r}.'
                line = line.format(path)
                self._io_manager._display(line)
            else:
                return path

    def _get_commands(self):
        result = []
        for name in dir(self):
            if name.startswith('_'):
                continue
            command = getattr(self, name)
            if not inspect.ismethod(command):
                continue
            result.append(command)
        return result

    def _get_file_path_ending_with(self, directory, string):
        if not os.path.isdir(directory):
            return
        for name in os.listdir(directory):
            if name.endswith(string):
                path = os.path.join(directory, name)
                if os.path.isfile(path):
                    return path

    def _get_git_status_lines(self, directory):
        command = 'git status --porcelain {}'
        command = command.format(directory)
        with systemtools.TemporaryDirectoryChange(directory=directory):
            process = self._io_manager.make_subprocess(command)
        stdout_lines = self._io_manager._read_from_pipe(process.stdout)
        stdout_lines = stdout_lines.splitlines()
        return stdout_lines

    def _get_metadata(self, directory):
        assert os.path.isdir(directory), repr(directory)
        metadata_py_path = os.path.join(
            directory,
            '__metadata__.py',
            )
        metadata = None
        if os.path.isfile(metadata_py_path):
            with open(metadata_py_path, 'r') as file_pointer:
                file_contents_string = file_pointer.read()
            try:
                result = self._io_manager.execute_string(
                    file_contents_string,
                    attribute_names=('metadata',),
                    )
                metadata = result[0]
            except SyntaxError:
                message = 'can not interpret metadata py: {!r}.'
                message = message.format(metadata_py_path)
                self._io_manager._display(message)
        metadata = metadata or datastructuretools.TypedOrderedDict()
        return metadata

    def _get_metadatum(self, directory, metadatum_name, default=None):
        assert os.path.isdir(directory), repr(directory)
        metadata = self._get_metadata(directory)
        metadatum = metadata.get(metadatum_name)
        if not metadatum:
            metadatum = default
        return metadatum

    def _get_modified_asset_paths(self, path):
        paths = []
        git_status_lines = self._get_git_status_lines(path)
        for line in git_status_lines:
            line = str(line)
            if line.startswith(('M', ' M')):
                path = line.strip('M ')
                path = path.strip()
                root_directory = self._get_repository_root_directory(path)
                path = os.path.join(root_directory, path)
                paths.append(path)
        return paths

    def _get_name_metadatum(self, directory):
        assert os.path.isdir(directory), repr(directory)
        name = self._get_metadatum(directory, 'name')
        if not name:
            name = os.path.basename(directory)
            name = name.replace('_', ' ')
        return name

    def _get_previous_segment_path(self, directory):
        segments_directory = self._to_score_directory(
            directory,
            'segments',
            )
        paths = self._list_visible_paths(segments_directory)
        for i, path in enumerate(paths):
            if path == directory:
                break
        else:
            message = 'can not find segment package path.'
            raise Exception(message)
        current_path_index = i
        if current_path_index == 0:
            return
        previous_path_index = current_path_index - 1
        previous_path = paths[previous_path_index]
        return previous_path

    def _get_repository_root_directory(self, path):
        command = 'git rev-parse --show-toplevel'
        with systemtools.TemporaryDirectoryChange(directory=path):
            process = self._io_manager.make_subprocess(command)
        line = self._io_manager._read_one_line_from_pipe(process.stdout)
        return line

    def _get_title_metadatum(self, score_directory, year=True):
        if year and self._get_metadatum(score_directory, 'year'):
            result = '{} ({})'
            result = result.format(
                self._get_title_metadatum(score_directory, year=False),
                self._get_metadatum(score_directory, 'year')
                )
            return result
        else:
            result = self._get_metadatum(score_directory, 'title')
            result = result or '(untitled score)'
            return result

    def _get_unadded_asset_paths(self, path):
        paths = []
        root_directory = self._get_repository_root_directory(path)
        git_status_lines = self._get_git_status_lines(path)
        for line in git_status_lines:
            line = str(line)
            if line.startswith('?'):
                path = line.strip('?')
                path = path.strip()
                path = os.path.join(root_directory, path)
                paths.append(path)
        return paths

    @staticmethod
    def _get_views_py_path(directory):
        assert os.path.isdir(directory), repr(directory)
        return os.path.join(directory, '__views__.py')

    def _git_add(self, path, dry_run=False):
        change = systemtools.TemporaryDirectoryChange(directory=path)
        with change:
            inputs = self._get_unadded_asset_paths(path)
            outputs = []
            if dry_run:
                return inputs, outputs
            if not inputs:
                message = 'nothing to add.'
                self._io_manager._display(message)
                return
            messages = []
            messages.append('will add ...')
            for path in inputs:
                messages.append(self._tab + path)
            self._io_manager._display(messages)
            result = self._io_manager._confirm()
            if not result:
                return
            command = 'git add -A {}'
            command = command.format(path)
            assert isinstance(command, str)
            self._io_manager.run_command(command)

    def _git_commit(self, path, commit_message=None):
        change = systemtools.TemporaryDirectoryChange(directory=path)
        with change:
            self._io_manager._session._attempted_method = '_git_commit'
            if self._io_manager._session.is_test:
                return
            if commit_message is None:
                getter = self._io_manager._make_getter()
                getter.append_string('commit message')
                commit_message = getter._run(io_manager=self._io_manager)
                if commit_message is None:
                    return
                message = 'commit message will be: "{}"'
                message = message.format(commit_message)
                self._io_manager._display(message)
                result = self._io_manager._confirm()
                if not result:
                    return
            message = path
            path = configuration.abjad_ide_example_scores_directory
            message = message.replace(path, '')
            path = configuration.composer_scores_directory
            message = message.replace(path, '')
            message = message.lstrip(os.path.sep)
            message = message + ' ...'
            command = 'git commit -m "{}" {}; git push'
            command = command.format(commit_message, path)
            self._io_manager.run_command(command, capitalize=False)

    def _git_revert(self, path):
        change = systemtools.TemporaryDirectoryChange(directory=path)
        with change:
            self._io_manager._session._attempted_method = '_git_revert'
            if self._io_manager._session.is_test:
                return
            paths = []
            paths.extend(self._get_added_asset_paths(path))
            paths.extend(self._get_modified_asset_paths(path))
            messages = []
            messages.append('will revert ...')
            for path in paths:
                messages.append(self._tab + path)
            self._io_manager._display(messages)
            result = self._io_manager._confirm()
            if not result:
                return
            commands = []
            for path in paths:
                command = 'git checkout {}'.format(path)
                commands.append(command)
            command = ' && '.join(commands)
            with systemtools.TemporaryDirectoryChange(directory=path):
                self._io_manager.spawn_subprocess(command)

    def _git_status(self, path):
        change = systemtools.TemporaryDirectoryChange(directory=path)
        with change:
            command = 'git status {}'.format(path)
            messages = []
            self._io_manager._session._attempted_method = '_git_status'
            message = 'Repository status for {} ...'
            message = message.format(path)
            messages.append(message)
            with systemtools.TemporaryDirectoryChange(directory=path):
                process = self._io_manager.make_subprocess(command)
            path_ = path + os.path.sep
            clean_lines = []
            stdout_lines = self._io_manager._read_from_pipe(process.stdout)
            for line in stdout_lines.splitlines():
                line = str(line)
                clean_line = line.strip()
                clean_line = clean_line.replace(path_, '')
                clean_lines.append(clean_line)
            everything_ok = False
            for line in clean_lines:
                if 'nothing to commit' in line:
                    everything_ok = True
                    break
            if clean_lines and not everything_ok:
                messages.extend(clean_lines)
            else:
                first_message = messages[0]
                first_message = first_message + ' OK'
                messages[0] = first_message
                clean_lines.append(message)
            self._io_manager._display(messages, capitalize=False)

    def _git_update(self, path, messages_only=False):
        messages = []
        change = systemtools.TemporaryDirectoryChange(directory=path)
        with change:
            if self._io_manager._session.is_test:
                return messages
            root_directory = self._get_repository_root_directory(path)
            command = 'git pull {}'
            command = command.format(root_directory)
            messages = self._io_manager.run_command(
                command,
                messages_only=True,
                )
        if messages and messages[-1].startswith('At revision'):
            messages = messages[-1:]
        elif messages and 'Already up-to-date' in messages[-1]:
            messages = messages[-1:]
        if messages_only:
            return messages
        self._io_manager._display(messages)

    def _handle_candidate(self, candidate_path, destination_path):
        messages = []
        if not os.path.exists(destination_path):
            shutil.copyfile(candidate_path, destination_path)
            message = 'wrote {}.'.format(destination_path)
            messages.append(message)
        elif systemtools.TestManager.compare_files(
            candidate_path,
            destination_path,
            ):
            messages_ = self._make_candidate_messages(
                True,
                candidate_path,
                destination_path,
                )
            messages.extend(messages_)
            message = 'preserved {}.'.format(destination_path)
            messages.append(message)
        else:
            shutil.copyfile(candidate_path, destination_path)
            message = 'overwrote {}.'.format(destination_path)
            messages.append(message)
        self._io_manager._display(messages)

    def _handle_input(self, result):
        assert isinstance(result, str), repr(result)
        if result == '<return>':
            return
        package_prototype = ('inner', 'material', 'segment')
        if result.startswith('!'):
            statement = result[1:]
            self._io_manager._invoke_shell(statement)
        elif result in self._command_name_to_command:
            command = self._command_name_to_command[result]
            if command.argument_name == 'current_directory':
                current_directory = self._session.manifest_current_directory
                command(current_directory)
            else:
                command()
        elif (result.endswith('!') and
            result[:-1] in self._command_name_to_command):
            result = result[:-1]
            self._command_name_to_command[result]()
        elif os.path.isfile(result):
            self._io_manager.open_file(result)
        elif self._is_score_directory(result, package_prototype):
            self._manage_directory(result)
        elif self._is_score_directory(result):
            self._manage_directory(result)
        else:
            current_score_directory = self._session.current_score_directory
            aliased_path = configuration.aliases.get(result, None)
            if current_score_directory and aliased_path:
                aliased_path = os.path.join(
                    current_score_directory,
                    aliased_path,
                    )
                if os.path.isfile(aliased_path):
                    self._io_manager.open_file(aliased_path)
                else:
                    message = 'file does not exist: {}.'
                    message = message.format(aliased_path)
                    self._io_manager._display(message)
            else:
                message = 'unknown command: {!r}.'
                message = message.format(result)
                self._io_manager._display([message, ''])

    def _interpret_file_ending_with(self, directory, string):
        r'''Typesets TeX file.
        Calls ``pdflatex`` on file TWICE.
        Some LaTeX packages like ``tikz`` require two passes.
        '''
        assert os.path.isdir(directory), repr(directory)
        directory_path = directory
        file_path = self._get_file_path_ending_with(directory_path, string)
        if not file_path:
            message = 'file ending in {!r} not found.'
            message = message.format(string)
            self._io_manager._display(message)
            return
        input_directory = os.path.dirname(file_path)
        output_directory = input_directory
        basename = os.path.basename(file_path)
        input_file_name_stem, file_extension = os.path.splitext(basename)
        job_name = '{}.candidate'.format(input_file_name_stem)
        candidate_name = '{}.candidate.pdf'.format(input_file_name_stem)
        candidate_path = os.path.join(output_directory, candidate_name)
        destination_name = '{}.pdf'.format(input_file_name_stem)
        destination_path = os.path.join(output_directory, destination_name)
        command = 'pdflatex --jobname={} -output-directory={} {}/{}.tex'
        command = command.format(
            job_name,
            output_directory,
            input_directory,
            input_file_name_stem,
            )
        command_called_twice = '{}; {}'.format(command, command)
        filesystem = systemtools.FilesystemState(remove=[candidate_path])
        directory = systemtools.TemporaryDirectoryChange(input_directory)
        with filesystem, directory:
            self._io_manager.spawn_subprocess(command_called_twice)
            for file_name in glob.glob('*.aux'):
                path = os.path.join(output_directory, file_name)
                os.remove(path)
            for file_name in glob.glob('*.aux'):
                path = os.path.join(output_directory, file_name)
                os.remove(path)
            for file_name in glob.glob('*.log'):
                path = os.path.join(output_directory, file_name)
                os.remove(path)
            self._handle_candidate(
                candidate_path,
                destination_path,
                )

    @staticmethod
    def _is_classfile_name(expr):
        if not isinstance(expr, str):
            return False
        file_name, file_extension = os.path.splitext(expr)
        if not stringtools.is_upper_camel_case(file_name):
            return False
        if not file_extension == '.py':
            return False
        return True

    @staticmethod
    def _is_dash_case_file_name(expr):
        if not isinstance(expr, str):
            return False
        if not expr == expr.lower():
            return False
        file_name, file_extension = os.path.splitext(expr)
        if not stringtools.is_dash_case(file_name):
            return False
        if not file_extension:
            return False
        return True

    def _is_git_unknown(self, path):
        if path is None:
            return False
        if not os.path.exists(path):
            return False
        git_status_lines = self._get_git_status_lines(path)
        git_status_lines = git_status_lines or ['']
        first_line = git_status_lines[0]
        if first_line.startswith('?'):
            return True
        return False

    def _is_git_versioned(self, path):
        if not self._is_in_git_repository(path):
            return False
        git_status_lines = self._get_git_status_lines(path)
        git_status_lines = git_status_lines or ['']
        first_line = git_status_lines[0]
        if first_line.startswith('?'):
            return False
        return True

    def _is_in_git_repository(self, path):
        if path is None:
            return False
        if not os.path.exists(path):
            return False
        git_status_lines = self._get_git_status_lines(path)
        git_status_lines = git_status_lines or ['']
        first_line = git_status_lines[0]
        if first_line.startswith('fatal:'):
            return False
        return True

    @staticmethod
    def _is_module_file_name(expr):
        if not isinstance(expr, str):
            return False
        if not expr == expr.lower():
            return False
        file_name, file_extension = os.path.splitext(expr)
        if not stringtools.is_snake_case(file_name):
            return False
        if not file_extension == '.py':
            return False
        return True

    @staticmethod
    def _is_package_name(expr):
        if not isinstance(expr, str):
            return False
        if not expr == expr.lower():
            return False
        if os.path.sep in expr:
            return False
        if not stringtools.is_snake_case(expr):
            return False
        return True

    def _is_score_directory(self, directory, prototype=()):
        if not isinstance(directory, str):
            return False
        if not os.path.isdir(directory):
            return False
        if isinstance(prototype, str):
            prototype = (prototype,)
        assert all(isinstance(_, str) for _ in prototype)
        if 'scores'in prototype:
            if directory == configuration.composer_scores_directory:
                return True
            if directory == configuration.abjad_ide_example_scores_directory:
                return True
        scores_directory = self._to_score_directory(directory, 'scores')
        if 'outer' in prototype and scores_directory:
            scores_directory_parts_count = len(
                scores_directory.split(os.path.sep))
            parts = directory.split(os.path.sep)
            if len(parts) == scores_directory_parts_count + 1:
                return True
        if 'inner' in prototype and scores_directory:
            scores_directory_parts_count = len(
                scores_directory.split(os.path.sep))
            parts = directory.split(os.path.sep)
            if len(parts) == scores_directory_parts_count + 2:
                if parts[-1] == parts[-2]:
                    return True
        parent_directory = os.path.dirname(directory)
        if 'material' in prototype and scores_directory:
            scores_directory_parts_count = len(
                scores_directory.split(os.path.sep))
            parts = directory.split(os.path.sep)
            if len(parts) == scores_directory_parts_count + 4:
                if parts[-2] == 'materials':
                    return True
        if 'segment' in prototype and scores_directory:
            scores_directory_parts_count = len(
                scores_directory.split(os.path.sep))
            parts = directory.split(os.path.sep)
            if len(parts) == scores_directory_parts_count + 4:
                if parts[-2] == 'segments':
                    return True
        base_name = os.path.basename(directory)
        if base_name not in (
            'build',
            'distribution',
            'etc',
            'makers',
            'material',
            'materials',
            'score',
            'scores',
            'segment',
            'segments',
            'stylesheets',
            'test',
            ):
            return False
        if prototype is None or base_name in prototype:
            return True
        return False

    @staticmethod
    def _is_stylesheet_name(expr):
        if not isinstance(expr, str):
            return False
        if not expr == expr.lower():
            return False
        file_name, file_extension = os.path.splitext(expr)
        if not stringtools.is_dash_case(file_name):
            return False
        if not file_extension == '.ily':
            return False
        return True

    @staticmethod
    def _is_test_file_name(expr):
        if not isinstance(expr, str):
            return False
        if not expr.startswith('test_'):
            return False
        file_name, file_extension = os.path.splitext(expr)
        if not stringtools.is_snake_case(file_name):
            return False
        if not file_extension == '.py':
            return False
        return True

    def _is_up_to_date(self, path):
        git_status_lines = self._get_git_status_lines(path)
        git_status_lines = git_status_lines or ['']
        first_line = git_status_lines[0]
        return first_line == ''

    def _list_paths(self, directory, example_scores=True):
        assert os.path.isdir(directory), repr(directory)
        paths = []
        directories = self._collect_similar_directories(
            directory,
            example_scores=example_scores,
            )
        directory_ = directory
        for directory in directories:
            if not directory:
                continue
            if not os.path.exists(directory):
                continue
            name_predicate = self._directory_to_name_predicate(directory)
            entries = sorted(os.listdir(directory))
            for entry in entries:
                if not name_predicate(entry):
                    continue
                path = os.path.join(directory, entry)
                if self._is_score_directory(directory, 'scores'):
                    path = os.path.join(path, entry)
                if not path.startswith(directory_):
                    continue
                paths.append(path)
        return paths

    def _list_secondary_paths(self, directory):
        assert os.path.isdir(directory), repr(directory)
        paths = []
        for name in os.listdir(directory):
            if name in self._secondary_names:
                path = os.path.join(directory, name)
                paths.append(path)
        return paths

    def _list_visible_paths(self, directory):
        assert os.path.isdir(directory), repr(directory)
        paths = self._list_paths(directory)
        strings = [self._to_menu_string(_) for _ in paths]
        entries = []
        pairs = list(zip(strings, paths))
        for string, path in pairs:
            entry = (string, None, None, path)
            entries.append(entry)
        entries = self._filter_by_view(directory, entries)
        if self._is_score_directory(directory, 'scores'):
            if self._session.is_test:
                entries = [_ for _ in entries if 'Example Score' in _[0]]
            else:
                entries = [_ for _ in entries if 'Example Score' not in _[0]]
        paths = [_[-1] for _ in entries]
        return paths

    def _make_candidate_messages(
        self,
        result,
        candidate_path,
        incumbent_path,
        ):
        messages = []
        messages.append('the files ...')
        messages.append(self._tab + candidate_path)
        messages.append(self._tab + incumbent_path)
        if result:
            messages.append('... compare the same.')
        else:
            messages.append('... compare differently.')
        return messages

    # TODO: reimplement this so it's comprehensible
    def _make_command_menu_sections(self, directory, menu):
        assert os.path.isdir(directory), repr(directory)
        methods = []
        commands = self._get_commands()
        is_in_score = self._session.is_in_score
        required_files = ()
        optional_files = ()
        if self._is_score_directory(directory, ('material', 'segment')):
            package_contents = self._directory_to_package_contents(directory)
            required_files = package_contents['required_files']
            optional_files = package_contents['optional_files']
        files = required_files + optional_files
        directory_name = os.path.basename(directory)
        parent_directory_name = directory.split(os.path.sep)[-2]
        for command in commands:
            if is_in_score and not command.in_score:
                continue
            if not is_in_score and not command.outside_score:
                continue
            if (command.outside_score == 'home' and
                (not self._is_score_directory(directory, 'scores') and
                not is_in_score)):
                continue
            if ((command.directories or command.parent_directories) and
                directory_name not in command.directories and
                parent_directory_name not in command.parent_directories):
                continue
            if command.file_ is not None and command.file_ not in files:
                continue
            if (command.in_score_directory_only and not
                self._is_score_directory(directory, 'inner')):
                continue
            if (command.never_in_score_directory and
                self._is_score_directory(directory, 'inner')):
                continue
            methods.append(command)
        command_groups = {}
        for method in methods:
            if method.section not in command_groups:
                command_groups[method.section] = []
            command_group = command_groups[method.section]
            command_group.append(method)
        for menu_section_name in command_groups:
            command_group = command_groups[menu_section_name]
            is_hidden = True
            if menu_section_name == 'basic':
                is_hidden = False
            menu.make_command_section(
                is_hidden=is_hidden,
                commands=command_group,
                name=menu_section_name,
                )

    def _make_file(self, directory):
        assert os.path.isdir(directory), repr(directory)
        getter = self._io_manager._make_getter()
        getter.append_string('file name')
        file_name = getter._run(io_manager=self._io_manager)
        if file_name is None:
            return
        file_name = self._coerce_name(directory, file_name)
        name_predicate = self._directory_to_name_predicate(directory)
        if not name_predicate(file_name):
            message = 'invalid file name: {!r}.'
            message = message.format(file_name)
            self._io_manager._display(message)
            self._io_manager._acknowledge()
            return
        file_path = os.path.join(directory, file_name)
        if self._is_score_directory(directory, 'makers'):
            source_file = os.path.join(
                configuration.abjad_ide_boilerplate_directory,
                'Maker.py',
                )
            shutil.copyfile(source_file, file_path)
        else:
            contents = ''
            file_name, file_extension = os.path.splitext(file_name)
            if file_extension == '.py':
                contents = self._unicode_directive
            self._io_manager.write(file_path, contents)
        self._io_manager.edit(file_path)

    def _make_main_menu(self, directory, explicit_header):
        assert os.path.isdir(directory), repr(directory)
        assert isinstance(explicit_header, str), repr(explicit_header)
        name = stringtools.to_space_delimited_lowercase(type(self).__name__)
        menu = self._io_manager._make_menu(
            explicit_header=explicit_header,
            name=name,
            )
        menu_entries = []
        secondary_menu_entries = self._make_secondary_menu_entries(directory)
        secondary_menu_entries = []
        for path in self._list_secondary_paths(directory):
            base_name = os.path.basename(path)
            menu_entry = (base_name, None, None, path)
            secondary_menu_entries.append(menu_entry)
        menu_entries.extend(secondary_menu_entries)
        asset_menu_entries = []
        paths = self._list_visible_paths(directory)
        strings = [self._to_menu_string(_) for _ in paths]
        pairs = list(zip(strings, paths))
        def sort_function(pair):
            string = pair[0]
            string = stringtools.strip_diacritics(string)
            string = string.replace("'", '')
            return string
        pairs.sort(key=lambda _: sort_function(_))
        for string, path in pairs:
            asset_menu_entry = (string, None, None, path)
            asset_menu_entries.append(asset_menu_entry)
        menu_entries.extend(asset_menu_entries)
        if menu_entries:
            section = menu.make_asset_section(menu_entries=menu_entries)
            if self._is_score_directory(directory, 'scores'):
                section._group_by_annotation = False
            else:
                section._group_by_annotation = True
        self._make_command_menu_sections(directory, menu)
        return menu

    def _make_material_or_segment_package(self, directory):
        assert os.path.isdir(directory), repr(directory)
        assert self._session.is_in_score
        new_directory = directory
        path = self._get_available_path_in_directory(new_directory)
        if not path:
            return
        assert not os.path.exists(path)
        os.mkdir(path)
        required_files = (
            '__init__.py',
            '__metadata__.py',
            'definition.py',
            )
        for required_file in required_files:
            if required_file == '__init__.py':
                source_path = os.path.join(
                    configuration.abjad_ide_boilerplate_directory,
                    'empty_unicode.py',
                    )
            elif required_file == '__metadata__.py':
                source_path = os.path.join(
                    configuration.abjad_ide_boilerplate_directory,
                    '__metadata__.py',
                    )
            elif required_file == 'definition.py':
                source_path = os.path.join(
                    configuration.abjad_ide_boilerplate_directory,
                    'definition.py',
                    )
            else:
                raise ValueError(required_file)
            target_path = os.path.join(path, required_file)
            shutil.copyfile(source_path, target_path)
        new_path = path
        paths = self._list_visible_paths(directory)
        if path not in paths:
            self._clear_view(directory)
        self._manage_directory(new_path)

    def _make_score_package(self):
        message = 'enter title'
        getter = self._io_manager._make_getter()
        getter.append_string(message)
        title = getter._run(io_manager=self._io_manager)
        if not title:
            return
        package_name = stringtools.strip_diacritics(title)
        package_name = stringtools.to_snake_case(package_name)
        scores_directory = configuration.composer_scores_directory
        if self._session.is_test:
            scores_directory = configuration.abjad_ide_example_scores_directory
        outer_score_directory = os.path.join(scores_directory, package_name)
        if os.path.exists(outer_score_directory):
            message = 'directory already exists: {}.'
            message = message.format(outer_score_directory)
            self._io_manager._display(message)
            return
        year = datetime.date.today().year
        systemtools.IOManager._make_score_package(
            outer_score_directory,
            title,
            year,
            configuration.composer_full_name,
            configuration.composer_email,
            configuration.composer_github_username,
            )
        self._clear_view(scores_directory)
        inner_score_directory = os.path.join(
            outer_score_directory, 
            package_name,
            )
        self._manage_directory(inner_score_directory)

    def _make_secondary_menu_entries(self, directory):
        menu_entries = []
        for path in self._list_secondary_paths(directory):
            base_name = os.path.basename(path)
            menu_entry = (base_name, None, None, path)
            menu_entries.append(menu_entry)
        return menu_entries

    def _manage_directory(self, directory):
        if not os.path.exists(directory):
            message = 'directory does not exist: {}.'
            message = message.format(directory)
            self._io_manager._display(message)
            return
        self._session._pending_redraw = True
        self._session._manifest_current_directory = directory
        menu_header = self._to_menu_header(directory)
        menu = self._make_main_menu(directory, menu_header)
        while True:
            self._session._manifest_current_directory = directory
            os.chdir(directory)
            if self._session._pending_menu_rebuild:
                menu = self._make_main_menu(directory, menu_header)
                self._session._pending_menu_rebuild = False
            result = menu._run(io_manager=self._io_manager)
            if self._session.is_quitting:
                return
            if result is None:
                continue
            self._handle_input(result)
            if self._session.is_quitting:
                return

    @staticmethod
    def _match_display_string_view_pattern(pattern, entry):
        display_string, _, _, path = entry
        token = ':ds:'
        assert token in pattern, repr(pattern)
        pattern = pattern.replace(token, repr(display_string))
        try:
            result = eval(pattern)
        except:
            traceback.print_exc()
            return False
        return result

    def _match_metadata_view_pattern(self, pattern, entry):
        display_string, _, _, path = entry
        count = pattern.count('md:')
        for _ in range(count+1):
            parts = pattern.split()
            for part in parts:
                if part.startswith('md:'):
                    metadatum_name = part[3:]
                    metadatum = self._get_metadatum(
                        path,
                        metadatum_name,
                        include_score=True,
                        )
                    metadatum = repr(metadatum)
                    pattern = pattern.replace(part, metadatum)
        try:
            result = eval(pattern)
        except:
            traceback.print_exc()
            return False
        return result

    @staticmethod
    def _match_path_view_pattern(pattern, entry):
        display_string, _, _, path = entry
        token = ':path:'
        assert token in pattern, repr(pattern)
        pattern = pattern.replace(token, repr(path))
        try:
            result = eval(pattern)
        except:
            traceback.print_exc()
            return False
        return result

    def _match_visible_path(self, secondary_paths, visible_paths, input_):
        assert isinstance(input_, (str, int)), repr(input_)
        paths = secondary_paths + visible_paths
        if isinstance(input_, int):
            path_number = input_
            path_index = path_number - 1
            path = paths[path_index]
            if path in secondary_paths:
                message = 'can not rename secondary asset {}.'
                message = message.format(path)
                self._io_manager._display(message)
                return
            return path
        elif isinstance(input_, str):
            name = input_
            name = name.lower()
            for path in visible_paths:
                base_name = os.path.basename(path)
                base_name = base_name.lower()
                if base_name.startswith(name):
                    return path
                base_name = base_name.replace('_', ' ')
                if base_name.startswith(name):
                    return path
                if not os.path.isdir(path):
                    continue
                title = self._get_metadatum(path, 'title')
                if not title:
                    continue
                title = title.lower()
                if title.startswith(name):
                    return path
            message = 'does not match visible path: {!r}.'
            message = message.format(name)
            self._io_manager._display(message)
            return
        else:
            raise ValueError(repr(input_))

    def _open_in_every_package(self, directories, file_name, verb='open'):
        paths = []
        for path in directories:
            path = os.path.join(path, file_name)
            if os.path.isfile(path):
                paths.append(path)
        if not paths:
            message = 'no {} files found.'
            message = message.format(file_name)
            self._io_manager._display(message)
            return
        messages = []
        message = 'will {} ...'.format(verb)
        messages.append(message)
        for path in paths:
            message = '   ' + path
            messages.append(message)
        self._io_manager._display(messages)
        result = self._io_manager._confirm()
        if not result:
            return
        self._io_manager.open_file(paths)

    def _parse_paper_dimensions(self, score_directory):
        string = self._get_metadatum(score_directory, 'paper_dimensions')
        string = string or '8.5 x 11 in'
        parts = string.split()
        assert len(parts) == 4
        width, _, height, units = parts
        width = eval(width)
        height = eval(height)
        return width, height, units

    def _path_to_annotation(self, path):
        annotation = None
        if self._is_score_directory(path, 'inner'):
            metadata = self._get_metadata(path)
            if metadata:
                year = metadata.get('year')
                title = metadata.get('title')
                if year:
                    annotation = '{} ({})'.format(title, year)
                else:
                    annotation = str(title)
            else:
                package_name = os.path.basename(path)
                annotation = package_name
        return annotation

    def _read_view(self, directory):
        assert os.path.isdir(directory), repr(directory)
        view_name = self._read_view_name(directory)
        if not view_name:
            return
        view_inventory = self._read_view_inventory(directory)
        if not view_inventory:
            return
        return view_inventory.get(view_name)

    def _read_view_inventory(self, directory):
        from ide.tools import idetools
        assert os.path.isdir(directory), repr(directory)
        views_py_path = self._get_views_py_path(directory)
        result = self._io_manager.execute_file(
            path=views_py_path,
            attribute_names=('view_inventory',),
            )
        if result == 'corrupt':
            messages = []
            message = '{} __views.py__ is corrupt:'
            message = message.format(directory)
            messages.append(message)
            messages.append('')
            message = '    {}'.format(views_py_path)
            messages.append(message)
            self._io_manager._display(messages)
            return
        if not result:
            return
        assert len(result) == 1
        view_inventory = result[0]
        if view_inventory is None:
            view_inventory = idetools.ViewInventory()
        items = list(view_inventory.items())
        view_inventory = idetools.ViewInventory(items)
        return view_inventory

    def _read_view_name(self, directory):
        assert os.path.isdir(directory), repr(directory)
        return self._get_metadatum(directory, 'view_name')

    def _remove(self, path):
        # handle score packages correctly
        parts = path.split(os.path.sep)
        if parts[-2] == parts[-1]:
            parts = parts[:-1]
        path = os.path.sep.join(parts)
        if self._is_in_git_repository(path):
            if self._is_git_unknown(path):
                command = 'rm -rf {}'
            else:
                command = 'git rm --force -r {}'
        else:
            command = 'rm -rf {}'
        command = command.format(path)
        with systemtools.TemporaryDirectoryChange(directory=path):
            process = self._io_manager.make_subprocess(command)
        self._io_manager._read_one_line_from_pipe(process.stdout)
        return True

    @staticmethod
    def _remove_file_line(file_path, line_to_remove):
        lines_to_keep = []
        with open(file_path, 'r') as file_pointer:
            for line in file_pointer.readlines():
                if line == line_to_remove:
                    pass
                else:
                    lines_to_keep.append(line)
        with open(file_path, 'w') as file_pointer:
            contents = ''.join(lines_to_keep)
            file_pointer.write(contents)

    @staticmethod
    def _replace_in_file(file_path, old, new):
        assert isinstance(old, str), repr(old)
        assert isinstance(new, str), repr(new)
        with open(file_path, 'r') as file_pointer:
            new_file_lines = []
            for line in file_pointer.readlines():
                line = line.replace(old, new)
                new_file_lines.append(line)
        new_file_contents = ''.join(new_file_lines)
        if sys.version_info[0] == 2:
            new_file_contents = unicode(new_file_contents, 'utf-8')
            with codecs.open(file_path, 'w', encoding='utf-8') as file_pointer:
                file_pointer.write(new_file_contents)
        else:
            with open(file_path, 'w') as file_pointer:
                file_pointer.write(new_file_contents)

    def _select_view(self, directory, is_ranged=False):
        assert os.path.isdir(directory), repr(directory)
        view_inventory = self._read_view_inventory(directory)
        if view_inventory is None:
            message = 'no views found.'
            self._io_manager._display(message)
            return
        view_names = list(view_inventory.keys())
        view_names.append('none')
        if is_ranged:
            target_name = 'view(s)'
        else:
            target_name = 'view'
        target_name = '{} to apply'.format(target_name)
        menu_header = self._to_menu_header(directory)
        selector = self._io_manager._make_selector(
            is_ranged=is_ranged,
            items=view_names,
            menu_header=menu_header,
            target_name=target_name,
            )
        result = selector._run(io_manager=self._io_manager)
        if result is None:
            return
        return result

    def _select_visible_path(self, directory, infinitive_phrase=None):
        assert os.path.isdir(directory), repr(directory)
        secondary_paths = self._list_secondary_paths(directory)
        visible_paths = self._list_visible_paths(directory)
        if not visible_paths:
            message = 'no visible paths'
            if infinitive_phrase is not None:
                message = message + ' ' + infinitive_phrase
            message = message + '.'
            self._io_manager._display(message)
            return
        paths = secondary_paths + visible_paths
        asset_identifier = self._directory_to_asset_identifier(directory)
        message = 'enter {}'.format(asset_identifier)
        if infinitive_phrase:
            message = message + ' ' + infinitive_phrase
        getter = self._io_manager._make_getter()
        getter.append_string_or_integer(message)
        result = getter._run(io_manager=self._io_manager)
        if not result:
            return
        path = self._match_visible_path(secondary_paths, visible_paths, result)
        return path

    def _select_visible_paths(self, directory, infinitive_phrase=None):
        assert os.path.isdir(directory), repr(directory)
        secondary_paths = self._list_secondary_paths(directory)
        visible_paths = self._list_visible_paths(directory)
        if not visible_paths:
            message = 'no visible paths'
            if infinitive_phrase is not None:
                message = message + ' ' + infinitive_phrase
            message = message + '.'
            self._io_manager._display(message)
            return
        paths = secondary_paths + visible_paths
        asset_identifier = self._directory_to_asset_identifier(directory)
        message = 'enter {}(s)'
        if infinitive_phrase is not None:
            message += ' ' + infinitive_phrase
        message = message.format(asset_identifier)
        getter = self._io_manager._make_getter()
        getter.append_anything(message)
        result = getter._run(io_manager=self._io_manager)
        if not result:
            return
        if isinstance(result, int):
            result = [result]
        elif isinstance(result, str) and ',' in result:
            result_ = result.split(',')
            result = []
            for part in result_:
                part = part.strip()
                if mathtools.is_integer_equivalent_expr(part):
                    part = int(part)
                result.append(part)
        elif isinstance(result, str) and not ',' in result:
            result = [result]
        paths = []
        for input_ in result:
            path = self._match_visible_path(
                secondary_paths, 
                visible_paths,
                input_,
                )
            if path:
                paths.append(path)
        return paths

    @staticmethod
    def _sort_ordered_dictionary(dictionary):
        new_dictionary = type(dictionary)()
        for key in sorted(dictionary):
            new_dictionary[key] = dictionary[key]
        return new_dictionary

    def _start(self, input_=None):
        self._session._reinitialize()
        type(self).__init__(self, session=self._session)
        if input_:
            self._session._pending_input = input_
        self._session._pending_redraw = True
        directory = configuration.composer_scores_directory
        if self._session.is_test:
            directory = configuration.abjad_ide_example_scores_directory
        while True:
            self._manage_directory(directory)
            if self._session.is_quitting:
                break
        self._io_manager._clean_up()
        self._io_manager.clear_terminal()

    @staticmethod
    def _strip_annotation(display_string):
        if not display_string.endswith(')'):
            return display_string
        index = display_string.find('(')
        result = display_string[:index]
        result = result.strip()
        return result

    def _test_add(self, path):
        assert self._is_up_to_date(path)
        path_1 = os.path.join(path, 'tmp_1.py')
        path_2 = os.path.join(path, 'tmp_2.py')
        with systemtools.FilesystemState(remove=[path_1, path_2]):
            with open(path_1, 'w') as file_pointer:
                file_pointer.write('')
            with open(path_2, 'w') as file_pointer:
                file_pointer.write('')
            assert os.path.exists(path_1)
            assert os.path.exists(path_2)
            assert not self._is_up_to_date(path)
            assert self._get_unadded_asset_paths(path) == [path_1, path_2]
            assert self._get_added_asset_paths(path) == []
            self._git_add(path)
            assert self._get_unadded_asset_paths(path) == []
            assert self._get_added_asset_paths(path) == [path_1, path_2]
            self._unadd_added_assets(path)
            assert self._get_unadded_asset_paths(path) == [path_1, path_2]
            assert self._get_added_asset_paths(path) == []
        assert self._is_up_to_date(path)
        return True

    def _test_revert(self, path):
        assert self._is_up_to_date(path)
        assert self._get_modified_asset_paths(path) == []
        file_name = self._find_first_file_name(path)
        if not file_name:
            return
        file_path = os.path.join(path, file_name)
        with systemtools.FilesystemState(keep=[file_path]):
            with open(file_path, 'a') as file_pointer:
                string = '# extra text appended during testing'
                file_pointer.write(string)
            assert not self._is_up_to_date(path)
            assert self._get_modified_asset_paths(path) == [file_path]
            self._get_revert(path)
        assert self._get_modified_asset_paths(path) == []
        assert self._is_up_to_date(path)
        return True

    def _to_classfile_name(self, name):
        assert isinstance(name, str), repr(name)
        name = stringtools.strip_diacritics(name)
        name, extension = os.path.splitext(name)
        name = stringtools.to_upper_camel_case(name)
        name = name + '.py'
        assert self._is_classfile_name(name), repr(name)
        return name

    def _to_dash_case_file_name(self, name):
        assert isinstance(name, str), repr(name)
        name = stringtools.strip_diacritics(name)
        name = name.lower()
        name, extension = os.path.splitext(name)
        name = stringtools.to_dash_case(name)
        extension = extension or '.txt'
        name = name + extension
        assert self._is_dash_case_file_name(name), repr(name)
        return name

    def _to_menu_header(self, directory):
        assert os.path.isdir(directory), repr(directory)
        header_parts = []
        if self._is_score_directory(directory, 'scores'):
            return 'Abjad IDE - all score directories'
        score_directory = self._to_score_directory(directory)
        score_part = self._get_title_metadatum(score_directory)
        header_parts.append(score_part)
        trimmed_path = self._trim_scores_directory(directory)
        path_parts = trimmed_path.split(os.path.sep)
        path_parts = path_parts[2:]
        if not path_parts:
            directory_part, package_part = None, None
        elif len(path_parts) == 1:
            directory_part, package_part = path_parts[0], None
        elif len(path_parts) == 2:
            directory_part, package_part = path_parts
        else:
            raise ValueError(directory)
        if directory_part:
            directory_part = directory_part + ' directory'
            header_parts.append(directory_part)
        if package_part:
            package_part = self._get_name_metadatum(directory)
            header_parts.append(package_part)
        header = ' - '.join(header_parts)
        return header

    def _to_menu_string(self, directory):
        if self._is_score_directory(directory, 'inner'):
            return self._path_to_annotation(directory)
        name = os.path.basename(directory)
        if '_' in name and not self._is_score_directory(directory, 'test'):
            name = stringtools.to_space_delimited_lowercase(name)
        if self._is_score_directory(directory, 'segment'):
            return self._get_metadatum(directory, 'name', name)
        else:
            return name

    def _to_module_file_name(self, name):
        assert isinstance(name, str), repr(name)
        name = stringtools.strip_diacritics(name)
        name = name.lower()
        name, extension = os.path.splitext(name)
        name = stringtools.to_snake_case(name)
        name = name + '.py'
        assert self._is_module_file_name(name), repr(name)
        return name

    def _to_package_name(self, name):
        assert isinstance(name, str), repr(name)
        name = stringtools.strip_diacritics(name)
        name = name.lower()
        name, extension = os.path.splitext(name)
        name = stringtools.to_snake_case(name)
        assert self._is_package_name(name), repr(name)
        return name

    @staticmethod
    def _to_score_directory(path, directory_name=None):
        assert os.path.sep in path, repr(path)
        if directory_name == 'scores':
            if path.startswith(configuration.composer_scores_directory):
                return configuration.composer_scores_directory
            elif path.startswith(configuration.abjad_ide_example_scores_directory):
                return configuration.abjad_ide_example_scores_directory
        if path.startswith(configuration.composer_scores_directory):
            prefix = len(configuration.composer_scores_directory)
        elif path.startswith(configuration.abjad_ide_example_scores_directory):
            prefix = len(configuration.abjad_ide_example_scores_directory)
        else:
            return
        path_prefix = path[:prefix]
        path_suffix = path[prefix + 1:]
        score_name = path_suffix.split(os.path.sep)[0]
        score_path = os.path.join(path_prefix, score_name)
        score_path = os.path.join(score_path, score_name)
        if os.path.normpath(score_path) == os.path.normpath(
            configuration.composer_scores_directory):
            return
        if os.path.normpath(score_path) == os.path.normpath(
            configuration.abjad_ide_example_scores_directory):
            return
        if directory_name is not None:
            score_path = os.path.join(score_path, directory_name)
        return score_path

    def _to_stylesheet_name(self, name):
        assert isinstance(name, str), repr(name)
        name = stringtools.strip_diacritics(name)
        name = name.lower()
        name, extension = os.path.splitext(name)
        name = stringtools.to_dash_case(name)
        name = name + '.ily'
        assert self._is_stylesheet_name(name), repr(name)
        return name

    def _to_test_file_name(self, name):
        assert isinstance(name, str), repr(name)
        name = stringtools.strip_diacritics(name)
        name = name.lower()
        name, extension = os.path.splitext(name)
        name = stringtools.to_snake_case(name)
        if not name.startswith('test_'):
            name = 'test_' + name
        name = name + '.py'
        assert self._is_test_file_name(name), repr(name)
        return name
    

    @staticmethod
    def _trim_lilypond_file(file_path):
        lines = []
        with open(file_path, 'r') as file_pointer:
            found_score_block = False
            for line in file_pointer.readlines():
                if line.startswith(r'\score'):
                    found_score_block = True
                    continue
                if line.startswith('}'):
                    found_score_block = False
                    lines.append('\n')
                    continue
                if found_score_block:
                    lines.append(line)
        if lines and lines[-1] == '\n':
            lines.pop()
        lines = ''.join(lines)
        with open(file_path, 'w') as file_pointer:
            file_pointer.write(lines)

    @staticmethod
    def _trim_scores_directory(path):
        assert os.path.sep in path, repr(path)
        if path.startswith(configuration.composer_scores_directory):
            scores_directory = configuration.composer_scores_directory
        elif path.startswith(configuration.abjad_ide_example_scores_directory):
            scores_directory = configuration.abjad_ide_example_scores_directory
        else:
            return path
        count = len(scores_directory.split(os.path.sep))
        parts = path.split(os.path.sep)
        parts = parts[count:]
        path = os.path.join(*parts)
        return path

    def _unadd_added_assets(self, path):
        paths = []
        paths.extend(self._get_added_asset_paths(path))
        paths.extend(self._get_modified_asset_paths(path))
        commands = []
        for path in paths:
            command = 'git reset -- {}'.format(path)
            commands.append(command)
        command = ' && '.join(commands)
        with systemtools.TemporaryDirectoryChange(directory=path):
            self._io_manager.spawn_subprocess(command)

    def _update_order_dependent_segment_metadata(self, directory):
        assert os.path.isdir(directory), repr(directory)
        directory = self._to_score_directory(
            directory,
            'segments',
            )
        paths = self._list_visible_paths(directory)
        if not paths:
            return
        segment_count = len(paths)
        # update segment numbers and segment count
        for segment_index, path in enumerate(paths):
            segment_number = segment_index + 1
            self._add_metadatum(
                path,
                'segment_number',
                segment_number,
                )
            self._add_metadatum(
                path,
                'segment_count',
                segment_count,
                )
        # update first bar numbers and measure counts
        path = paths[0]
        first_bar_number = 1
        self._add_metadatum(
            path,
            'first_bar_number',
            first_bar_number,
            )
        measure_count = self._get_metadatum(path, 'measure_count')
        if not measure_count:
            return
        next_bar_number = first_bar_number + measure_count
        for path in paths[1:]:
            first_bar_number = next_bar_number
            self._add_metadatum(
                path,
                'first_bar_number',
                next_bar_number,
                )
            measure_count = self._get_metadatum(path, 'measure_count')
            if not measure_count:
                return
            next_bar_number = first_bar_number + measure_count

    def _write_enclosing_artifacts(self, inner_path, outer_path):
        self._copy_boilerplate(
            'README.md',
            outer_path,
            )
        self._copy_boilerplate(
            'requirements.txt',
            outer_path,
            )
        self._copy_boilerplate(
            'setup.cfg',
            outer_path,
            )
        package_name = os.path.basename(outer_path)
        replacements = {
            'COMPOSER_EMAIL': configuration.composer_email,
            'COMPOSER_FULL_NAME': configuration.composer_full_name,
            'COMPOSER_GITHUB_USERNAME': configuration.composer_github_username,
            'PACKAGE_NAME': package_name,
            }
        self._copy_boilerplate(
            'setup.py',
            outer_path,
            replacements=replacements,
            )

    def _write_metadata_py(self, directory, metadata):
        assert os.path.isdir(directory), repr(directory)
        metadata_py_path = os.path.join(directory, '__metadata__.py')
        lines = []
        lines.append(self._unicode_directive)
        lines.append('from abjad import *')
        lines.append('')
        lines.append('')
        contents = '\n'.join(lines)
        metadata = datastructuretools.TypedOrderedDict(metadata)
        items = list(metadata.items())
        items.sort()
        metadata = datastructuretools.TypedOrderedDict(items)
        metadata_lines = format(metadata, 'storage')
        metadata_lines = 'metadata = {}'.format(metadata_lines)
        contents = contents + '\n' + metadata_lines
        with open(metadata_py_path, 'w') as file_pointer:
            file_pointer.write(contents)

    # unused?
    def _write_view_inventory(self, directory, view_inventory):
        assert os.path.isdir(directory), repr(directory)
        lines = []
        lines.append(self._unicode_directive)
        lines.append(self._abjad_import_statement)
        lines.append('from ide.tools import idetools')
        lines.append('')
        lines.append('')
        view_inventory = self._sort_ordered_dictionary(view_inventory)
        line = 'view_inventory={}'.format(format(view_inventory))
        lines.append(line)
        contents = '\n'.join(lines)
        views_py_path = self._get_views_py_path(directory)
        self._io_manager.write(views_py_path, contents)

    ### PUBLIC METHODS ###

    @Command(
        'dfk',
        argument_name='current_directory',
        description='definition file - check',
        file_='definition.py',
        outside_score=False,
        section='definition_file',
        )
    def check_definition_file(self, directory, dry_run=False):
        r'''Checks definition file.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        definition_path = os.path.join(directory, 'definition.py')
        if not os.path.isfile(definition_path):
            message = 'file not found: {}.'
            message = message.format(definition_path)
            self._io_manager._display(message)
            return
        inputs, outputs = [], []
        if dry_run:
            inputs.append(definition_path)
            return inputs, outputs
        stdout_lines, stderr_lines = self._io_manager.interpret_file(
            definition_path)
        if stderr_lines:
            messages = [definition_path + ' FAILED:']
            messages.extend('    ' + _ for _ in stderr_lines)
            self._io_manager._display(messages)
        else:
            message = '{} OK.'.format(definition_path)
            self._io_manager._display(message)

    @Command(
        'dfk*',
        argument_name='current_directory',
        directories=('materials', 'segments'),
        outside_score=False,
        section='star',
        )
    def check_every_definition_file(self, directory):
        r'''Checks definition file in every package.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        paths = self._list_visible_paths(directory)
        inputs, outputs = [], []
        for path in paths:
            inputs_, outputs_ = self.check_definition_file(path, dry_run=True)
            inputs.extend(inputs_)
            outputs.extend(outputs_)
        messages = self._format_messaging(inputs, outputs, verb='check')
        self._io_manager._display(messages)
        result = self._io_manager._confirm()
        if not result:
            return
        start_time = time.time()
        for path in paths:
            self.check_definition_file(path)
        stop_time = time.time()
        total_time = stop_time - start_time
        total_time = int(total_time)
        message = 'total time: {} seconds.'
        message = message.format(total_time)
        self._io_manager._display(message)

    @Command(
        'mc',
        argument_name='current_directory',
        directories=('build'),
        outside_score=False,
        section='build',
        )
    def collect_segment_lilypond_files(self, directory):
        r'''Copies ``illustration.ly`` files from segment packages to build
        directory.

        Trims top-level comments, includes and directives from each
        ``illustration.ly`` file.

        Trims header and paper block from each ``illustration.ly`` file.

        Leaves score block in each ``illustration.ly`` file.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        pairs = self._gather_segment_files(
            score_directory,
            'illustration.ly',
            )
        if not pairs:
            return
        for source_file_path, target_file_path in pairs:
            candidate_file_path = target_file_path.replace(
                '.ly',
                '.candidate.ly',
                )
            with systemtools.FilesystemState(remove=[candidate_file_path]):
                shutil.copyfile(source_file_path, candidate_file_path)
                self._trim_lilypond_file(candidate_file_path)
                self._handle_candidate(
                    candidate_file_path,
                    target_file_path,
                    )
                self._io_manager._display('')

    @Command(
        'cp',
        argument_name='current_directory',
        is_hidden=False,
        never_in_score_directory=True,
        section='basic',
        )
    def copy(self, directory):
        r'''Copies into `directory`.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        directories = self._collect_similar_directories(
            directory,
            example_scores=self._session.is_test,
            )
        paths = []
        for directory_ in directories:
            for name in os.listdir(directory_):
                if name.endswith('.pyc'):
                    continue
                if name.startswith('.'):
                    continue
                if name == '__pycache__':
                    continue
                path = os.path.join(directory_, name)
                paths.append(path)
        selector = self._io_manager._make_selector(items=paths)
        source_path = selector._run(io_manager=self._io_manager)
        if not source_path:
            return
        if source_path not in paths:
            return
        asset_name = os.path.basename(source_path)
        target_path = os.path.join(directory, asset_name)
        messages = []
        messages.append('will copy ...')
        messages.append(' FROM: {}'.format(source_path))
        messages.append('   TO: {}'.format(target_path))
        self._io_manager._display(messages)
        result = self._io_manager._confirm()
        if not result:
            return
        if os.path.isfile(source_path):
            shutil.copyfile(source_path, target_path)
        elif os.path.isdir(source_path):
            shutil.copytree(source_path, target_path)
        else:
            raise ValueError(source_path)
        self._session._pending_menu_rebuild = True
        self._session._pending_redraw = True

    @Command(
        '?', 
        section='system',
        )
    def display_action_command_help(self):
        r'''Displays action commands.

        Returns none.
        '''
        pass

    @Command(
        ';', 
        section='display navigation',
        )
    def display_navigation_command_help(self):
        r'''Displays navigation commands.

        Returns none.
        '''
        pass

    @Command(
        'abb',
        argument_name='current_directory',
        description='abbreviations - edit',
        outside_score=False,
        section='global files',
        )
    def edit_abbreviations_file(self, directory):
        r'''Edits abbreviations file.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        path = os.path.join(
            score_directory,
            'materials',
            '__abbreviations__.py',
            )
        if not path or not os.path.isfile(path):
            with open(path, 'w') as file_pointer:
                file_pointer.write('')
        self._io_manager.edit(path)

    @Command(
        'df',
        argument_name='current_directory',
        description='definition file - edit',
        file_='definition.py',
        outside_score=False,
        section='definition_file',
        )
    def edit_definition_file(self, directory):
        r'''Edits definition file.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        definition_path = os.path.join(directory, 'definition.py')
        self._io_manager.edit(definition_path)

    @Command(
        'df*',
        argument_name='current_directory',
        directories=('materials', 'segments'),
        section='star',
        )
    def edit_every_definition_file(self, directory):
        r'''Edits definition file in every subdirectory of `directory`.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        paths = self._list_visible_paths(directory)
        self._open_in_every_package(paths, 'definition.py')

    @Command(
        'ill',
        argument_name='current_directory',
        description='illustrate file - edit',
        file_='__illustrate__.py',
        outside_score=False,
        section='illustrate_file',
        )
    def edit_illustrate_file(self, directory):
        r'''Edits illustrate file.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        illustrate_py_path = os.path.join(directory, '__illustrate__.py')
        self._io_manager.edit(illustrate_py_path)

    @Command(
        'log', 
        description='log - edit',
        section='global files',
        )
    def edit_lilypond_log(self):
        r'''Edits LilyPond log.

        Returns none.
        '''
        from abjad.tools import systemtools
        self._session._attempted_to_open_file = True
        if self._session.is_test:
            return
        systemtools.IOManager.open_last_log()

    @Command(
        'ly',
        argument_name='current_directory',
        description='ly - edit',
        file_='illustration.ly',
        outside_score=False,
        section='ly',
        )
    def edit_ly(self, directory):
        r'''Edits ``illustration.ly`` in `directory`.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        file_path = os.path.join(directory, 'illustration.ly')
        self._io_manager.open_file(file_path)

    @Command(
        'sty',
        argument_name='current_directory',
        description='stylesheet - edit',
        outside_score=False,
        section='global files',
        )
    def edit_score_stylesheet(self, directory):
        r'''Edits score stylesheet.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        path = os.path.join(
            score_directory,
            'stylesheets',
            'stylesheet.ily',
            )
        if not path or not os.path.isfile(path):
            with open(path, 'w') as file_pointer:
                file_pointer.write('')
        self._io_manager.edit(path)

    @Command(
        'bcg',
        argument_name='current_directory',
        directories=('build'),
        outside_score=False,
        section='build',
        )
    def generate_back_cover_source(self, directory):
        r'''Generates ``back-cover.tex``.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        replacements = {}
        catalog_number = self._get_metadatum(score_directory, 'catalog_number')
        if catalog_number:
            old = 'CATALOG NUMBER'
            new = str(catalog_number)
            replacements[old] = new
        composer_website = configuration.composer_website
        if self._session.is_test:
            composer_website = 'www.composer-website.com'
        if composer_website:
            old = 'COMPOSER WEBSITE'
            new = str(composer_website)
            replacements[old] = new
        price = self._get_metadatum(score_directory, 'price')
        if price:
            old = 'PRICE'
            new = str(price)
            replacements[old] = new
        width, height, unit = self._parse_paper_dimensions(score_directory)
        if width and height:
            old = '{PAPER_SIZE}'
            new = '{{{}{}, {}{}}}'
            new = new.format(width, unit, height, unit)
            replacements[old] = new
        self._copy_boilerplate(
            'back-cover.tex',
            os.path.join(score_directory, 'build'),
            replacements=replacements,
            )

    @Command(
        'fcg',
        argument_name='current_directory',
        directories=('build'),
        outside_score=False,
        section='build',
        )
    def generate_front_cover_source(self, directory):
        r'''Generates ``front-cover.tex``.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        file_name = 'front-cover.tex'
        replacements = {}
        score_title = self._get_title_metadatum(
            score_directory,
            year=False,
            )
        if score_title:
            old = 'TITLE'
            new = str(score_title.upper())
            replacements[old] = new
        forces_tagline = self._get_metadatum(score_directory, 'forces_tagline')
        if forces_tagline:
            old = 'FOR INSTRUMENTS'
            new = str(forces_tagline)
            replacements[old] = new
        year = self._get_metadatum(score_directory, 'year')
        if year:
            old = 'YEAR'
            new = str(year)
            replacements[old] = new
        composer = configuration.composer_uppercase_name
        if self._session.is_test:
            composer = 'EXAMPLE COMPOSER NAME'
        if composer:
            old = 'COMPOSER'
            new = str(composer)
            replacements[old] = new
        width, height, unit = self._parse_paper_dimensions(score_directory)
        if width and height:
            old = '{PAPER_SIZE}'
            new = '{{{}{}, {}{}}}'
            new = new.format(width, unit, height, unit)
            replacements[old] = new
        self._copy_boilerplate(
            file_name,
            os.path.join(score_directory, 'build'),
            replacements=replacements,
            )

    @Command(
        'mg',
        argument_name='current_directory',
        directories=('build'),
        outside_score=False,
        section='build',
        )
    def generate_music_source(self, directory):
        r'''Generates ``music.ly``.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        result = self._confirm_segment_names(score_directory)
        if not isinstance(result, list):
            return
        segment_names = result
        lilypond_names = [_.replace('_', '-') for _ in segment_names]
        source_path = os.path.join(
            configuration.abjad_ide_boilerplate_directory,
            'music.ly',
            )
        destination_path = os.path.join(
            score_directory,
            'build',
            'music.ly',
            )
        candidate_path = os.path.join(
            score_directory,
            'build',
            'music.candidate.ly',
            )
        with systemtools.FilesystemState(remove=[candidate_path]):
            shutil.copyfile(source_path, candidate_path)
            result = self._parse_paper_dimensions(score_directory)
            width, height, unit = result
            old = '{PAPER_SIZE}'
            new = '{{{}{}, {}{}}}'
            new = new.format(width, unit, height, unit)
            self._replace_in_file(candidate_path, old, new)
            lines = []
            for lilypond_name in lilypond_names:
                file_name = lilypond_name + '.ly'
                line = self._tab + r'\include "{}"'
                line = line.format(file_name)
                lines.append(line)
            if lines:
                new = '\n'.join(lines)
                old = '%%% SEGMENTS %%%'
                self._replace_in_file(candidate_path, old, new)
            else:
                line_to_remove = '%%% SEGMENTS %%%\n'
                self._remove_file_line(candidate_path, line_to_remove)
            stylesheet_path = os.path.join(
                score_directory,
                'stylesheets',
                'stylesheet.ily',
                )
            if stylesheet_path:
                old = '% STYLESHEET_INCLUDE_STATEMENT'
                new = r'\include "../stylesheets/stylesheet.ily"'
                self._replace_in_file(candidate_path, old, new)
            language_token = lilypondfiletools.LilyPondLanguageToken()
            lilypond_language_directive = format(language_token)
            old = '% LILYPOND_LANGUAGE_DIRECTIVE'
            new = lilypond_language_directive
            self._replace_in_file(candidate_path, old, new)
            version_token = lilypondfiletools.LilyPondVersionToken()
            lilypond_version_directive = format(version_token)
            old = '% LILYPOND_VERSION_DIRECTIVE'
            new = lilypond_version_directive
            self._replace_in_file(candidate_path, old, new)
            score_title = self._get_title_metadatum(
                score_directory,
                year=False,
                )
            if score_title:
                old = 'SCORE_NAME'
                new = score_title
                self._replace_in_file(candidate_path, old, new)
            annotated_title = self._get_title_metadatum(
                score_directory,
                year=True,
                )
            if annotated_title:
                old = 'SCORE_TITLE'
                new = annotated_title
                self._replace_in_file(candidate_path, old, new)
            forces_tagline = self._get_metadatum(
                score_directory,
                'forces_tagline',
                )
            if forces_tagline:
                old = 'FORCES_TAGLINE'
                new = forces_tagline
                self._replace_in_file(candidate_path, old, new)
            self._handle_candidate(
                candidate_path,
                destination_path,
                )

    @Command(
        'pg',
        argument_name='current_directory',
        directories=('build'),
        outside_score=False,
        section='build',
        )
    def generate_preface_source(self, directory):
        r'''Generates ``preface.tex``.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        replacements = {}
        width, height, unit = self._parse_paper_dimensions(score_directory)
        if width and height:
            old = '{PAPER_SIZE}'
            new = '{{{}{}, {}{}}}'
            new = new.format(width, unit, height, unit)
            replacements[old] = new
        self._copy_boilerplate(
            'preface.tex',
            os.path.join(score_directory, 'build'),
            replacements=replacements,
            )

    @Command(
        'sg',
        argument_name='current_directory',
        directories=('build'),
        outside_score=False,
        section='build',
        )
    def generate_score_source(self, directory):
        r'''Generates ``score.tex``.

        Returns none.
        '''
        assert os.path.isdir(directory)
        score_directory = self._to_score_directory(directory)
        replacements = {}
        width, height, unit = self._parse_paper_dimensions(score_directory)
        if width and height:
            old = '{PAPER_SIZE}'
            new = '{{{}{}, {}{}}}'
            new = new.format(width, unit, height, unit)
            replacements[old] = new
        self._copy_boilerplate(
            'score.tex',
            os.path.join(score_directory, 'build'),
            replacements=replacements,
            )

    @Command(
        'add*',
        argument_name='current_directory',
        in_score=False,
        outside_score='home',
        section='git',
        )
    def git_add_every_package(self, directory):
        r'''Adds every asset to repository.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        directories = self._list_visible_paths(directory)
        self._session._attempted_method = 'git_add_every_package'
        if self._session.is_test:
            return
        inputs, outputs = [], []
        method_name = '_git_add'
        for directory in directories:
            inputs_, outputs_ = self._git_add(
                directory,
                dry_run=True,
                )
            inputs.extend(inputs_)
            outputs.extend(outputs_)
        messages = self._format_messaging(inputs, outputs, verb='add')
        self._io_manager._display(messages)
        if not inputs:
            return
        result = self._io_manager._confirm()
        if not result:
            return
        for directory in directories:
            self._git_add(directory)
        count = len(inputs)
        identifier = stringtools.pluralize('file', count)
        message = 'added {} {} to repository.'
        message = message.format(count, identifier)
        self._io_manager._display(message)

    @Command(
        'ci*',
        argument_name='current_directory',
        in_score=False,
        outside_score='home',
        section='git',
        )
    def git_commit_every_package(self, directory):
        r'''Commits every asset to repository.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        directories = self._list_visible_paths(directory)
        self._session._attempted_method = 'git_commit_every_package'
        if self._session.is_test:
            return
        getter = self._io_manager._make_getter()
        getter.append_string('commit message')
        commit_message = getter._run(io_manager=self._io_manager)
        if commit_message is None:
            return
        line = 'commit message will be: "{}"'.format(commit_message)
        self._io_manager._display(line)
        result = self._io_manager._confirm()
        if not result:
            return
        for directory in directories:
            self._git_commit(
                directory,
                commit_message=commit_message,
                )

    @Command(
        'st*',
        argument_name='current_directory',
        in_score=False,
        outside_score='home',
        section='git',
        )
    def git_status_every_package(self, directory):
        r'''Displays Git status of every package.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        directories = self._list_visible_paths(directory)
        self._session._attempted_method = 'git_status_every_package'
        directories.sort()
        for directory in directories:
            self._git_status(directory)

    @Command(
        'up*',
        argument_name='current_directory',
        in_score=False,
        outside_score='home',
        section='git',
        )
    def git_update_every_package(self, directory):
        r'''Updates every asset from repository.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        directories = self._list_visible_paths(directory)
        self._session._attempted_method = 'git_update_every_package'
        for directory in directories:
            messages = []
            message = self._to_menu_string(directory)
            message = self._strip_annotation(message)
            message = message + ':'
            messages_ = self._git_update(
                directory,
                messages_only=True,
                )
            if len(messages_) == 1:
                message = message + ' ' + messages_[0]
                messages.append(message)
            else:
                messages_ = [self._tab + _ for _ in messages_]
                messages.extend(messages_)
            self._io_manager._display(messages, capitalize=False)

    @Command('h', description='home', section='back-home-quit')
    def go_home(self):
        r'''Goes home.

        Returns none.
        '''
        directory = configuration.composer_scores_directory
        if self._session.is_test:
            directory = configuration.abjad_ide_example_scores_directory
        self._manage_directory(directory)

    @Command(
        'bb',
        argument_name='current_directory',
        outside_score=False,
        section='navigation',
        )
    def go_to_build_directory(self, directory):
        r'''Goes to build directory.

        Returns none.
        '''
        assert os.path.isdir(directory)
        directory = self._to_score_directory(directory, 'build')
        self._manage_directory(directory)

    @Command(
        'dd',
        argument_name='current_directory',
        outside_score=False,
        section='navigation',
        )
    def go_to_distribution_directory(self, directory):
        r'''Goes to distribution directory.

        Returns none.
        '''
        assert os.path.isdir(directory)
        directory = self._to_score_directory(directory, 'distribution')
        self._manage_directory(directory)

    @Command(
        'ee',
        argument_name='current_directory',
        outside_score=False,
        section='navigation',
        )
    def go_to_etc_directory(self, directory):
        r'''Goes to etc directory.

        Returns none.
        '''
        assert os.path.isdir(directory)
        directory = self._to_score_directory(directory, 'etc')
        self._manage_directory(directory)

    @Command(
        'kk',
        argument_name='current_directory',
        outside_score=False,
        section='navigation',
        )
    def go_to_makers_directory(self, directory):
        r'''Goes to makers directory.

        Returns none.
        '''
        assert os.path.isdir(directory)
        directory = self._to_score_directory(directory, 'makers')
        self._manage_directory(directory)

    @Command(
        'mm',
        argument_name='current_directory',
        outside_score=False,
        section='navigation',
        )
    def go_to_materials_directory(self, directory):
        r'''Goes to materials directory.

        Returns none.
        '''
        assert os.path.isdir(directory)
        directory = self._to_score_directory(directory, 'materials')
        self._manage_directory(directory)

    @Command(
        'ss',
        argument_name='current_directory',
        outside_score=False,
        section='navigation',
        )
    def go_to_score_directory(self, directory):
        r'''Goes to score directory.

        Returns none.
        '''
        assert os.path.isdir(directory)
        directory = self._to_score_directory(directory)
        self._manage_directory(directory)

    @Command(
        'gg',
        argument_name='current_directory',
        outside_score=False,
        section='navigation',
        )
    def go_to_segments_directory(self, directory):
        r'''Goes to segments directory.

        Returns none.
        '''
        assert os.path.isdir(directory)
        directory = self._to_score_directory(directory, 'segments')
        self._manage_directory(directory)

    @Command(
        'yy',
        argument_name='current_directory',
        outside_score=False,
        section='navigation',
        )
    def go_to_stylesheets_directory(self, directory):
        r'''Goes to stylesheets directory.

        Returns none.
        '''
        assert os.path.isdir(directory)
        directory = self._to_score_directory(directory, 'stylesheets')
        self._manage_directory(directory)

    @Command(
        'tt',
        argument_name='current_directory',
        outside_score=False,
        section='navigation',
        )
    def go_to_test_directory(self, directory):
        r'''Goes to test directory.

        Returns none.
        '''
        assert os.path.isdir(directory)
        directory = self._to_score_directory(directory, 'test')
        self._manage_directory(directory)

    @Command(
        'i',
        argument_name='current_directory',
        file_='definition.py',
        outside_score=False,
        parent_directories=('segments',),
        section='pdf',
        )
    def illustrate_definition(self, directory, dry_run=False):
        r'''Illustrates definition.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        definition_path = os.path.join(directory, 'definition.py')
        if not os.path.isfile(definition_path):
            message = 'File not found: {}.'
            message = message.format(definition_path)
            self._io_manager._display(message)
            return
        self._update_order_dependent_segment_metadata(directory)
        boilerplate_path = os.path.join(
            configuration.abjad_ide_boilerplate_directory,
            '__illustrate_segment__.py',
            )
        illustrate_path = os.path.join(
            directory,
            '__illustrate_segment__.py',
            )
        candidate_ly_path = os.path.join(
            directory,
            'illustration.candidate.ly'
            )
        candidate_pdf_path = os.path.join(
            directory,
            'illustration.candidate.pdf'
            )
        temporary_files = (
            illustrate_path,
            candidate_ly_path,
            candidate_pdf_path,
            )
        for path in temporary_files:
            if os.path.exists(path):
                os.remove(path)
        illustration_source_path = os.path.join(
            directory,
            'illustration.ly',
            )
        illustration_pdf_path = os.path.join(
            directory,
            'illustration.pdf',
            )
        inputs, outputs = [], []
        if dry_run:
            inputs.append(definition_path)
            outputs.append((illustration_source_path, illustration_pdf_path))
            return inputs, outputs
        with systemtools.FilesystemState(remove=temporary_files):
            shutil.copyfile(boilerplate_path, illustrate_path)
            previous_segment_path = self._get_previous_segment_path(directory)
            if previous_segment_path is None:
                statement = 'previous_segment_metadata = None'
            else:
                score_directory = self._to_score_directory(directory)
                score_name = os.path.basename(score_directory)
                previous_segment_name = previous_segment_path
                previous_segment_name = os.path.basename(previous_segment_path)
                statement = 'from {}.segments.{}.__metadata__'
                statement += ' import metadata as previous_segment_metadata'
                statement = statement.format(score_name, previous_segment_name)
            self._replace_in_file(
                illustrate_path,
                'PREVIOUS_SEGMENT_METADATA_IMPORT_STATEMENT',
                statement,
                )
            result = self._io_manager.interpret_file(
                illustrate_path,
                strip=False,
                )
            stdout_lines, stderr_lines = result
            if stderr_lines:
                self._io_manager._display_errors(stderr_lines)
                return
            if not os.path.exists(illustration_pdf_path):
                messages = []
                messages.append('Wrote ...')
                if os.path.exists(candidate_ly_path):
                    shutil.move(candidate_ly_path, illustration_source_path)
                    messages.append(self._tab + illustration_source_path)
                if os.path.exists(candidate_pdf_path):
                    shutil.move(candidate_pdf_path, illustration_pdf_path)
                    messages.append(self._tab + illustration_pdf_path)
                self._io_manager._display(messages)
            else:
                result = systemtools.TestManager.compare_files(
                candidate_pdf_path,
                illustration_pdf_path,
                )
                messages = self._make_candidate_messages(
                    result,
                    candidate_pdf_path,
                    illustration_pdf_path,
                    )
                self._io_manager._display(messages)
                if result:
                    message = 'preserved {}.'.format(illustration_pdf_path)
                    self._io_manager._display(message)
                    return
                else:
                    message = 'overwrite existing PDF with candidate PDF?'
                    result = self._io_manager._confirm(message=message)
                    if not result:
                        return
                    try:
                        shutil.move(candidate_ly_path, illustration_source_path)
                    except IOError:
                        pass
                    try:
                        shutil.move(candidate_pdf_path, illustration_pdf_path)
                    except IOError:
                        pass

    @Command(
        'di*',
        argument_name='current_directory',
        directories=('segments'),
        outside_score=False,
        section='star',
        )
    def illustrate_every_definition(self, directories):
        r'''Illustrates every definition.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        directories = self._list_visible_paths(directory)
        inputs, outputs = [], []
        method_name = 'illustrate_definition'
        for directory in directories:
            inputs_, outputs_ = self.illustrate_definition(
                directory,
                dry_run=True,
                )
            inputs.extend(inputs_)
            outputs.extend(outputs_)
        messages = self._format_messaging(inputs, outputs, verb='illustrate')
        self._io_manager._display(messages)
        result = self._io_manager._confirm()
        if not result:
            return
        for directory in directories:
            self.illustrate_definition(directory)

    @Command(
        'bci',
        argument_name='current_directory',
        directories=('build'),
        section='build',
        outside_score=False,
        )
    def interpret_back_cover(self, directory):
        r'''Interprets ``back-cover.tex``.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        build_directory = os.path.join(score_directory, 'build')
        self._interpret_file_ending_with(build_directory, 'back-cover.tex')

    @Command(
        'lyi*',
        argument_name='current_directory',
        directories=('materials', 'segments'),
        outside_score=False,
        section='star',
        )
    def interpret_every_ly(self, directory, open_every_illustration_pdf=True):
        r'''Interprets illustration ly in every package.

        Makes illustration PDF in every package.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        directories = self._list_visible_paths(directory)
        inputs, outputs = [], []
        method_name = 'interpret_illustration_source'
        for directory in directories:
            inputs_, outputs_ = self.interpret_ly(
                directory,
                dry_run=True,
                )
            inputs.extend(inputs_)
            outputs.extend(outputs_)
        messages = self._format_messaging(inputs, outputs)
        self._io_manager._display(messages)
        result = self._io_manager._confirm()
        if not result:
            return
        for directory in directories:
            result = self.interpret_ly(
                directory,
                confirm=False,
                )
            subprocess_messages, candidate_messages = result
            if subprocess_messages:
                self._io_manager._display(subprocess_messages)
                self._io_manager._display(candidate_messages)
                self._io_manager._display('')

    @Command(
        'fci',
        argument_name='current_directory',
        directories=('build'),
        outside_score=False,
        section='build',
        )
    def interpret_front_cover(self, directory):
        r'''Interprets ``front-cover.tex``.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        build_directory = os.path.join(score_directory, 'build')
        self._interpret_file_ending_with(build_directory, 'front-cover.tex')

    @Command(
        'lyi',
        argument_name='current_directory',
        description='ly - interpret',
        file_='illustration.ly',
        outside_score=False,
        section='ly',
        )
    def interpret_ly(self, directory, confirm=True, dry_run=False):
        r'''Interprets illustration ly in `directory`.

        Makes illustration PDF.

        Returns a pair.
        
        Pairs equals list of STDERR messages from LilyPond together
        with list of candidate messages.
        '''
        assert os.path.isdir(directory), repr(directory)
        illustration_source_path = os.path.join(directory, 'illustration.ly')
        illustration_pdf_path = os.path.join(directory, 'illustration.pdf')
        inputs, outputs = [], []
        if os.path.isfile(illustration_source_path):
            inputs.append(illustration_source_path)
            outputs.append((illustration_pdf_path,))
        if dry_run:
            return inputs, outputs
        if not os.path.isfile(illustration_source_path):
            message = 'the file {} does not exist.'
            message = message.format(illustration_source_path)
            self._io_manager._display(message)
            return [], []
        messages = self._format_messaging(inputs, outputs)
        self._io_manager._display(messages)
        if confirm:
            result = self._io_manager._confirm()
            if not result:
                return [], []
        result = self._io_manager.run_lilypond(illustration_source_path)
        subprocess_messages, candidate_messages = result
        return subprocess_messages, candidate_messages

    @Command(
        'mi',
        argument_name='current_directory',
        directories=('build'),
        outside_score=False,
        section='build',
        )
    def interpret_music(self, directory):
        r'''Interprets ``music.ly``.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        build_directory = os.path.join(score_directory, 'build')
        self._call_lilypond_on_file_ending_with(
            build_directory,
            'music.ly',
            )

    @Command(
        'pi',
        argument_name='current_directory',
        directories=('build'),
        outside_score=False,
        section='build',
        )
    def interpret_preface(self, directory):
        r'''Interprets ``preface.tex``.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        build_directory = os.path.join(score_directory, 'build')
        self._interpret_file_ending_with(build_directory, 'preface.tex')

    @Command(
        'si',
        argument_name='current_directory',
        directories=('build'),
        outside_score=False,
        section='build',
        )
    def interpret_score(self, directory):
        r'''Interprets ``score.tex``.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        build_directory = os.path.join(score_directory, 'build')
        self._interpret_file_ending_with(build_directory, 'score.tex')

    @Command('!', section='system')
    def invoke_shell(self):
        r'''Invokes shell.

        Returns none.
        '''
        statement = self._io_manager._handle_input(
            '$',
            include_chevron=False,
            include_newline=False,
            )
        statement = statement.strip()
        self._io_manager._invoke_shell(statement)

    @Command(
        'illm',
        argument_name='current_directory',
        description='illustrate file - make',
        file_='__illustrate__.py',
        outside_score=False,
        section='illustrate_file',
        )
    def make_illustrate_file(self, directory):
        r'''Makes illustrate file.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        score_package_name = os.path.basename(score_directory)
        material_package_name = os.path.basename(directory)
        source_path = os.path.join(
            configuration.abjad_ide_boilerplate_directory,
            '__illustrate_material__.py',
            )
        target_path = os.path.join(
            directory,
            '__illustrate__.py',
            )
        shutil.copyfile(source_path, target_path)
        with open(target_path, 'r') as file_pointer:
            template = file_pointer.read()
        completed_template = template.format(
            score_package_name=score_package_name,
            material_package_name=material_package_name,
            )
        with open(target_path, 'w') as file_pointer:
            file_pointer.write(completed_template)
        self._session._pending_redraw = True

    @Command(
        'lym',
        argument_name='current_directory',
        description='ly - make',
        file_='definition.py',
        outside_score=False,
        parent_directories=('materials',),
        section='ly',
        )
    def make_ly(self, directory, dry_run=False):
        r'''Makes illustration ly.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        definition_path = os.path.join(directory, 'definition.py')
        if not os.path.isfile(definition_path):
            message = 'File not found: {}.'
            message = message.format(definition_path)
            self._io_manager._display(message)
            return
        illustrate_file_path = os.path.join(directory, '__illustrate__.py')
        if not os.path.isfile(illustrate_file_path):
            message = 'File not found: {}.'
            message = message.format(illustrate_file_path)
            self._io_manager._display(message)
            return
        candidate_ly_path = os.path.join(
            directory,
            'illustration.candidate.ly'
            )
        source_make_ly_file = os.path.join(
            configuration.abjad_ide_boilerplate_directory,
            '__make_ly__.py',
            )
        target_make_ly_file = os.path.join(directory, '__make_ly__.py')
        temporary_files = (
            candidate_ly_path,
            target_make_ly_file,
            )
        for path in temporary_files:
            if os.path.exists(path):
                os.remove(path)
        ly_path = os.path.join(directory, 'illustration.ly')
        inputs, outputs = [], []
        if dry_run:
            inputs.append(definition_path)
            outputs.append(ly_path)
            return inputs, outputs
        with systemtools.FilesystemState(remove=temporary_files):
            shutil.copyfile(source_make_ly_file, target_make_ly_file)
            result = self._io_manager.interpret_file(
                target_make_ly_file,
                strip=False,
                )
            stdout_lines, stderr_lines = result
            if stderr_lines:
                self._io_manager._display_errors(stderr_lines)
                return
            if not os.path.isfile(candidate_ly_path):
                message = 'could not make {}.'
                message = message.format(candidate_ly_path)
                self._io_manager._display(message)
                return
            result = systemtools.TestManager.compare_files(
                candidate_ly_path,
                ly_path,
                )
            messages = self._make_candidate_messages(
                result,
                candidate_ly_path,
                ly_path,
                )
            self._io_manager._display(messages)
            if result:
                message = 'preserved {}.'.format(ly_path)
                self._io_manager._display(message)
                return
            else:
                message = 'overwriting {} ...'
                message = message.format(ly_path)
                self._io_manager._display(message)
                try:
                    shutil.move(
                        candidate_ly_path,
                        ly_path,
                        )
                except IOError:
                    pass
                if not self._session.is_test:
                    message = 'opening {} ...'
                    message = message.format(ly_path)
                    self._io_manager._display(message)
                    self._io_manager.open_file(ly_path)

    @Command(
        'pdfm',
        argument_name='current_directory',
        description='pdf - make',
        file_='definition.py',
        outside_score=False,
        parent_directories=('materials',),
        section='pdf',
        )
    def make_pdf(self, directory, dry_run=False):
        r'''Makes illustration PDF.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        definition_path = os.path.join(directory, 'definition.py')
        if not os.path.isfile(definition_path):
            message = 'File not found: {}.'
            message = message.format(definition_path)
            self._io_manager._display(message)
            return
        illustrate_file_path = os.path.join(directory, '__illustrate__.py')
        if not os.path.isfile(illustrate_file_path):
            message = 'File not found: {}.'
            message = message.format(illustrate_file_path)
            self._io_manager._display(message)
            return
        candidate_ly_path = os.path.join(
            directory,
            'illustration.candidate.ly'
            )
        ly_path = os.path.join(directory, 'illustration.ly')
        candidate_pdf_path = os.path.join(
            directory,
            'illustration.candidate.pdf'
            )
        pdf_path = os.path.join(directory, 'illustration.pdf')
        source_make_pdf_file = os.path.join(
            configuration.abjad_ide_boilerplate_directory,
            '__make_pdf__.py',
            )
        target_make_pdf_file = os.path.join(directory, '__make_pdf__.py')
        temporary_files = (
            candidate_ly_path,
            candidate_pdf_path,
            target_make_pdf_file,
            )
        for path in temporary_files:
            if os.path.exists(path):
                os.remove(path)
        inputs, outputs = [], []
        if dry_run:
            inputs.append(definition_path)
            outputs.append((ly_path, pdf_path))
            return inputs, outputs
        with systemtools.FilesystemState(remove=temporary_files):
            shutil.copyfile(source_make_pdf_file, target_make_pdf_file)
            message = 'interpreting {} ...'
            message = message.format(target_make_pdf_file)
            self._io_manager._display(message)
            result = self._io_manager.interpret_file(
                target_make_pdf_file,
                strip=False,
                )
            stdout_lines, stderr_lines = result
            if stderr_lines:
                self._io_manager._display_errors(stderr_lines)
                return
                
            if not os.path.isfile(candidate_ly_path):
                message = 'could not make {}.'
                message = message.format(candidate_ly_path)
                self._io_manager._display(message)
                return
            result = systemtools.TestManager.compare_files(
                candidate_ly_path,
                ly_path,
                )
            if result:
                messages = []
                messages.append('preserving {} ...'.format(ly_path))
                messages.append('preserving {} ...'.format(pdf_path))
                self._io_manager._display(messages)
                return
            else:
                message = 'overwriting {} ...'
                message = message.format(ly_path)
                self._io_manager._display(message)
                try:
                    shutil.move(candidate_ly_path, ly_path)
                except IOError:
                    message = 'could not overwrite {} with {}.'
                    message = message.format(ly_path, candidate_ly_path)
                    self._io_manager._display(message)
            if not os.path.isfile(candidate_pdf_path):
                message = 'could not make {}.'
                message = message.format(candidate_pdf_path)
                self._io_manager._display(message)
                return
            result = systemtools.TestManager.compare_files(
                candidate_pdf_path,
                pdf_path,
                )
            if result:
                message = 'preserving {} ...'.format(pdf_path)
                self._io_manager._display(message)
                return
            else:
                message = 'overwriting {} ...'
                message = message.format(pdf_path)
                self._io_manager._display(message)
                try:
                    shutil.move(candidate_pdf_path, pdf_path)
                except IOError:
                    message = 'could not overwrite {} with {}.'
                    message = message.format(pdf_path, candidate_pdf_path)
                    self._io_manager._display(message)
            if not self._session.is_test:
                message = 'opening {} ...'
                message = message.format(pdf_path)
                self._io_manager._display(message)
                self._io_manager.open_file(pdf_path)

    @Command(
        'new',
        argument_name='current_directory',
        is_hidden=False,
        never_in_score_directory=True,
        section='basic',
        )
    def new(self, directory):
        r'''Makes new asset.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        asset_identifier = self._directory_to_asset_identifier(directory)
        if self._is_score_directory(directory, 'scores'):
            self._make_score_package()
        elif asset_identifier == 'file':
            self._make_file(directory)
        elif asset_identifier == 'package':
            self._make_material_or_segment_package(directory)
        else:
            raise ValueError(directory)
        self._session._pending_menu_rebuild = True
        self._session._pending_redraw = True

    @Command(
        'io*',
        argument_name='current_directory',
        directories=('materials', 'segments'),
        outside_score=False,
        section='star',
        )
    def open_every_illustration_pdf(self, directory):
        r'''Opens ``illustration.pdf`` in every package.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        directories = self._list_visible_paths(directory)
        self._open_in_every_package(directories, 'illustration.pdf')

    @Command(
        'so*',
        argument_name='current_directory',
        in_score=False,
        outside_score='home',
        section='star',
        )
    def open_every_score_pdf(self, directory):
        r'''Opens ``score.pdf`` in every package.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        directories = self._list_visible_paths(directory)
        paths = []
        for directory in directories:
            inputs, outputs = self.open_score_pdf(directory, dry_run=True)
            paths.extend(inputs)
        messages = ['will open ...']
        paths = [self._tab + _ for _ in paths]
        messages.extend(paths)
        self._io_manager._display(messages)
        result = self._io_manager._confirm()
        if not result:
            return
        if paths:
            self._io_manager.open_file(paths)

    @Command(
        'pdf',
        argument_name='current_directory',
        description='pdf - open',
        file_='illustration.pdf',
        outside_score=False,
        section='pdf',
        )
    def open_pdf(self, directory):
        r'''Opens illustration PDF.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        file_path = os.path.join(directory, 'illustration.pdf')
        self._io_manager.open_file(file_path)

    @Command(
        'so',
        argument_name='current_directory',
        in_score_directory_only=True,
        outside_score=False,
        section='pdf',
        )
    def open_score_pdf(self, directory, dry_run=False):
        r'''Opens ``score.pdf``.

        Returns none.
        '''
        file_name = 'score.pdf'
        directory = os.path.join(directory, 'distribution')
        path = self._get_file_path_ending_with(directory, file_name)
        if not path:
            directory = os.path.join(directory, 'build')
            path = self._get_file_path_ending_with(
                directory,
                file_name,
                )
        if dry_run:
            inputs, outputs = [], []
            if path:
                inputs = [path]
            return inputs, outputs
        if path:
            self._io_manager.open_file(path)
        else:
            message = "no score.pdf file found"
            message += ' in either distribution/ or build/ directories.'
            self._io_manager._display(message)

    @Command(
        'sp',
        argument_name='current_directory',
        directories=('build'),
        outside_score=False,
        section='build',
        )
    def push_score_pdf_to_distribution_directory(self, directory):
        r'''Pushes ``score.pdf`` to distribution directory.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        score_directory = self._to_score_directory(directory)
        path = os.path.join(score_directory, 'build')
        build_score_path = os.path.join(path, 'score.pdf')
        if not os.path.exists(build_score_path):
            message = 'does not exist: {!r}.'
            message = message.format(build_score_path)
            self._io_manager._display(message)
            return
        score_package_name = os.path.basename(score_directory)
        score_package_name = score_package_name.replace('_', '-')
        distribution_file_name = '{}-score.pdf'.format(score_package_name)
        distribution_directory = os.path.join(score_directory, 'distribution')
        distribution_score_path = os.path.join(
            distribution_directory,
            distribution_file_name,
            )
        shutil.copyfile(build_score_path, distribution_score_path)
        messages = []
        messages.append('Copied')
        message = ' FROM: {}'.format(build_score_path)
        messages.append(message)
        message = '   TO: {}'.format(distribution_score_path)
        messages.append(message)
        self._io_manager._display(messages)

    @Command('q', description='quit', section='back-home-quit')
    def quit_abjad_ide(self):
        r'''Quits Abjad IDE.

        Returns none.
        '''
        self._session._is_quitting = True

    @Command(
        'rm',
        argument_name='current_directory',
        is_hidden=False,
        never_in_score_directory=True,
        section='basic',
        )
    def remove(self, directory):
        r'''Removes asset(s).

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        paths = self._select_visible_paths(directory, 'to remove')
        if not paths:
            return
        count = len(paths)
        messages = []
        if count == 1:
            message = 'will remove {}'.format(paths[0])
            messages.append(message)
        else:
            messages.append('will remove ...')
            for path in paths:
                message = '    {}'.format(path)
                messages.append(message)
        self._io_manager._display(messages)
        if count == 1:
            confirmation_string = 'remove'
        else:
            confirmation_string = 'remove {}'
            confirmation_string = confirmation_string.format(count)
        message = "type {!r} to proceed"
        message = message.format(confirmation_string)
        getter = self._io_manager._make_getter()
        getter.append_string(message)
        if self._session.confirm:
            result = getter._run(io_manager=self._io_manager)
            if result is None:
                return
            if not result == confirmation_string:
                return
        for path in paths:
            self._remove(path)
        self._session._pending_menu_rebuild = True
        self._session._pending_redraw = True

    @Command(
        'ren',
        argument_name='current_directory',
        is_hidden=False,
        never_in_score_directory=True,
        section='basic',
        )
    def rename(self, directory):
        r'''Renames asset.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        source_path = self._select_visible_path(directory, 'to rename')
        if self._is_score_directory(source_path, 'inner'):
            source_path = os.path.dirname(source_path)
        if not source_path:
            return
        message = 'Will rename]> {}'
        trimmed_source_path = self._trim_scores_directory(source_path)
        message = message.format(trimmed_source_path)
        self._io_manager._display(message)
        getter = self._io_manager._make_getter()
        getter.append_string('new name or return to cancel')
        original_target_name = getter._run(io_manager=self._io_manager)
        if not original_target_name:
            return
        target_name = self._coerce_name(directory, original_target_name)
        source_name = os.path.basename(source_path)
        target_path = os.path.join(
            os.path.dirname(source_path),
            target_name,
            )
        if os.path.exists(target_path):
            message = 'path already exists: {!r}.'
            message = message.format(target_path)
            self._io_manager._display(message)
            return
        messages = []
        messages.append('will rename ...')
        message = ' FROM: {}'.format(source_path)
        messages.append(message)
        message = '   TO: {}'.format(target_path)
        messages.append(message)
        self._io_manager._display(messages)
        if not self._io_manager._confirm():
            return
        shutil.move(source_path, target_path)
        if os.path.isdir(target_path):
            for directory_entry in sorted(os.listdir(target_path)):
                if not directory_entry.endswith('.py'):
                    continue
                path = os.path.join(target_path, directory_entry)
                self._replace_in_file(
                    path,
                    source_name,
                    target_name,
                    )
        if self._is_score_directory(target_path, 'outer'):
            false_inner_path = os.path.join(target_path, source_name)
            assert os.path.exists(false_inner_path)
            correct_inner_path = os.path.join(target_path, target_name)
            shutil.move(false_inner_path, correct_inner_path)
            self._add_metadatum(
                correct_inner_path, 
                'title',
                original_target_name,
                )
            for directory_entry in sorted(os.listdir(correct_inner_path)):
                if not directory_entry.endswith('.py'):
                    continue
                path = os.path.join(correct_inner_path, directory_entry)
                self._replace_in_file(
                    path,
                    source_name,
                    target_name,
                    )
        self._session._pending_menu_rebuild = True
        self._session._pending_redraw = True

    @Command(
        'ws',
        argument_name='current_directory',
        directories=(
            'build',
            'distribution',
            'etc',
            'makers',
            'materials',
            'scores',
            'segments',
            'stylesheets',
            'test',
            ),
        outside_score='home',
        section='view',
        )
    def set_view(self, directory):
        r'''Sets view.

        Returns none.
        '''
        assert os.path.isdir(directory), repr(directory)
        view_name = self._select_view(directory)
        if view_name is None:
            return
        if view_name == 'none':
            view_name = None
        view_directory = self._session.manifest_current_directory
        metadatum_name = 'view_name'
        self._add_metadatum(
            view_directory,
            metadatum_name,
            view_name,
            )