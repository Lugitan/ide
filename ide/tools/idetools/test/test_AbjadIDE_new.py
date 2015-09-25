# -*- coding: utf-8 -*-
import os
from abjad import *
import ide
abjad_ide = ide.tools.idetools.AbjadIDE(is_test=True)
configuration = ide.tools.idetools.AbjadIDEConfiguration()


def test_AbjadIDE_new_01():
    r'''Makes new score directory.
    '''

    outer_path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
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

    input_ = 'new Example~Score q'

    with systemtools.FilesystemState(remove=[outer_path]):
        abjad_ide._start(input_=input_)
        contents = abjad_ide._io_manager._transcript.contents
        assert os.path.exists(outer_path)
        session = ide.tools.idetools.Session(is_test=True)
        io_manager = ide.tools.idetools.IOManager(session=session)
        entries = os.listdir(inner_path)
        for entry in inner_directory_entries:
            assert entry in entries, repr(entry)
        for file_name in outer_directory_entries:
            path = os.path.join(outer_path, file_name)
            assert os.path.exists(path)

    assert 'Enter title]> Example Score' in contents


def test_AbjadIDE_new_02():
    r'''Coerces score directory name.
    '''

    score_package = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'example_score_1',
        )

    with systemtools.FilesystemState(remove=[score_package]):
        input_ = 'new ExampleScore1 q'
        abjad_ide._start(input_=input_)
        assert os.path.exists(score_package)

    with systemtools.FilesystemState(remove=[score_package]):
        input_ = 'new exampleScore1 q'
        abjad_ide._start(input_=input_)
        assert os.path.exists(score_package)

    with systemtools.FilesystemState(remove=[score_package]):
        input_ = 'new EXAMPLE_SCORE_1 q'
        abjad_ide._start(input_=input_)
        assert os.path.exists(score_package)

    with systemtools.FilesystemState(remove=[score_package]):
        input_ = 'new example_score_1 q'
        abjad_ide._start(input_=input_)
        assert os.path.exists(score_package)


def test_AbjadIDE_new_03():
    r'''Makes new build file.
    '''

    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'build',
        'test-file.txt',
        )

    input_ = 'red~example~score bb new test-file.txt q'

    with systemtools.FilesystemState(remove=[path]):
        abjad_ide._start(input_=input_)
        assert os.path.exists(path)


def test_AbjadIDE_new_04():
    r'''Coerces build file name.
    '''

    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'build',
        'test-file.txt',
        )

    input_ = 'red~example~score bb new test_file.txt q'

    with systemtools.FilesystemState(remove=[path]):
        abjad_ide._start(input_=input_)
        assert os.path.exists(path)


def test_AbjadIDE_new_05():
    r'''Makes new maker file.
    '''

    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'makers',
        'NewMaker.py',
        )

    input_ = 'red~example~score kk new NewMaker.py q'

    with systemtools.FilesystemState(remove=[path]):
        abjad_ide._start(input_=input_)
        assert os.path.exists(path)
        with open(path, 'r') as file_pointer:
            string = file_pointer.read()
            assert 'class NewMaker(object)' in string


def test_AbjadIDE_new_06():
    r'''Coerces maker file name.
    '''

    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'makers',
        'NewMaker.py',
        )

    input_ = 'red~example~score kk new new~maker q'

    with systemtools.FilesystemState(remove=[path]):
        abjad_ide._start(input_=input_)
        assert os.path.exists(path)
        with open(path, 'r') as file_pointer:
            string = file_pointer.read()
            assert 'class NewMaker(object)' in string


def test_AbjadIDE_new_07():
    r'''Makes new material directory.
    '''

    session = ide.tools.idetools.Session(is_test=True)
    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'materials',
        'test_notes',
        )
    directory_entries = [
        '__init__.py',
        '__metadata__.py',
        'definition.py',
        ]

    input_ = 'Red~Example~Score mm new test_notes q'

    with systemtools.FilesystemState(remove=[path]):
        abjad_ide._start(input_=input_)
        assert os.path.exists(path)
        session = ide.tools.idetools.Session(is_test=True)
        io_manager = ide.tools.idetools.IOManager(session=session)
        entries = os.listdir(path)
        for entry in directory_entries:
            assert entry in entries, repr(entry)


def test_AbjadIDE_new_08():
    r'''Coerces material directory name.
    '''

    session = ide.tools.idetools.Session(is_test=True)
    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'materials',
        'test_notes',
        )
    directory_entries = [
        '__init__.py',
        '__metadata__.py',
        'definition.py',
        ]

    input_ = 'Red~Example~Score mm new test~notes q'

    with systemtools.FilesystemState(remove=[path]):
        abjad_ide._start(input_=input_)
        assert os.path.exists(path)
        session = ide.tools.idetools.Session(is_test=True)
        io_manager = ide.tools.idetools.IOManager(session=session)
        entries = os.listdir(path)
        for entry in directory_entries:
            assert entry in entries, repr(entry)


def test_AbjadIDE_new_09():
    r'''Makes new segment directory.
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

    input_ = 'red~example~score gg new segment_04 q'

    with systemtools.FilesystemState(remove=[path]):
        abjad_ide._start(input_=input_)
        contents = abjad_ide._io_manager._transcript.contents
        assert os.path.exists(path)
        session = ide.tools.idetools.Session(is_test=True)
        io_manager = ide.tools.idetools.IOManager(session=session)
        entries = os.listdir(path)
        for entry in directory_entries:
            assert entry in entries, repr(entry)


def test_AbjadIDE_new_10():
    r'''Coerces segment directory name.
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

    input_ = 'red~example~score gg new segment~04 q'

    with systemtools.FilesystemState(remove=[path]):
        abjad_ide._start(input_=input_)
        contents = abjad_ide._io_manager._transcript.contents
        assert os.path.exists(path)
        session = ide.tools.idetools.Session(is_test=True)
        io_manager = ide.tools.idetools.IOManager(session=session)
        entries = os.listdir(path)
        for entry in directory_entries:
            assert entry in entries, repr(entry)


def test_AbjadIDE_new_11():
    r'''Makes new stylesheet.
    '''

    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'stylesheets',
        'new-stylesheet.ily',
        )

    input_ = 'red~example~score yy new new-stylesheet.ily q'

    with systemtools.FilesystemState(remove=[path]):
        abjad_ide._start(input_=input_)
        assert os.path.exists(path)


def test_AbjadIDE_new_12():
    r'''Coerces stylesheet new.
    '''

    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'stylesheets',
        'new-stylesheet.ily',
        )

    input_ = 'red~example~score yy new new~stylesheet q'

    with systemtools.FilesystemState(remove=[path]):
        abjad_ide._start(input_=input_)
        assert os.path.exists(path)