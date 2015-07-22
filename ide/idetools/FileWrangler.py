# -*- encoding: utf-8 -*-
import glob
import os
import shutil
from abjad.tools import lilypondfiletools
from abjad.tools import stringtools
from abjad.tools import systemtools
from ide.idetools.Wrangler import Wrangler


class FileWrangler(Wrangler):
    r'''File wrangler.
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_extension',
        '_file_name_predicate',
        '_file_wrangler_type',
        '_in_score_commands',
        '_new_file_contents',
        )

    def __init__(self, session=None):
        superclass = super(FileWrangler, self)
        superclass.__init__(session=session)
        self._abjad_storehouse_path = None
        self._asset_identifier = 'file'
        self._extension = ''
        self._file_name_predicate = stringtools.is_dash_case
        self._file_wrangler_type = None
        self._human_readable = False
        self._in_score_commands = []
        self._include_extensions = True
        self._new_file_contents = ''
        self._user_storehouse_path = None

    ### PRIVATE PROPERTIES ###

    @property
    def _command_to_method(self):
        superclass = super(FileWrangler, self)
        result = superclass._command_to_method
        result = result.copy()
        result.update({
            'cp': self.copy_file,
            'new': self.make_file,
            'ren': self.rename_file,
            'rm': self.remove_files,
            #
            'ck*': self.check_every_file,
            })
        return result

    ### PRIVATE METHODS ###

    def _call_lilypond_on_file_ending_with(self, string):
        file_path = self._get_file_path_ending_with(string)
        if file_path:
            self._io_manager.run_lilypond(file_path)
        else:
            message = 'file ending in {!r} not found.'
            message = message.format(string)
            self._io_manager._display(message)

    def _collect_segment_files(self, file_name):
        segments_directory = self._session.current_segments_directory
        #build_directory = self._get_current_directory()
        build_directory = self._session.current_build_directory
        directory_entries = sorted(os.listdir(segments_directory))
        source_file_paths, target_file_paths = [], []
        _, extension = os.path.splitext(file_name)
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
            score_path = self._session.current_score_directory
            score_package = self._configuration.path_to_package(
                score_path)
            score_name = score_package.replace('_', '-')
            directory_entry = directory_entry.replace('_', '-')
            target_file_name = directory_entry + extension
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
            if self._session.is_backtracking:
                return
        if not os.path.exists(build_directory):
            os.mkdir(build_directory)
        pairs = zip(source_file_paths, target_file_paths)
        return pairs

    def _confirm_segment_names(self):
        wrangler = self._session._abjad_ide._segment_package_wrangler
        view_name = wrangler._read_view_name()
        view_inventory = wrangler._read_view_inventory()
        if not view_inventory or view_name not in view_inventory:
            view_name = None
        segment_paths = wrangler._list_visible_asset_paths()
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
        if self._session.is_backtracking or not result:
            return False
        return segment_names

    def _copy_boilerplate(self, file_name, candidacy=True, replacements=None):
        replacements = replacements or {}
        manager = self._session.current_score_package_manager
        assert manager is not None
        width, height, unit = manager._parse_paper_dimensions()
        source_path = os.path.join(
            self._configuration.abjad_ide_directory,
            'boilerplate',
            file_name,
            )
        destination_path = os.path.join(
            manager._path,
            'build',
            file_name,
            )
        base_name, extension = os.path.splitext(file_name)
        candidate_name = base_name + '.candidate' + extension
        candidate_path = os.path.join(
            manager._path,
            'build',
            candidate_name,
            )
        messages = []
        with systemtools.FilesystemState(remove=[candidate_path]):
            shutil.copyfile(source_path, candidate_path)
            old = '{PAPER_SIZE}'
            new = '{{{}{}, {}{}}}'
            new = new.format(width, unit, height, unit)
            self._replace_in_file(candidate_path, old, new)
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
                if self._session.is_backtracking or not result:
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

    def _edit_file_ending_with(self, string):
        file_path = self._get_file_path_ending_with(string)
        if file_path:
            self._io_manager.edit(file_path)
        else:
            message = 'file ending in {!r} not found.'
            message = message.format(string)
            self._io_manager._display(message)

    def _enter_run(self):
        if self._file_wrangler_type == 'build':
            self._session._is_navigating_to_build_files = False   
        elif self._file_wrangler_type == 'distribution':
            self._session._is_navigating_to_distribution_files = False
        elif self._file_wrangler_type == 'etc':
            self._session._is_navigating_to_etc_files = False
        elif self._file_wrangler_type == 'maker':
            self._session._is_navigating_to_maker_files = False
        elif self._file_wrangler_type == 'stylesheet':
            self._session._is_navigating_to_stylesheets = False
        else:
            raise ValueError(repr(self._file_wrangler_type))

    @staticmethod
    def _file_name_callback(file_name):
        file_name = file_name.replace(' ', '-')
        file_name = file_name.replace('_', '-')
        return file_name

    def _interpret_file_ending_with(self, string):
        r'''Typesets TeX file.
        Calls ``pdflatex`` on file TWICE.
        Some LaTeX packages like ``tikz`` require two passes.
        '''
        file_path = self._get_file_path_ending_with(string)
        if not file_path:
            message = 'file ending in {!r} not found.'
            message = message.format(string)
            self._io_manager._display(message)
            return
        input_directory = os.path.dirname(file_path)
        output_directory = input_directory
        basename = os.path.basename(file_path)
        input_file_name_stem, extension = os.path.splitext(basename)
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
            self._handle_candidate(candidate_path, destination_path)

    def _is_valid_directory_entry(self, directory_entry):
        superclass = super(FileWrangler, self)
        if superclass._is_valid_directory_entry(directory_entry):
            name, extension = os.path.splitext(directory_entry)
            if self._file_name_predicate(name):
                if self._extension == '':
                    return True
                elif self._extension == extension:
                    return True
        return False

#    def _make_all_menu_section(self, menu):
#        commands = []
#        commands.append(('all files - check', 'ck*'))
#        commands.append(('all files - repository - add', 'rad*'))
#        commands.append(('all files - repository - clean', 'rcn*'))
#        commands.append(('all files - repository - commit', 'rci*'))
#        commands.append(('all files - repository - revert', 'rrv*'))
#        commands.append(('all files - repository - status', 'rst*'))
#        commands.append(('all files - repository - update', 'rup*'))
#        menu.make_command_section(
#            commands=commands,
#            is_hidden=True,
#            name='all',
#            )

    def _make_files_menu_section(self, menu):
        commands = []
        commands.append(('copy', 'cp'))
        commands.append(('new', 'new'))
        commands.append(('rename', 'ren'))
        commands.append(('remove', 'rm'))
        menu.make_command_section(
            commands=commands,
            name='files',
            )

    def _make_main_menu(self):
        superclass = super(FileWrangler, self)
        menu = superclass._make_main_menu()
        #self._make_all_menu_section(menu)
        self._make_files_menu_section(menu)
        if self._in_score_commands:
            menu.make_command_section(
                commands=self._in_score_commands,
                is_hidden=True,
                name='in score commands',
                )
        return menu

    def _trim_lilypond_file(self, file_path):
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

    ### PUBLIC METHODS ###

    def check_every_file(self):
        r'''Checks every file.

        Returns none.
        '''
        paths = self._list_asset_paths(valid_only=False)
        paths = [_ for _ in paths if os.path.basename(_)[0].isalpha()]
        paths = [_ for _ in paths if not _.endswith('.pyc')]
        current_directory = self._get_current_directory()
        if current_directory:
            paths = [_ for _ in paths if _.startswith(current_directory)]
        invalid_paths = []
        for path in paths:
            file_name = os.path.basename(path)
            if not self._is_valid_directory_entry(file_name):
                invalid_paths.append(path)
        messages = []
        if not invalid_paths:
            count = len(paths)
            message = '{} ({} files): OK'.format(self._breadcrumb, count)
            messages.append(message)
        else:
            message = '{}:'.format(self._breadcrumb)
            messages.append(message)
            identifier = 'file'
            count = len(invalid_paths)
            identifier = stringtools.pluralize(identifier, count)
            message = '{} unrecognized {} found:'
            message = message.format(count, identifier)
            tab = self._io_manager._tab
            message = tab + message
            messages.append(message)
            for invalid_path in invalid_paths:
                message = tab + tab + invalid_path
                messages.append(message)
        self._io_manager._display(messages)
        missing_files, missing_directories = [], []
        return messages, missing_files, missing_directories

    def collect_segment_lilypond_files(self):
        r'''Copies ``illustration.ly`` files from segment packages to build 
        directory.

        Trims top-level comments, includes and directives from each
        ``illustration.ly`` file.

        Trims header and paper block from each ``illustration.ly`` file.

        Leaves score block in each ``illustration.ly`` file.

        Returns none.
        '''
        pairs = self._collect_segment_files('illustration.ly')
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
                self._handle_candidate(candidate_file_path, target_file_path)
                self._io_manager._display('')

    def collect_segment_pdfs(self):
        r'''Copies ``illustration.pdf`` files from segment packages to build 
        directory.

        Returns none.
        '''
        pairs = self._collect_segment_files('illustration.pdf')
        if not pairs:
            return
        for source_file_path, target_file_path in pairs:
            self._handle_candidate(source_file_path, target_file_path)
            self._io_manager._display('')

    def copy_file(self):
        r'''Copies file.

        Returns none.
        '''
        self._copy_asset()

    def generate_back_cover_source(self):
        r'''Generates ``back-cover.tex``.

        Returns none.
        '''
        replacements = {}
        manager = self._session.current_score_package_manager
        catalog_number = manager._get_metadatum('catalog_number')
        if catalog_number:
            old = 'CATALOG NUMBER'
            new = str(catalog_number)
            replacements[old] = new
        composer_website = self._configuration.composer_website
        if self._session.is_test:
            composer_website = 'www.composer-website.com'
        if composer_website:
            old = 'COMPOSER WEBSITE'
            new = str(composer_website)
            replacements[old] = new
        price = manager._get_metadatum('price')
        if price:
            old = 'PRICE'
            new = str(price)
            replacements[old] = new
        self._copy_boilerplate('back-cover.tex', replacements=replacements)

    def generate_front_cover_source(self):
        r'''Generates ``front-cover.tex``.

        Returns none.
        '''
        file_name = 'front-cover.tex'
        replacements = {}
        manager = self._session.current_score_package_manager
        score_title = manager._get_title()
        if score_title:
            old = 'TITLE'
            new = str(score_title.upper())
            replacements[old] = new
        forces_tagline = manager._get_metadatum('forces_tagline')
        if forces_tagline:
            old = 'FOR INSTRUMENTS'
            new = str(forces_tagline)
            replacements[old] = new
        year = manager._get_metadatum('year')
        if year:
            old = 'YEAR'
            new = str(year)
            replacements[old] = new
        composer = self._configuration.upper_case_composer_full_name
        if self._session.is_test:
            composer = 'EXAMPLE COMPOSER NAME'
        if composer:
            old = 'COMPOSER'
            new = str(composer)
            replacements[old] = new
        self._copy_boilerplate(file_name, replacements=replacements)

    def generate_interpret_open_front_cover(self):
        r'''Generates ``front-cover.tex``.

        Then interprets ``front-cover.tex``.

        Then opens ``front-cover.pdf``.

        Returns none.
        '''
        self.generate_front_cover_source()
        self.interpret_front_cover()
        self.open_front_cover_pdf()
        
    def generate_music_source(self):
        r'''Generates ``music.ly``.

        Returns none.
        '''
        result = self._confirm_segment_names()
        if self._session.is_backtracking or not isinstance(result, list):
            return
        segment_names = result
        lilypond_names = [_.replace('_', '-') for _ in segment_names]
        source_path = os.path.join(
            self._configuration.abjad_ide_directory,
            'boilerplate',
            'music.ly',
            )
        manager = self._session.current_score_package_manager
        destination_path = os.path.join(
            manager._path,
            'build',
            'music.ly',
            )
        candidate_path = os.path.join(
            manager._path,
            'build',
            'music.candidate.ly',
            )
        with systemtools.FilesystemState(remove=[candidate_path]):
            shutil.copyfile(source_path, candidate_path)
            width, height, unit = manager._parse_paper_dimensions()
            old = '{PAPER_SIZE}'
            new = '{{{}{}, {}{}}}'
            new = new.format(width, unit, height, unit)
            self._replace_in_file(candidate_path, old, new)
            lines = []
            for lilypond_name in lilypond_names:
                file_name = lilypond_name + '.ly'
                tab = 4 * ' '
                line = tab + r'\include "{}"'
                line = line.format(file_name)
                lines.append(line)
            if lines:
                new = '\n'.join(lines)
                old = '%%% SEGMENTS %%%'
                self._replace_in_file(candidate_path, old, new)
            else:
                line_to_remove = '%%% SEGMENTS %%%\n'
                self._remove_file_line(candidate_path, line_to_remove)
            stylesheet_path = self._session.current_stylesheet_path
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
            score_title = manager._get_title()
            if score_title:
                old = 'SCORE_NAME'
                new = score_title
                self._replace_in_file(candidate_path, old, new)
            annotated_title = manager._get_title(year=True)
            if annotated_title:
                old = 'SCORE_TITLE'
                new = annotated_title
                self._replace_in_file(candidate_path, old, new)
            forces_tagline = manager._get_metadatum('forces_tagline')
            if forces_tagline:
                old = 'FORCES_TAGLINE'
                new = forces_tagline
                self._replace_in_file(candidate_path, old, new)
            self._handle_candidate(candidate_path, destination_path)

    def generate_preface_source(self):
        r'''Generates ``preface.tex``.

        Returns none.
        '''
        self._copy_boilerplate('preface.tex')

    def generate_score_source(self):
        r'''Generates ``score.tex``.

        Returns none.
        '''
        self._copy_boilerplate('score.tex')

    def interpret_back_cover(self):
        r'''Interprets ``back-cover.tex``.

        Returns none.
        '''
        self._interpret_file_ending_with('back-cover.tex')

    def interpret_front_cover(self):
        r'''Interprets ``front-cover.tex``.

        Returns none.
        '''
        self._interpret_file_ending_with('front-cover.tex')

    def interpret_music(self):
        r'''Interprets ``music.ly``.

        Returns none.
        '''
        self._call_lilypond_on_file_ending_with('music.ly')

    def interpret_open_front_cover(self):
        r'''Interprets ``front-cover.tex`` and then opens ``front-cover.pdf``.

        Returns none.
        '''
        self.interpret_front_cover()
        self.open_front_cover_pdf()
        
    def interpret_preface(self):
        r'''Interprets ``preface.tex``.

        Returns none.
        '''
        self._interpret_file_ending_with('preface.tex')

    def interpret_score(self):
        r'''Interprets ``score.tex``.

        Returns none.
        '''
        self._interpret_file_ending_with('score.tex')

    def make_file(self):
        r'''Makes empty file.

        Returns none.
        '''
        self._make_file(
            contents=self._new_file_contents,
            message='file name',
            )

    def push_score_pdf_to_distribution_directory(self):
        r'''Pushes ``score.pdf`` to distribution directory.

        Returns none.
        '''
        path = self._session.current_build_directory
        build_score_path = os.path.join(path, 'score.pdf')
        if not os.path.exists(build_score_path):
            message = 'does not exist: {!r}.'
            message = message.format(build_score_path)
            self._io_manager._display(message)
            return
        score_package_name = self._session.current_score_package_name
        score_package_name = score_package_name.replace('_', '-')
        distribution_file_name = '{}-score.pdf'.format(score_package_name)
        distribution_directory = self._session.current_distribution_directory
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
        
    def remove_files(self):
        r'''Removes one or more files.

        Returns none.
        '''
        self._remove_assets()

    def rename_file(self):
        r'''Renames file.

        Returns none.
        '''
        self._rename_asset()