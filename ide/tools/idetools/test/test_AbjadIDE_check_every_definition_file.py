# -*- coding: utf-8 -*-
import os
from abjad import *
import ide
abjad_ide = ide.tools.idetools.AbjadIDE(is_test=True)
configuration = ide.tools.idetools.AbjadIDEConfiguration()


def test_AbjadIDE_check_every_definition_file_01():

    input_ = 'red~example~score mm dfk* y q'
    abjad_ide._run_main_menu(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents

    package_names = [
        'magic_numbers',
        'performer_inventory',
        'pitch_range_inventory',
        'tempo_inventory',
        'time_signatures',
        ]
    paths = []
    for package_name in package_names:
        path = os.path.join(
            configuration.abjad_ide_example_scores_directory,
            'red_example_score',
            'red_example_score',
            'materials',
            package_name,
            'definition.py',
            )
        paths.append(path)

    confirmation_messages = [_ + ' OK.' for _ in paths]

    assert 'Will check ...' in contents
    for path in paths:
        assert path in contents
    for confirmation_message in confirmation_messages:
        assert confirmation_message in contents


def test_AbjadIDE_check_every_definition_file_02():

    input_ = 'red~example~score gg dfk* y q'
    abjad_ide._run_main_menu(input_=input_)
    contents = abjad_ide._io_manager._transcript.contents

    package_names = [
        'segment_01',
        'segment_02',
        'segment_03',
        ]
    paths = []
    for package_name in package_names:
        path = os.path.join(
            configuration.abjad_ide_example_scores_directory,
            'red_example_score',
            'red_example_score',
            'segments',
            package_name,
            'definition.py',
            )
        paths.append(path)

    confirmation_messages = [_ + ' OK.' for _ in paths]

    assert 'Will check ...' in contents
    for path in paths:
        assert path in contents
    for confirmation_message in confirmation_messages:
        assert confirmation_message in contents