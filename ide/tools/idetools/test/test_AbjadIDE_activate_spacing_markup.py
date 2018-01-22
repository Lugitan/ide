import abjad
import ide
abjad_ide = ide.AbjadIDE(test=True)


tags_ = (
    abjad.tags.SPACING_MARKUP,
    abjad.tags.SPACING_OVERRIDE_MARKUP,
    )
match = lambda tags: bool(set(tags) & set(tags_))

name = 'spacing markup'

def test_AbjadIDE_activate_spacing_markup_01():
    r'''In build directory.
    '''

    with ide.Test():

        build = ide.Path('green_score', 'builds', 'arch-a-score')
        path = build('_segments', 'segment-_.ly')

        abjad_ide('gre bb arch-a-score ggc q')
        assert path.is_file()
        assert path.count(match) == ((0, 0), (0, 0))
        
        abjad_ide('gre bb arch-a-score spm q')
        lines = abjad_ide.io.transcript.lines
        assert f'Found no spacing markup tags in arch-a-score ...' in lines
        assert path.count(match) == ((0, 0), (0, 0))


def test_AbjadIDE_activate_spacing_markup_02():
    r'''In segment directory.
    '''

    with ide.Test():

        path = ide.Path('green_score', 'segments', '_', 'layout.ly')
        assert path.is_file()
        assert path.count(match) == ((0, 0), (2, 14))
        
        abjad_ide('gre %_ spm q')
        lines = abjad_ide.io.transcript.lines
        assert path.count(match) == ((2, 14), (0, 0))
        for line in [
            'Found 2 spacing markup tags in _ ...',
            ' Activating 2 deactivated spacing markup tags in _ ...',
            ' No already-active spacing markup tags to skip in _ ...',
            ]:
            assert line in lines

        abjad_ide('gre %_ spmx q')
        lines = abjad_ide.io.transcript.lines
        assert path.count(match) == ((0, 0), (2, 14))
        for line in [
            'Found 2 spacing markup tags in _ ...',
            ' Deactivating 2 active spacing markup tags in _ ...',
            ' No already-deactivated spacing markup tags to skip in _ ...',
            ]:
            assert line in lines
