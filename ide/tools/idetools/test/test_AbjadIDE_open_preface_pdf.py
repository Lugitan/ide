import ide
abjad_ide = ide.AbjadIDE(is_test=True)


def test_AbjadIDE_open_preface_pdf_01():

    abjad_ide('red~score %letter ro q')
    path = ide.Path('red_score').build('letter', 'preface.pdf')
    transcript = abjad_ide.io.transcript
    assert f'Missing {path.trim()} ...' in transcript