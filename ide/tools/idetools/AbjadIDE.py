# -*- encoding: utf-8 -*-
import os
import shutil
import sys
from abjad.tools import stringtools
from abjad.tools import systemtools
from ide.tools.idetools.Controller import Controller


class AbjadIDE(Controller):
    r'''Abjad IDE.

    ..  container:: example

        ::

            >>> ide.tools.idetools.AbjadIDE(is_test=True)
            AbjadIDE()

    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        )

    ### INITIALIZER ###

    def __init__(self, session=None, is_test=False):
        from ide.tools import idetools
        if session is None:
            session = idetools.Session()
            session._is_test = is_test
        superclass = super(AbjadIDE, self)
        superclass.__init__(session=session)
        self._session._abjad_ide = self
        self._score_package_wrangler._supply_missing_views_files()

    ### PRIVATE PROPERTIES ###

    @property
    def _breadcrumb(self):
        if not self._session.is_in_score:
            return 'Abjad IDE'

    @property
    @systemtools.Memoize
    def _build_file_wrangler(self):
        from ide.tools import idetools
        wrangler = idetools.Wrangler(session=self._session)
        wrangler._asset_identifier = 'file'
        wrangler._basic_breadcrumb = 'build'
        wrangler._file_name_predicate = stringtools.is_dash_case
        wrangler._score_storehouse_path_infix_parts = ('build',)
        wrangler._use_dash_case = True
        wrangler._directory_entry_predicate = \
            wrangler._is_valid_file_directory_entry
        commands = []
        commands.append(('collect music segment files', 'mc'))
        commands.append(('generate back-cover.tex', 'bcg'))
        commands.append(('generate front-cover.tex', 'fcg'))
        commands.append(('generate music.ly', 'mg'))
        commands.append(('generate preface.tex', 'pg'))
        commands.append(('generate score.tex', 'sg'))
        commands.append(('interpret back-cover.tex', 'bci'))
        commands.append(('interpret front-cover.tex', 'fci'))
        commands.append(('interpret music.ly', 'mi'))
        commands.append(('interpret preface.tex', 'pi'))
        commands.append(('interpret score.tex', 'si'))
        commands.append(('push score to distribution directory', 'sp'))
        wrangler._controller_commands = commands
        return wrangler

    @property
    @systemtools.Memoize
    def _distribution_file_wrangler(self):
        from ide.tools import idetools
        wrangler = idetools.Wrangler(session=self._session)
        wrangler._asset_identifier = 'file'
        wrangler._basic_breadcrumb = 'distribution'
        wrangler._file_name_predicate = stringtools.is_dash_case
        wrangler._use_dash_case = True
        wrangler._directory_entry_predicate = \
            wrangler._is_valid_file_directory_entry
        wrangler._score_storehouse_path_infix_parts = ('distribution',)
        return wrangler

    @property
    @systemtools.Memoize
    def _etc_file_wrangler(self):
        from ide.tools import idetools
        wrangler = idetools.Wrangler(session=self._session)
        wrangler._asset_identifier = 'file'
        wrangler._basic_breadcrumb = 'etc'
        wrangler._file_name_predicate = stringtools.is_dash_case
        wrangler._use_dash_case = True
        wrangler._directory_entry_predicate = \
            wrangler._is_valid_file_directory_entry
        wrangler._score_storehouse_path_infix_parts = ('etc',)
        return wrangler

    @property
    @systemtools.Memoize
    def _maker_file_wrangler(self):
        from ide.tools import idetools
        wrangler = idetools.Wrangler(session=self._session)
        wrangler._asset_identifier = 'maker'
        wrangler._basic_breadcrumb = 'makers'
        wrangler._file_extension = '.py'
        wrangler._file_name_predicate = stringtools.is_upper_camel_case
        wrangler._force_lowercase_file_name = False
        wrangler._new_file_contents = self._configuration.unicode_directive
        wrangler._score_storehouse_path_infix_parts = ('makers',)
        wrangler._directory_entry_predicate = \
            wrangler._is_valid_file_directory_entry
        return wrangler

    @property
    @systemtools.Memoize
    def _material_package_wrangler(self):
        from ide.tools import idetools
        wrangler = idetools.Wrangler(session=self._session)
        wrangler._asset_identifier = 'material package'
        wrangler._basic_breadcrumb = 'materials'
        wrangler._directory_entry_predicate = \
            wrangler._is_valid_package_directory_entry
        wrangler._score_storehouse_path_infix_parts = ('materials',)
        commands = []
        commands.append(('check every definition.py files', 'dc*'))
        commands.append(('edit every definition.py files', 'de*'))
        commands.append(('interpret all illustration.ly files', 'ii*'))
        commands.append(('open all illustration.pdf files', 'io*'))
        commands.append(('next package', '>'))
        commands.append(('previous package', '<'))
        wrangler._controller_commands = commands
        return wrangler

    @property
    @systemtools.Memoize
    def _score_package_wrangler(self):
        from ide.tools import idetools
        wrangler = idetools.Wrangler(session=self._session)
        wrangler._asset_identifier = 'score package'
        wrangler._annotate_year = True
        wrangler._basic_breadcrumb = 'scores'
        wrangler._group_asset_section_by_annotation = False
        wrangler._hide_breadcrumb_in_score = True
        wrangler._include_asset_name = False
        wrangler._mandatory_copy_target_storehouse = \
            wrangler._configuration.user_score_packages_directory
        wrangler._only_example_scores_during_test = True
        wrangler._sort_by_annotation = False
        wrangler._directory_entry_predicate = \
            wrangler._is_valid_package_directory_entry
        commands = []
        commands.append(('check every score packages', 'ck*'))
        commands.append(('git add all score packages', 'add*'))
        commands.append(('git clean all score packages', 'clean*'))
        commands.append(('git commit all score packages', 'ci*'))
        commands.append(('git revert all score packages', 'revert*'))
        commands.append(('git status all score packages', 'st*'))
        commands.append(('git update all score packages', 'up*'))
        commands.append(('open all distribution score.pdf files', 'so*'))
        commands.append(('go to all build files', 'uu'))
        commands.append(('go to all distribution', 'dd'))
        commands.append(('go to all etc files', 'ee'))
        commands.append(('go to all maker files', 'kk'))
        commands.append(('go to all material packages', 'mm'))
        commands.append(('go to all segment packages', 'gg'))
        commands.append(('go to all stylesheets', 'yy'))
        wrangler._controller_commands = commands
        return wrangler

    @property
    @systemtools.Memoize
    def _segment_package_wrangler(self):
        from ide.tools import idetools
        wrangler = idetools.Wrangler(session=self._session)
        wrangler._asset_identifier = 'segment package'
        wrangler._basic_breadcrumb = 'segments'
        wrangler._score_storehouse_path_infix_parts = ('segments',)
        wrangler._directory_entry_predicate = \
            wrangler._is_valid_package_directory_entry
        commands = []
        commands.append(('check every definition.py files', 'dc*'))
        commands.append(('edit every definition.py files', 'de*'))
        commands.append(('illustrate all definition.py files', 'di*'))
        commands.append(('interpret all illustration.ly files', 'ii*'))
        commands.append(('open all illustration.pdf files', 'io*'))
        commands.append(('next package', '>'))
        commands.append(('previous package', '<'))
        wrangler._controller_commands = commands
        return wrangler

    @property
    @systemtools.Memoize
    def _stylesheet_wrangler(self):
        from ide.tools import idetools
        wrangler = idetools.Wrangler(session=self._session)
        wrangler._asset_identifier = 'stylesheet'
        wrangler._basic_breadcrumb = 'stylesheets'
        wrangler._file_extension = '.ily'
        wrangler._file_name_predicate = stringtools.is_dash_case
        wrangler._score_storehouse_path_infix_parts = ('stylesheets',)
        wrangler._use_dash_case = True
        wrangler._directory_entry_predicate = \
            wrangler._is_valid_file_directory_entry
        return wrangler

    @property
    def _wranglers(self):
        return (
            self._build_file_wrangler,
            self._distribution_file_wrangler,
            self._etc_file_wrangler,
            self._maker_file_wrangler,
            self._material_package_wrangler,
            self._score_package_wrangler,
            self._segment_package_wrangler,
            self._stylesheet_wrangler,
            )

    ### PRIVATE METHODS ###

    def _run(self, input_=None):
        from ide.tools import idetools
        self._session._reinitialize()
        type(self).__init__(self, session=self._session)
        if input_:
            self._session._pending_input = input_
        controller = self._io_manager._controller(
            controller=self,
            consume_local_backtrack=True,
            on_exit_callbacks=(self._session._clean_up,)
            )
        path = self._configuration.abjad_ide_directory
        directory_change = systemtools.TemporaryDirectoryChange(path)
        state = systemtools.NullContextManager()
        wrangler_views = os.path.join(
            self._configuration.configuration_directory,
            'views',
            '__metadata__.py',
            )
        if self._session.is_test:
            paths_to_keep = []
            paths_to_keep.append(wrangler_views)
            state = systemtools.FilesystemState(keep=paths_to_keep)
        interaction = self._io_manager._make_interaction(task=False)
        with controller, directory_change, state, interaction:
            self._session._pending_redraw = True
            if self._session.is_test:
                empty_views = os.path.join(
                    self._configuration.boilerplate_directory,
                    '__views_metadata__.py',
                    )
                shutil.copyfile(empty_views, wrangler_views)
            while True:
                result = self._score_package_wrangler._get_sibling_score_path()
                if not result:
                    result = self._session.wrangler_navigation_directive
                if result:
                    self._score_package_wrangler._handle_input(result)
                else:
                    self._score_package_wrangler._run()
                self._session._is_backtracking_to_score = False
                self._session._is_navigating_to_scores = False
                if self._session.is_quitting:
                    if not self._transcript[-1][-1] == '':
                        self._io_manager._display('')
                    if self._session._clear_terminal_after_quit:
                        self._io_manager.clear_terminal()
                    return

    ### PUBLIC METHODS ###

    @staticmethod
    def start_abjad_ide():
        r'''Starts Abjad IDE.

        Returns none.
        '''
        import ide
        abjad_ide = ide.tools.idetools.AbjadIDE(is_test=False)
        input_ = ' '.join(sys.argv[1:])
        abjad_ide._run(input_=input_)