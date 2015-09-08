# -*- encoding: utf-8 -*-
import os
from abjad import *
import ide
abjad_ide = ide.tools.idetools.AbjadIDE(is_test=True)
configuration = ide.tools.idetools.AbjadIDEConfiguration()


def test_AbjadIDE_rename_01():
    r'''Renames score package.
    '''

    path_100_outer = os.path.join(
        configuration.composer_scores_directory,
        'example_score_100',
        )
    path_100_inner = os.path.join(
        configuration.composer_scores_directory,
        'example_score_100',
        'example_score_100',
        )
    path_101_outer = os.path.join(
        configuration.composer_scores_directory,
        'example_score_101',
        )
    path_101_inner = os.path.join(
        configuration.composer_scores_directory,
        'example_score_101',
        'example_score_101',
        )

    with systemtools.FilesystemState(remove=[path_100_outer, path_101_outer]):
        input_ = 'new example~score~100 y q'
        abjad_ide._run_main_menu(input_=input_)
        assert os.path.exists(path_100_outer)
        assert os.path.exists(path_100_inner)
        title = 'Example Score 100'
        abjad_ide._add_metadatum(
            path_100_inner,
            'title',
            title,
            )
        input_ = 'ren Example~Score~100 example_score_101 y q'
        abjad_ide._run_main_menu(input_=input_)
        assert not os.path.exists(path_100_outer)
        assert os.path.exists(path_101_outer)
        assert os.path.exists(path_101_inner)


def test_AbjadIDE_rename_02():
    r'''Renames material package in score.
    '''

    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'materials',
        'test_material',
        )
    new_path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'materials',
        'new_test_material',
        )

    with systemtools.FilesystemState(remove=[path, new_path]):
        input_ = 'red~example~score m new test~material y q'
        abjad_ide._run_main_menu(input_=input_)
        assert os.path.exists(path)
        input_ = 'red~example~score m ren test~material new~test~material y q'
        abjad_ide._run_main_menu(input_=input_)
        assert not os.path.exists(path)
        assert os.path.exists(new_path)


# TODO: make this work
#def test_AbjadIDE_rename_03():
#    r'''Renames material package outside of score.
#    '''
#
#    path = os.path.join(
#        configuration.abjad_ide_example_scores_directory,
#        'red_example_score',
#        'red_example_score',
#        'materials',
#        'test_material',
#        )
#    new_path = os.path.join(
#        configuration.abjad_ide_example_scores_directory,
#        'red_example_score',
#        'red_example_score',
#        'materials',
#        'new_test_material',
#        )
#
#    input_ = 'new Red~Example~Score m new test~material y q'
#
#    with systemtools.FilesystemState(remove=[path, new_path]):
#        abjad_ide._run_main_menu(input_=input_)
#        assert os.path.exists(path)
#        input_ = 'red~example~score m ren test~material new~test~material y q'
#        abjad_ide._run_main_menu(input_=input_)
#        assert not os.path.exists(path)
#        assert os.path.exists(new_path)


def test_AbjadIDE_rename_04():
    r'''Renames segment package.
    '''

    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'segments',
        'segment_04',
        )
    new_path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'segments',
        'renamed_segment_04',
        )

    with systemtools.FilesystemState(remove=[path, new_path]):
        input_ = 'red~example~score g new segment~04 y q'
        abjad_ide._run_main_menu(input_=input_)
        assert os.path.exists(path)
        input_ = 'red~example~score g ren segment~04 renamed_segment_04 y q'
        abjad_ide._run_main_menu(input_=input_)
        assert not os.path.exists(path)
        assert os.path.exists(new_path)


def test_AbjadIDE_rename_05():
    r'''Works at home screen.
    '''

    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'build',
        'score.pdf',
        )
    new_path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'build',
        'foo-score.pdf',
        )

    assert os.path.exists(path)

    input_ = 'uu ren score.pdf~(Red~Example~Score)'
    input_ += ' foo-score.pdf y q'
    abjad_ide._run_main_menu(input_=input_)
    assert not os.path.exists(path)
    assert os.path.exists(new_path)

    # no shutil because need to rename file in repository
    input_ = 'uu ren foo-score.pdf~(Red~Example~Score)'
    input_ += ' score.pdf y q'
    abjad_ide._run_main_menu(input_=input_)
    assert not os.path.exists(new_path)
    assert os.path.exists(path)


def test_AbjadIDE_rename_06():
    r'''Works in score package.
    '''

    path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'build',
        'score.pdf',
        )
    new_path = os.path.join(
        configuration.abjad_ide_example_scores_directory,
        'red_example_score',
        'red_example_score',
        'build',
        'foo-score.pdf',
        )

    assert os.path.exists(path)

    input_ = 'red~example~score u ren score.pdf'
    input_ += ' foo-score.pdf y q'
    abjad_ide._run_main_menu(input_=input_)
    assert not os.path.exists(path)
    assert os.path.exists(new_path)

    # no shutil because need to rename file in repository
    input_ = 'red~example~score u ren foo-score.pdf'
    input_ += ' score.pdf y q'
    abjad_ide._run_main_menu(input_=input_)
    assert not os.path.exists(new_path)
    assert os.path.exists(path)