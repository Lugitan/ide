import ide
# test must be false for this file
abjad_ide = ide.AbjadIDE(test=False)


def test_AbjadIDE_aliases_01():
    r'''From material directory.
    '''
    
    if not abjad_ide.test_baca_directories():
        return

    abjad_ide('fab mm metronome sti q')
    transcript = abjad_ide.io.transcript
    assert transcript.titles == [
        'Abjad IDE : scores',
        'Fabergé Investigations (2016)',
        'Fabergé Investigations (2016) : materials',
        'Fabergé Investigations (2016) : materials : metronome_marks',
        'Stirrings Still (2017)',
        ]


def test_AbjadIDE_aliases_02():
    r'''From scores directory.
    '''

    if not abjad_ide.test_baca_directories():
        return

    abjad_ide('sti q')
    transcript = abjad_ide.io.transcript
    assert transcript.titles == [
        'Abjad IDE : scores',
        'Stirrings Still (2017)',
        ]


def test_AbjadIDE_aliases_03():
    r'''With test score.
    '''

    if not abjad_ide.test_baca_directories():
        return

    abjad_ide('red q')
    transcript = abjad_ide.io.transcript
    assert 'Red Shift Hijinks (2006)' in transcript
    assert transcript.titles == [
        'Abjad IDE : scores',
        'Red Score (2017)',
        ]
