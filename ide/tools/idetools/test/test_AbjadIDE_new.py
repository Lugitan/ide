# -*- encoding: utf-8 -*-
import os
import pytest
from abjad import *
import ide
abjad_ide = ide.tools.idetools.AbjadIDE(is_test=True)
configuration = ide.tools.idetools.AbjadIDEConfiguration()


def test_AbjadIDE_new_01():
    r'''Makes score package.
    '''

    outer_path = os.path.join(
        configuration.composer_scores_directory,
        'example_score',
        )
    inner_path = os.path.join(outer_path, 'example_score')
    outer_directory_entries = [
        'README.md',
        'requirements.txt',
        'setup.cfg',
        'setup.py',
        ]
    inner_directory_entries = [
        '__init__.py',
        '__metadata__.py',
        'build',
        'distribution',
        'etc',
        'makers',
        'materials',
        'segments',
        'stylesheets',
        'test',
        ]

    with systemtools.FilesystemState(remove=[outer_path]):
        input_ = 'new Example~Score y q'
        abjad_ide._run_main_menu(input_=input_)
        contents = abjad_ide._io_manager._transcript.contents
        assert os.path.exists(outer_path)
        session = ide.tools.idetools.Session(is_test=True)
        io_manager = ide.tools.idetools.IOManager(session=session)
        assert abjad_ide._list_directory(inner_path) == inner_directory_entries
        for file_name in outer_directory_entries:
            path = os.path.join(outer_path, file_name)
            assert os.path.exists(path)

    assert 'Enter title]> Example Score' in contents


def test_AbjadIDE_new_02():
    r'''Accepts flexible package name input for score packages.
    '''

    score_package = os.path.join(
        configuration.composer_scores_directory,
        'example_score_1',
        )

    with systemtools.FilesystemState(remove=[score_package]):
        input_ = 'new ExampleScore1 y q'
        abjad_ide._run_main_menu(input_=input_)
        assert os.path.exists(score_package)

    with systemtools.FilesystemState(remove=[score_package]):
        input_ = 'new exampleScore1 y q'
        abjad_ide._run_main_menu(input_=input_)
        assert os.path.exists(score_package)

    with systemtools.FilesystemState(remove=[score_package]):
        input_ = 'new EXAMPLE_SCORE_1 y q'
        abjad_ide._run_main_menu(input_=input_)
        assert os.path.exists(score_package)

    with systemtools.FilesystemState(remove=[score_package]):
        input_ = 'new example_score_1 y q'
        abjad_ide._run_main_menu(input_=input_)
        assert os.path.exists(score_package)


def test_AbjadIDE_new_03():
    r'''Creates material package outside score.
    '''

    session = ide.tools.idetools.Session(is_test=True)
    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'materials',
        'testnotes',
        )
    directory_entries = [
        '__init__.py',
        '__metadata__.py',
        'definition.py',
        ]

    with systemtools.FilesystemState(remove=[path]):
        input_ = 'mm new Red~Example~Score testnotes y q'
        abjad_ide._run_main_menu(input_=input_)
        assert os.path.exists(path)
        session = ide.tools.idetools.Session(is_test=True)
        io_manager = ide.tools.idetools.IOManager(session=session)
        assert abjad_ide._list_directory(path) == directory_entries


def test_AbjadIDE_new_04():
    r'''Makes segment package.
    '''

    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'segments',
        'segment_04',
        )
    directory_entries = [
        '__init__.py',
        '__metadata__.py',
        'definition.py',
        ]

    with systemtools.FilesystemState(remove=[path]):
        input_ = 'red~example~score g new segment~04 y q'
        abjad_ide._run_main_menu(input_=input_)
        contents = abjad_ide._io_manager._transcript.contents
        assert os.path.exists(path)
        session = ide.tools.idetools.Session(is_test=True)
        io_manager = ide.tools.idetools.IOManager(session=session)
        assert abjad_ide._list_directory(path) == directory_entries


def test_AbjadIDE_new_05():
    r'''Makes new build file in score.
    '''

    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'build',
        'test-file.txt',
        )

    with systemtools.FilesystemState(remove=[path]):
        input_ = 'red~example~score u new test-file.txt q'
        abjad_ide._run_main_menu(input_=input_)
        assert os.path.exists(path)