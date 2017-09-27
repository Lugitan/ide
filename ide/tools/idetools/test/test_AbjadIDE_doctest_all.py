import abjad
import ide
abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_doctest_all_01():
    r'''In contents directory.
    '''

    abjad_ide('red ^^ q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^' to 11 files ..." in transcript

    abjad_ide('red ^^def q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^def' to 8 files ..." in transcript

    abjad_ide('red ^^magic q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^magic' to 0 files ..." in transcript

    abjad_ide('red ^^A q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^A' to 0 files ..." in transcript

    abjad_ide('red ^^ST q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^ST' to 1 file ..." in transcript


def test_AbjadIDE_doctest_all_02():
    r'''In materials directory.
    '''

    abjad_ide('red mm ^^ q')
    transcript = abjad_ide.io.transcript 
    assert f"Matching '^^' to 5 files ..." in transcript

    abjad_ide('red mm ^^def q')
    transcript = abjad_ide.io.transcript 
    assert f"Matching '^^def' to 5 files ..." in transcript

    abjad_ide('red mm ^^magic q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^magic' to 0 files ..." in transcript

    abjad_ide('red mm ^^ST q')
    transcript = abjad_ide.io.transcript 
    assert f"Matching '^^ST' to 0 files ..." in transcript


def test_AbjadIDE_doctest_all_03():
    r'''In segments directory.
    '''

    abjad_ide('red gg ^^ q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^' to 3 files ..." in transcript

    abjad_ide('red gg ^^def q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^def' to 3 files ..." in transcript

    abjad_ide('red gg ^^A q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^A' to 0 files ..." in transcript

    abjad_ide('red gg ^^ST q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^ST' to 0 files ..." in transcript


def test_AbjadIDE_doctest_all_04():
    r'''In test directory.
    '''

    abjad_ide('red tt ^^ q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^' to 0 files ..." in transcript


def test_AbjadIDE_doctest_all_05():
    r'''Handles numeric input.
    '''

    abjad_ide('red oo ^^0 q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^0' to 0 files ..." in transcript

    abjad_ide('red oo ^^1 q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^1' to 0 files ..." in transcript

    abjad_ide('red oo ^^99 q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^99' to 0 files ..." in transcript


def test_AbjadIDE_doctest_all_06():
    r'''Emtpy and junk addresses.
    '''

    abjad_ide('^^asdf q')
    transcript = abjad_ide.io.transcript 
    assert "Matching '^^asdf' to 0 files ..." in transcript