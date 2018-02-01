import abjad
import baca
import ide
abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_color_staff_lines_01():
    r'''In build directory.
    '''

    with ide.Test():

        build = ide.Path('green_score', 'builds', 'arch-a-score')
        path = build('_segments', 'segment-_.ly')

        abjad_ide('gre bb arch-a-score ggc q')
        assert path.is_file()
        
        abjad_ide('gre bb arch-a-score slcl q')
        lines = abjad_ide.io.transcript.lines
        for line in [
            'Coloring staff lines ...',
            ' Activating staff lines color tags in arch-a-score ...',
            '  Found 4 staff lines color tags in arch-a-score ...',
            '  Activating 4 staff lines color tags in arch-a-score ...',
            ]:
            assert line in lines

        abjad_ide('gre bb arch-a-score sluc q')
        lines = abjad_ide.io.transcript.lines
        for line in [
            'Uncoloring staff lines ...',
            ' Deactivating staff lines color tags in arch-a-score ...',
            '  Found 4 staff lines color tags in arch-a-score ...',
            '  Deactivating 4 staff lines color tags in arch-a-score ...',
            ]:
            assert line in lines

        abjad_ide('gre bb arch-a-score slcl q')
        lines = abjad_ide.io.transcript.lines
        for line in [
            'Coloring staff lines ...',
            ' Activating staff lines color tags in arch-a-score ...',
            '  Found 4 staff lines color tags in arch-a-score ...',
            '  Activating 4 staff lines color tags in arch-a-score ...',
            ]:
            assert line in lines


def test_AbjadIDE_color_staff_lines_02():
    r'''In segment directory.
    '''

    with ide.Test():

        path = ide.Path('green_score', 'segments', '_', 'illustration.ly')
        assert path.is_file()
        
        abjad_ide('gre %_ slcl q')
        lines = abjad_ide.io.transcript.lines
        for line in [
            'Coloring staff lines ...',
            ' Activating staff lines color tags in _ ...',
            '  Found 4 staff lines color tags in _ ...',
            '  Skipping 4 (active) staff lines color tags in _ ...',
            ]:
            assert line in lines
        
        abjad_ide('gre %_ sluc q')
        lines = abjad_ide.io.transcript.lines
        for line in [
            'Uncoloring staff lines ...',
            ' Deactivating staff lines color tags in _ ...',
            '  Found 4 staff lines color tags in _ ...',
            '  Deactivating 4 staff lines color tags in _ ...',
            ]:
            assert line in lines

        abjad_ide('gre %_ slcl q')
        lines = abjad_ide.io.transcript.lines
        for line in [
            'Coloring staff lines ...',
            ' Activating staff lines color tags in _ ...',
            '  Found 4 staff lines color tags in _ ...',
            '  Activating 4 staff lines color tags in _ ...',
            ]:
            assert line in lines