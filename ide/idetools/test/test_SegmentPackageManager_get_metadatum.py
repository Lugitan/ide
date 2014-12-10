# -*- encoding: utf-8 -*-
import os
from abjad import *
import ide
abjad_ide = ide.idetools.AbjadIDE(is_test=True)
metadata_py_path = os.path.join(
    abjad_ide._configuration.example_score_packages_directory,
    'red_example_score',
    'segments',
    'segment_01',
    '__metadata__.py',
    )


def test_SegmentPackageManager_get_metadatum_01():

    with systemtools.FilesystemState(keep=[metadata_py_path]):
        # make sure no flavor metadatum found
        input_ = 'red~example~score g A mdg flavor q'
        abjad_ide._run(input_=input_)
        assert 'None' in abjad_ide._transcript.contents

        # add flavor metadatum
        input_ = 'red~example~score g A mda flavor cherry q'
        abjad_ide._run(input_=input_)

        # maker sure flavor metadatum now equal to 'cherry'
        input_ = 'red~example~score g A mdg flavor q'
        abjad_ide._run(input_=input_)
        assert "'cherry'" in abjad_ide._transcript.contents