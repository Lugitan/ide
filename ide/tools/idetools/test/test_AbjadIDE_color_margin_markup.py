import abjad
import baca
import ide
abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_color_margin_markup_01():
    r'''In build directory.
    '''

    with ide.Test():

        match = abjad.tags.margin_markup_color_expression_match
        build = ide.Path('green_score', 'builds', 'arch-a-score')
        path = build('_segments', 'segment-_.ly')

        abjad_ide('gre bb arch-a-score ggc q')
        assert path.is_file()
        assert path.count(match) == ((0, 0), (0, 0))
        
        abjad_ide('gre bb arch-a-score mmcl q')
        lines = abjad_ide.io.transcript.lines
        assert path.count(match) == ((0, 0), (0, 0))
        for line in [
            'Coloring margin markup ...',
            ' Activating margin markup color tags in arch-a-score ...',
            '  Found no margin markup color tags in arch-a-score ...',
            ]:
            assert line in lines

        abjad_ide('gre bb arch-a-score mmuc q')
        lines = abjad_ide.io.transcript.lines
        assert path.count(match) == ((0, 0), (0, 0))
        for line in [
            'Uncoloring margin markup ...',
            ' Deactivating margin markup color tags in arch-a-score ...',
            '  Found no margin markup color tags in arch-a-score ...',
            ]:
            assert line in lines

        abjad_ide('gre bb arch-a-score mmcl q')
        lines = abjad_ide.io.transcript.lines
        assert path.count(match) == ((0, 0), (0, 0))
        for line in [
            'Coloring margin markup ...',
            ' Activating margin markup color tags in arch-a-score ...',
            '  Found no margin markup color tags in arch-a-score ...',
            ]:
            assert line in lines


def test_AbjadIDE_color_margin_markup_02():
    r'''In segment directory.
    '''

    with ide.Test():

        match = abjad.tags.margin_markup_color_expression_match
        path = ide.Path('green_score', 'segments', '_', 'illustration.ly')
        assert path.is_file()
        assert path.count(match) == ((0, 0), (0, 0))
        
        abjad_ide('gre %_ mmcl q')
        lines = abjad_ide.io.transcript.lines
        assert path.count(match) == ((0, 0), (0, 0))
        for line in [
            'Coloring margin markup ...',
            ' Activating margin markup color tags in _ ...',
            '  Found no margin markup color tags in _ ...',
            ]:
            assert line in lines
        
        abjad_ide('gre %_ mmuc q')
        assert path.count(match) == ((0, 0), (0, 0))
        lines = abjad_ide.io.transcript.lines
        for line in [
            'Uncoloring margin markup ...',
            ' Deactivating margin markup color tags in _ ...',
            '  Found no margin markup color tags in _ ...',
            ]:
            assert line in lines

        abjad_ide('gre %_ mmcl q')
        lines = abjad_ide.io.transcript.lines
        assert path.count(match) == ((0, 0), (0, 0))
        for line in [
            'Coloring margin markup ...',
            ' Activating margin markup color tags in _ ...',
            '  Found no margin markup color tags in _ ...',
            ]:
            assert line in lines
