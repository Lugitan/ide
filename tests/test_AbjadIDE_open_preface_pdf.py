import ide

abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_open_preface_pdf_01():

    abjad_ide("red %letter pfpo q")
    transcript = abjad_ide.io.transcript
    assert f"No files matching preface.pdf ..." in transcript