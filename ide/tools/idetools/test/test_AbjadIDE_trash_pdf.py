import ide
import pathlib
abjad_ide = ide.AbjadIDE(is_test=True)


def test_AbjadIDE_trash_pdf_01():
    r'''In material directory.
    '''

    material_directory = pathlib.Path(
        abjad_ide.configuration.example_scores_directory,
        'red_score',
        'red_score',
        'materials',
        'magic_numbers',
        )
    pdf_path = pathlib.Path(material_directory, 'illustration.pdf')

    with ide.Test():
        input_ = 'red~score mm magic~numbers pdfm q'
        abjad_ide._start(input_=input_)
        assert pdf_path.is_file()
        input_ = 'red~score mm magic~numbers pdft q'
        abjad_ide._start(input_=input_)
        assert not pdf_path.exists()


def test_AbjadIDE_trash_pdf_02():
    r'''In segment directory.
    '''

    segment_directory = pathlib.Path(
        abjad_ide.configuration.example_scores_directory,
        'red_score',
        'red_score',
        'segments',
        'segment_01',
        )
    ly_path = pathlib.Path(segment_directory, 'illustration.ly')
    pdf_path = pathlib.Path(segment_directory, 'illustration.pdf')

    with ide.Test():
        input_ = 'red~score gg A pdfm q'
        abjad_ide._start(input_=input_)
        assert pdf_path.is_file()
        input_ = 'red~score gg A pdft q'
        abjad_ide._start(input_=input_)
        assert not pdf_path.exists()
