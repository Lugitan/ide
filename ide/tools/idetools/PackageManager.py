# -*- encoding: utf-8 -*-
from __future__ import print_function
import os
import shutil
import time
from abjad.tools import stringtools
from abjad.tools import systemtools
from ide.tools.idetools.AbjadIDEConfiguration import AbjadIDEConfiguration
from ide.tools.idetools.Controller import Controller
from ide.tools.idetools.Command import Command
configuration = AbjadIDEConfiguration()


class PackageManager(Controller):
    r'''Package manager.
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_breadcrumb_callback',
        '_optional_directories',
        '_optional_files',
        '_package_creation_callback',
        '_path',
        '_required_directories',
        '_required_files',
        )

    ### INITIALIZER ###

    def __init__(self, path=None, session=None):
        assert session is not None
        assert path is not None and os.path.sep in path
        superclass = super(PackageManager, self)
        superclass.__init__(session=session)
        self._breadcrumb_callback = None
        self._optional_directories = (
            '__pycache__',
            'test',
            )
        self._optional_files = ()
        self._package_creation_callback = None
        self._path = path
        self._required_directories = ()
        self._required_files = (
            '__init__.py',
            '__metadata__.py',
            )

    ### SPECIAL METHODS ###

    def __repr__(self):
        r'''Gets interpreter representation of manager.

        Returns string.
        '''
        return '{}({!r})'.format(type(self).__name__, self._path)

    ### PRIVATE PROPERTIES ###

    @property
    def _breadcrumb(self):
        if self._breadcrumb_callback is not None:
            return self._breadcrumb_callback(
                self._session,
                self._metadata_py_path,
                )
        return self._space_delimited_lowercase_name

    @property
    def _definition_py_path(self):
        return os.path.join(self._path, 'definition.py')

    @property
    def _illustrate_py_path(self):
        return os.path.join(self._path, '__illustrate__.py')

    @property
    def _illustration_ly_path(self):
        return os.path.join(self._path, 'illustration.ly')

    @property
    def _illustration_pdf_path(self):
        return os.path.join(self._path, 'illustration.pdf')

    @property
    def _inner_path(self):
        return os.path.join(self._outer_path, self._package_name)

    @property
    def _metadata_py_path(self):
        return os.path.join(self._path, '__metadata__.py')

    @property
    def _outer_path(self):
        if self._path.startswith(configuration.composer_scores_directory):
            return os.path.join(
                configuration.composer_scores_directory,
                self._package_name
                )
        else:
            return os.path.join(
                configuration.abjad_ide_example_scores_directory,
                self._package_name
                )

    @property
    def _package_name(self):
        return os.path.basename(self._path)

    @property
    def _repository_add_command(self):
        command = 'git add -A {}'
        command = command.format(self._path)
        return command

    @property
    def _repository_update_command(self):
        root_directory = self._get_repository_root_directory(
            self._session,
            self._path,
            )
        command = 'git pull {}'
        command = command.format(root_directory)
        return command

    @property
    def _shell_remove_command(self):
        if self._session._io_manager.find_executable('trash'):
            return 'trash'
        return 'rm'

    @property
    def _space_delimited_lowercase_name(self):
        base_name = os.path.basename(self._path)
        result = base_name.replace('_', ' ')
        return result

    ### PRIVATE METHODS ###

    def _configure_as_material_package_manager(self):
        self._basic_breadcrumb = 'MATERIALS'
        self._optional_files = (
            '__illustrate__.py',
            'illustration.ly',
            'illustration.pdf',
            'maker.py',
            )
        self._required_files = (
            '__init__.py',
            '__metadata__.py',
            'definition.py',
            )

    def _configure_as_score_package_manager(self):
        self._basic_breadcrumb = 'SCORES'
        self._breadcrumb_callback = self._get_title_metadatum
        self._optional_directories = (
            '__pycache__',
            'etc',
            'test',
            )
        self._package_creation_callback = \
            self._make_score_into_installable_package
        self._required_directories = (
            'build',
            'distribution',
            'makers',
            'materials',
            'segments',
            'stylesheets',
            )
        self._required_files = (
            '__init__.py',
            '__metadata__.py',
            os.path.join('makers', '__init__.py'),
            os.path.join('materials', '__init__.py'),
            os.path.join('segments', '__init__.py'),
            )

    def _configure_as_segment_package_manager(self):
        self._basic_breadcrumb = 'SEGMENTS'
        self._breadcrumb_callback = self._get_name_metadatum
        self._optional_files = (
            'illustration.ly',
            'illustration.pdf',
            )
        self._required_files = (
            '__init__.py',
            '__metadata__.py',
            'definition.py',
            )

    def _get_current_directory(self):
        return self._path

    def _list_visible_asset_paths(self):
        return [self._path]

    def _make_asset_menu_section(self, menu):
        directory_entries = self._list_directory(self._path, smart_sort=True)
        menu_entries = []
        for directory_entry in directory_entries:
            clean_directory_entry = directory_entry
            if directory_entry.endswith('/'):
                clean_directory_entry = directory_entry[:-1]
            path = os.path.join(self._path, clean_directory_entry)
            menu_entry = (directory_entry, None, None, path)
            menu_entries.append(menu_entry)
        menu.make_asset_section(menu_entries=menu_entries)

    def _make_package(self):
        assert not os.path.exists(self._path)
        os.mkdir(self._path)
        with self._session._io_manager._silent(self._session):
            self.check_package(
                return_supply_messages=True,
                supply_missing=True,
                )
        if self._package_creation_callback is not None:
            self._package_creation_callback(
                self._session,
                self._inner_path,
                self._outer_path,
                )

    def _make_score_into_installable_package(
        self,
        session,
        inner_path,
        outer_path,
        ):
        old_path = outer_path
        temporary_path = os.path.join(
            os.path.dirname(outer_path),
            '_TEMPORARY_SCORE_PACKAGE',
            )
        shutil.move(old_path, temporary_path)
        shutil.move(temporary_path, inner_path)
        self._write_enclosing_artifacts(
            session,
            inner_path,
            outer_path,
            )

    def _rename(self, new_path):
        if self._is_in_git_repository(self._session, self._path):
            if self._is_git_unknown(self._session, self._path):
                command = 'mv {} {}'
            else:
                command = 'git mv --force {} {}'
        else:
            command = 'mv {} {}'
        command = command.format(self._path, new_path)
        with systemtools.TemporaryDirectoryChange(directory=self._path):
            process = self._session._io_manager.make_subprocess(command)
        self._session._io_manager._read_from_pipe(process.stdout)
        self._path = new_path

    def _rename_interactively(
        self,
        file_extension=None,
        file_name_callback=None,
        force_lowercase=True,
        ):
        base_name = os.path.basename(self._path)
        line = 'current name: {}'.format(base_name)
        self._session._io_manager._display(line)
        getter = self._session._io_manager._make_getter()
        getter.append_string('new name')
        new_package_name = getter._run()
        if self._session.is_backtracking or new_package_name is None:
            return
        new_package_name = stringtools.strip_diacritics(new_package_name)
        if file_name_callback:
            new_package_name = file_name_callback(new_package_name)
        new_package_name = new_package_name.replace(' ', '_')
        if force_lowercase:
            new_package_name = new_package_name.lower()
        if file_extension and not new_package_name.endswith(file_extension):
            new_package_name = new_package_name + file_extension
        lines = []
        line = 'current name: {}'.format(base_name)
        lines.append(line)
        line = 'new name:     {}'.format(new_package_name)
        lines.append(line)
        self._session._io_manager._display(lines)
        result = self._session._io_manager._confirm()
        if self._session.is_backtracking or not result:
            return
        new_directory = os.path.join(
            os.path.dirname(self._path),
            new_package_name,
            )
        if os.path.exists(new_directory):
            message = 'path already exists: {!r}.'
            message = message.format(new_directory)
            self._session._io_manager._display(message)
            return
        shutil.move(self._path, new_directory)
        # update path name to reflect change
        self._path = new_directory
        self._session._is_backtracking_locally = True

    def _run(self):
        controller = self._session._io_manager._controller(
            consume_local_backtrack=True,
            controller=self,
            )
        directory = systemtools.TemporaryDirectoryChange(self._path)
        with controller, directory:
                self._enter_run()
                self._session._pending_redraw = True
                while True:
                    result = self._session.navigation_command_name
                    if not result:
                        menu = self._make_main_menu()
                        result = menu._run()
                        self._handle_pending_redraw_directive(result)
                        self._handle_wrangler_navigation_directive(result)
                    if self._exit_run():
                        break
                    elif not result:
                        continue
                    self._handle_input(result)
                    if self._exit_run():
                        break

    def _space_delimited_lowercase_name_to_asset_name(
        self, space_delimited_lowercase_name):
        space_delimited_lowercase_name = space_delimited_lowercase_name.lower()
        asset_name = space_delimited_lowercase_name.replace(' ', '_')
        return asset_name

    def _test_add(self):
        assert self._is_up_to_date(self._session, self._path)
        path_1 = os.path.join(self._path, 'tmp_1.py')
        path_2 = os.path.join(self._path, 'tmp_2.py')
        with systemtools.FilesystemState(remove=[path_1, path_2]):
            with open(path_1, 'w') as file_pointer:
                file_pointer.write('')
            with open(path_2, 'w') as file_pointer:
                file_pointer.write('')
            assert os.path.exists(path_1)
            assert os.path.exists(path_2)
            assert not self._is_up_to_date(self._session, self._path)
            assert self._get_unadded_asset_paths(
                self._session, self._path) == [path_1, path_2]
            assert self._get_added_asset_paths() == []
            with self._session._io_manager._silent(self._session):
                self.add()
            assert self._get_unadded_asset_paths(
                self._session, self._path) == []
            assert self._get_added_asset_paths() == [path_1, path_2]
            with self._session._io_manager._silent(self._session):
                self._unadd_added_assets()
            assert self._get_unadded_asset_paths(
                self._session, self._path) == [path_1, path_2]
            assert self._get_added_asset_paths() == []
        assert self._is_up_to_date(self._session, self._path)
        return True

    def _test_revert(self):
        assert self._is_up_to_date(self._session, self._path)
        assert self._get_modified_asset_paths(self._session, self._path) == []
        file_name = self._find_first_file_name(self._path)
        if not file_name:
            return
        file_path = os.path.join(self._path, file_name)
        with systemtools.FilesystemState(keep=[file_path]):
            with open(file_path, 'a') as file_pointer:
                string = '# extra text appended during testing'
                file_pointer.write(string)
            assert not self._is_up_to_date(self._session, self._path)
            assert self._get_modified_asset_paths(
                self._session, self._path) == [file_path]
            with self._session._io_manager._silent(self._session):
                self.revert()
        assert self._get_modified_asset_paths(self._session, self._path) == []
        assert self._is_up_to_date(self._session, self._path)
        return True

    def _unadd_added_assets(self):
        paths = []
        paths.extend(self._get_added_asset_paths())
        paths.extend(self._get_modified_asset_paths(self._session, self._path))
        commands = []
        if self._is_git_versioned():
            for path in paths:
                command = 'git reset -- {}'.format(path)
                commands.append(command)
        else:
            raise ValueError(self)
        command = ' && '.join(commands)
        with systemtools.TemporaryDirectoryChange(directory=self._path):
            self._session._io_manager.spawn_subprocess(command)

    def _update_order_dependent_segment_metadata(self):
        wrangler = self._session._abjad_ide._segment_package_wrangler
        wrangler._update_order_dependent_segment_metadata()

    def _write_enclosing_artifacts(self, session, inner_path, outer_path):
        # CAUTION
        self._path = inner_path
        self._copy_boilerplate(
            session,
            'README.md',
            outer_path,
            )
        self._copy_boilerplate(
            session,
            'requirements.txt',
            outer_path,
            )
        self._copy_boilerplate(
            session,
            'setup.cfg',
            outer_path,
            )
        replacements = {
            'COMPOSER_EMAIL': configuration.composer_email,
            'COMPOSER_FULL_NAME': configuration.composer_full_name,
            'COMPOSER_GITHUB_USERNAME': configuration.composer_github_username,
            'PACKAGE_NAME': self._package_name,
            }
        self._copy_boilerplate(
            session,
            'setup.py',
            outer_path,
            replacements=replacements,
            )

    ### PUBLIC METHODS ###

    @Command(
        'dc', 
        file_='definition.py',
        outside_score=False,
        section='package', 
        )
    def check_definition_py(self, dry_run=False):
        r'''Checks ``definition.py``.

        Display errors generated during interpretation.
        '''
        if not os.path.isfile(self._definition_py_path):
            message = 'File not found: {}.'
            message = message.format(self._definition_py_path)
            self._session._io_manager._display(message)
            return
        inputs, outputs = [], []
        if dry_run:
            inputs.append(self._definition_py_path)
            return inputs, outputs
        with self._session._io_manager._silent(self._session):
            stdout_lines, stderr_lines = self._session._io_manager.interpret_file(
                self._definition_py_path)
        if stderr_lines:
            messages = [self._definition_py_path + ' FAILED:']
            messages.extend('    ' + _ for _ in stderr_lines)
            self._session._io_manager._display(messages)
        else:
            message = '{} OK.'.format(self._definition_py_path)
            self._session._io_manager._display(message)

    @Command(
        'ck', 
        outside_score=False,
        section='package', 
        )
    def check_package(
        self,
        problems_only=None,
        return_messages=False,
        return_supply_messages=False,
        supply_missing=None,
        ):
        r'''Checks package.

        Returns none.
        '''
        if problems_only is None:
            prompt = 'show problem assets only?'
            result = self._session._io_manager._confirm(prompt)
            if self._session.is_backtracking or result is None:
                return
            problems_only = bool(result)
        tab = self._session._io_manager._tab
        optional_directories, optional_files = [], []
        missing_directories, missing_files = [], []
        required_directories, required_files = [], []
        supplied_directories, supplied_files = [], []
        unrecognized_directories, unrecognized_files = [], []
        names = self._list_directory(self._path)
        if 'makers' in names:
            makers_initializer = os.path.join('makers', '__init__.py')
            if makers_initializer in self._required_files:
                path = os.path.join(self._path, makers_initializer)
                if os.path.isfile(path):
                    required_files.append(path)
        if 'materials' in names:
            materials_initializer = os.path.join('materials', '__init__.py')
            if materials_initializer in self._required_files:
                path = os.path.join(self._path, materials_initializer)
                if os.path.isfile(path):
                    required_files.append(path)
        if 'segments' in names:
            segments_initializer = os.path.join('segments', '__init__.py')
            if segments_initializer in self._required_files:
                path = os.path.join(self._path, segments_initializer)
                if os.path.isfile(path):
                    required_files.append(path)
        for name in names:
            path = os.path.join(self._path, name)
            if os.path.isdir(path):
                if name in self._required_directories:
                    required_directories.append(path)
                elif name in self._optional_directories:
                    optional_directories.append(path)
                else:
                    unrecognized_directories.append(path)
            elif os.path.isfile(path):
                if name in self._required_files:
                    required_files.append(path)
                elif name in self._optional_files:
                    optional_files.append(path)
                else:
                    unrecognized_files.append(path)
            else:
                raise TypeError(path)
        recognized_directories = required_directories + optional_directories
        recognized_files = required_files + optional_files
        for required_directory in self._required_directories:
            path = os.path.join(self._path, required_directory)
            if path not in recognized_directories:
                missing_directories.append(path)
        for required_file in self._required_files:
            path = os.path.join(self._path, required_file)
            if path not in recognized_files:
                missing_files.append(path)
        messages = []
        if not problems_only:
            messages_ = self._format_ratio_check_messages(
                required_directories,
                self._required_directories,
                'required directory',
                participal='found',
                tab=self._session._io_manager._tab,
                )
            messages.extend(messages_)
        if missing_directories:
            messages_ = self._format_ratio_check_messages(
                missing_directories,
                self._required_directories,
                'required directory',
                'missing',
                tab=self._session._io_manager._tab,
                )
            messages.extend(messages_)
        if not problems_only:
            messages_ = self._format_ratio_check_messages(
                required_files,
                self._required_files,
                'required file',
                'found',
                tab=self._session._io_manager._tab,
                )
            messages.extend(messages_)
        if missing_files:
            messages_ = self._format_ratio_check_messages(
                missing_files,
                self._required_files,
                'required file',
                'missing',
                tab=self._session._io_manager._tab,
                )
            messages.extend(messages_)
        if not problems_only:
            messages_ = self._format_counted_check_messages(
                optional_directories,
                'optional directory',
                participal='found',
                tab=self._session._io_manager._tab
                )
            messages.extend(messages_)
            messages_ = self._format_counted_check_messages(
                optional_files,
                'optional file',
                participal='found',
                tab=self._session._io_manager._tab
                )
            messages.extend(messages_)
        messages_ = self._format_counted_check_messages(
            unrecognized_directories,
            'unrecognized directory',
            participal='found',
            tab=self._session._io_manager._tab
            )
        messages.extend(messages_)
        messages_ = self._format_counted_check_messages(
            unrecognized_files,
            'unrecognized file',
            participal='found',
            tab=self._session._io_manager._tab
            )
        messages.extend(messages_)
        tab = self._session._io_manager._tab
        messages = [tab + _ for _ in messages]
        name = self._path_to_asset_menu_display_string(self._path)
        found_problems = (
            missing_directories or
            missing_files or
            unrecognized_directories or
            unrecognized_files
            )
        count = len(names)
        wranglers = self._get_directory_wranglers(
            self._session,
            self._path,
            )
        if wranglers or not return_messages:
            message = 'top level ({} assets):'.format(count)
            if not found_problems:
                message = '{} OK'.format(message)
            messages.insert(0, message)
            messages = [stringtools.capitalize_start(_) for _ in messages]
            messages = [tab + _ for _ in messages]
        message = '{}:'.format(name)
        if not wranglers and not found_problems and return_messages:
            message = '{} OK'.format(message)
        messages.insert(0, message)
        if wranglers:
            controller = self._session._io_manager._controller(
                controller=self,
                current_score_directory=self._path,
                )
            silence = self._session._io_manager._silent(self._session)
            with controller, silence:
                tab = self._session._io_manager._tab
                for wrangler in wranglers:
                    self._session._io_manager._display(repr(wrangler))
                    if wrangler._asset_identifier == 'file':
                        result = wrangler._check_every_file()
                    else:
                        result = wrangler.check_every_package(
                            indent=1,
                            problems_only=problems_only,
                            supply_missing=False,
                            )
                    messages_, missing_directories_, missing_files_ = result
                    missing_directories.extend(missing_directories_)
                    missing_files.extend(missing_files_)
                    messages_ = [
                        stringtools.capitalize_start(_) for _ in messages_]
                    messages_ = [tab + _ for _ in messages_]
                    messages.extend(messages_)
        if return_messages:
            return messages, missing_directories, missing_files
        else:
            self._session._io_manager._display(messages)
        if not missing_directories + missing_files:
            return messages, missing_directories, missing_files
        if supply_missing is None:
            directory_count = len(missing_directories)
            file_count = len(missing_files)
            directories = stringtools.pluralize('directory', directory_count)
            files = stringtools.pluralize('file', file_count)
            if missing_directories and missing_files:
                prompt = 'supply missing {} and {}?'.format(directories, files)
            elif missing_directories:
                prompt = 'supply missing {}?'.format(directories)
            elif missing_files:
                prompt = 'supply missing {}?'.format(files)
            else:
                raise ValueError
            result = self._session._io_manager._confirm(prompt)
            if self._session.is_backtracking or result is None:
                return
            supply_missing = bool(result)
        if not supply_missing:
            return messages, missing_directories, missing_files
        messages = []
        messages.append('Made:')
        for missing_directory in missing_directories:
            os.makedirs(missing_directory)
            gitignore_path = os.path.join(missing_directory, '.gitignore')
            with open(gitignore_path, 'w') as file_pointer:
                file_pointer.write('')
            message = tab + missing_directory
            messages.append(message)
            supplied_directories.append(missing_directory)
        for missing_file in missing_files:
            if missing_file.endswith('__init__.py'):
                if self._basic_breadcrumb == 'scores':
                    lines = self._get_score_initializer_file_lines(
                        missing_file)
                else:
                    lines = [self._unicode_directive]
            elif missing_file.endswith('__metadata__.py'):
                lines = []
                lines.append(self._unicode_directive)
                lines.append('from abjad import *')
                lines.append('')
                lines.append('')
                lines.append(
                    'metadata = datastructuretools.TypedOrderedDict()')
            elif missing_file.endswith('__views__.py'):
                lines = []
                lines.append(self._unicode_directive)
                lines.append(self._abjad_import_statement)
                lines.append('from ide.tools import idetools')
                lines.append('')
                lines.append('')
                line = 'view_inventory = idetools.ViewInventory([])'
                lines.append(line)
            elif missing_file.endswith('definition.py'):
                source_path = os.path.join(
                    configuration.abjad_ide_boilerplate_directory,
                    'definition.py',
                    )
                with open(source_path, 'r') as file_pointer:
                    lines = file_pointer.readlines()
                lines = [_.strip() for _ in lines]
            else:
                message = 'do not know how to make stub for {}.'
                message = message.format(missing_file)
                raise ValueError(message)
            contents = '\n'.join(lines)
            with open(missing_file, 'w') as file_pointer:
                file_pointer.write(contents)
            message = tab + missing_file
            messages.append(message)
            supplied_files.append(missing_file)
        if return_supply_messages:
            return messages, supplied_directories, supplied_files
        else:
            self._session._io_manager._display(messages)
        return messages, supplied_directories, supplied_files

    @Command(
        'de', 
        file_='definition.py', 
        outside_score=False,
        section='package', 
        )
    def edit_definition_py(self):
        r'''Edits ``definition.py``.

        Returns none.
        '''
        self._session._io_manager.edit(self._definition_py_path)

    @Command(
        'le', 
        description='edit __illustrate__.py', 
        file_='__illustrate__.py',
        outside_score=False,
        section='package',
        )
    def edit_illustrate_py(self):
        r'''Edits ``__illustrate.py__``.

        Returns none.
        '''
        self._session._io_manager.edit(self._illustrate_py_path)

    @Command(
        'ie', 
        file_='illustration.ly', 
        outside_score=False, 
        section='package',
        )
    def edit_illustration_ly(self):
        r'''Opens ``illustration.ly``.

        Returns none.
        '''
        self._session._io_manager.open_file(self._illustration_ly_path)

    @Command(
        'gl', 
        description='generate __illustrate__.py', 
        file_='__illustrate__.py',
        outside_score=False,
        section='package',
        )
    def generate_illustrate_py(self):
        r'''Generates ``__illustrate.py__``.

        Returns none.
        '''
        message = 'will generate {}.'
        message = message.format(self._illustrate_py_path)
        self._session._io_manager._display(message)
        result = self._session._io_manager._confirm()
        if self._session.is_backtracking or not result:
            return
        lines = []
        lines.append(self._abjad_import_statement)
        line = 'from output import {}'
        line = line.format(self._package_name)
        lines.append(line)
        lines.append('')
        lines.append('')
        line = 'triple = scoretools.make_piano_score_from_leaves({})'
        line = line.format(self._package_name)
        lines.append(line)
        line = 'score, treble_staff, bass_staff = triple'
        lines.append(line)
        line = 'illustration = lilypondfiletools.'
        line += 'make_basic_lilypond_file(score)'
        lines.append(line)
        contents = '\n'.join(lines)
        with open(self._illustrate_py_path, 'w') as file_pointer:
            file_pointer.write(contents)
        message = 'generated {}.'
        message = message.format(self._illustrate_py_path)
        self._session._io_manager._display(message)

    @Command(
        'i', 
        file_='definition.py',
        outside_score=False,
        parent_directories=('segments',),
        section='package', 
        )
    def illustrate_definition_py(self, dry_run=False):
        r'''Illustrates ``definition.py``.

        Makes ``illustration.ly`` and ``illustration.pdf``.

        Returns none.
        '''
        if not os.path.isfile(self._definition_py_path):
            message = 'File not found: {}.'
            message = message.format(self._definition_py_path)
            self._session._io_manager._display(message)
            return
        self._update_order_dependent_segment_metadata()
        boilerplate_path = os.path.join(
            configuration.abjad_ide_boilerplate_directory,
            '__illustrate_segment__.py',
            )
        illustrate_path = os.path.join(
            self._path,
            '__illustrate_segment__.py',
            )
        candidate_ly_path = os.path.join(
            self._path,
            'illustration.candidate.ly'
            )
        candidate_pdf_path = os.path.join(
            self._path,
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
        illustration_ly_path = os.path.join(
            self._path,
            'illustration.ly',
            )
        illustration_pdf_path = os.path.join(
            self._path,
            'illustration.pdf',
            )
        inputs, outputs = [], []
        if dry_run:
            inputs.append(self._definition_py_path)
            outputs.append((illustration_ly_path, illustration_pdf_path))
            return inputs, outputs
        with systemtools.FilesystemState(remove=temporary_files):
            shutil.copyfile(boilerplate_path, illustrate_path)
            previous_segment_manager = self._get_previous_segment_manager(
                self._session,
                self._path,
                )
            if previous_segment_manager is None:
                statement = 'previous_segment_metadata = None'
            else:
                score_name = self._session.current_score_directory
                score_name = os.path.basename(score_name)
                previous_segment_name = previous_segment_manager._path
                previous_segment_name = os.path.basename(previous_segment_name)
                statement = 'from {}.segments.{}.__metadata__'
                statement += ' import metadata as previous_segment_metadata'
                statement = statement.format(score_name, previous_segment_name)
            self._replace_in_file(
                illustrate_path,
                'PREVIOUS_SEGMENT_METADATA_IMPORT_STATEMENT',
                statement,
                )
            with self._session._io_manager._silent(self._session):
                start_time = time.time()
                result = self._session._io_manager.interpret_file(
                    illustrate_path,
                    strip=False,
                    )
                stop_time = time.time()
                total_time = stop_time - start_time
            stdout_lines, stderr_lines = result
            if stderr_lines:
                self._session._io_manager._display_errors(stderr_lines)
                return
            message = 'total time: {} seconds.'
            message = message.format(int(total_time))
            self._session._io_manager._display(message)
            if not os.path.exists(illustration_pdf_path):
                messages = []
                messages.append('Wrote ...')
                tab = self._session._io_manager._tab
                if os.path.exists(candidate_ly_path):
                    shutil.move(candidate_ly_path, illustration_ly_path)
                    messages.append(tab + illustration_ly_path)
                if os.path.exists(candidate_pdf_path):
                    shutil.move(candidate_pdf_path, illustration_pdf_path)
                    messages.append(tab + illustration_pdf_path)
                self._session._io_manager._display(messages)
            else:
                result = systemtools.TestManager.compare_files(
                candidate_pdf_path,
                illustration_pdf_path,
                )
                messages = self._make_candidate_messages(
                    self._session,
                    result,
                    candidate_pdf_path,
                    illustration_pdf_path,
                    )
                self._session._io_manager._display(messages)
                if result:
                    message = 'preserved {}.'.format(illustration_pdf_path)
                    self._session._io_manager._display(message)
                    return
                else:
                    message = 'overwrite existing PDF with candidate PDF?'
                    result = self._session._io_manager._confirm(message=message)
                    if self._session.is_backtracking or not result:
                        return
                    try:
                        shutil.move(candidate_ly_path, illustration_ly_path)
                    except IOError:
                        pass
                    try:
                        shutil.move(candidate_pdf_path, illustration_pdf_path)
                    except IOError:
                        pass

    @Command(
        'ii', 
        file_='illustration.ly',
        outside_score=False,
        section='package', 
        )
    def interpret_illustration_ly(self, dry_run=False):
        r'''Interprets ``illustration.ly``.

        Makes ``illustration.pdf``.

        Returns pair. List of STDERR messages from LilyPond together
        with list of candidate messages.
        '''
        inputs, outputs = [], []
        if os.path.isfile(self._illustration_ly_path):
            inputs.append(self._illustration_ly_path)
            outputs.append((self._illustration_pdf_path,))
        if dry_run:
            return inputs, outputs
        if not os.path.isfile(self._illustration_ly_path):
            message = 'The file {} does not exist.'
            message = message.format(self._illustration_ly_path)
            self._session._io_manager._display(message)
            return [], []
        messages = self._format_messaging(inputs, outputs)
        self._session._io_manager._display(messages)
        result = self._session._io_manager._confirm()
        if self._session.is_backtracking or not result:
            return [], []
        result = self._session._io_manager.run_lilypond(self._illustration_ly_path)
        subprocess_messages, candidate_messages = result
        return subprocess_messages, candidate_messages

    @Command(
        'io', 
        file_='illustration.pdf',
        outside_score=False,
        section='package', 
        )
    def open_illustration_pdf(self):
        r'''Opens ``illustration.pdf``.

        Returns none.
        '''
        self._session._io_manager.open_file(self._illustration_pdf_path)

    @Command(
        'so', 
        in_score_directory_only=True,
        outside_score=False,
        section='package', 
        )
    def open_score_pdf(self, dry_run=False):
        r'''Opens ``score.pdf``.

        Returns none.
        '''
        with self._session._io_manager._make_interaction(
            self._session,
            dry_run=dry_run,
            ):
            file_name = 'score.pdf'
            directory = os.path.join(self._path, 'distribution')
            manager = self._session._io_manager._make_package_manager(directory)
            path = manager._get_file_path_ending_with(manager._path, file_name)
            if not path:
                directory = os.path.join(self._path, 'build')
                manager = self._session._io_manager._make_package_manager(directory)
                path = manager._get_file_path_ending_with(
                    manager._path, 
                    file_name,
                    )
            if dry_run:
                inputs, outputs = [], []
                if path:
                    inputs = [path]
                return inputs, outputs
            if path:
                self._session._io_manager.open_file(path)
            else:
                message = "no score.pdf file found"
                message += ' in either distribution/ or build/ directories.'
                self._session._io_manager._display(message)