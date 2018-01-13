import abjad
import ide
abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_activate_markup_01():

    ly_paths = []
    for name in ('_', 'A', 'B'):
        ly_name = f'segment-{name}.ly'
        ly_path = ide.Path('red_score', 'builds', 'letter-score')._segments(ly_name)
        ly_paths.append(ly_path)

    with ide.Test(remove=[ly_paths]):

        abjad_ide('red %let ctm q')
        transcript = abjad_ide.io.transcript
        tag = abjad.tags.CLOCK_TIME_MARKUP
        for ly_path in ly_paths:
            line = f'No {tag} tags to activate ...'
            assert line in transcript


def test_AbjadIDE_activate_markup_02():

    abjad_ide('blu %let ctm q')
    transcript = abjad_ide.io.transcript
    assert 'No _segments directory found ...' in transcript
