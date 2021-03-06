import sys
import traceback

import abjad
import definition

if __name__ == "__main__":

    directory, lilypond_file = ide.Path(__file__).parent, None

    try:
        material = getattr(definition, directory.name)
    except ImportError:
        traceback.print_exc()
        sys.exit(1)

    try:
        with abjad.Timer() as timer:
            if getattr(definition, "__illustrate__", None):
                __illustrate__ = getattr(definition, "__illustrate__")
                lilypond_file = __illustrate__(material)
            elif hasattr(material, "__illustrate__"):
                lilypond_file = material.__illustrate__()
            else:
                print(f"No illustrate method ...")
        count = int(timer.elapsed_time)
        counter = abjad.String("second").pluralize(count)
        message = f"Abjad runtime {count} {counter} ..."
        print(message)
    except Exception:
        traceback.print_exc()
        sys.exit(1)

    if lilypond_file is None:
        sys.exit(0)

    try:
        ly = directory / "illustration.ly"
        with abjad.Timer() as timer:
            abjad.persist.as_ly(lilypond_file, ly, align_tags=89)
        count = int(timer.elapsed_time)
        counter = abjad.String("second").pluralize(count)
        message = f"LilyPond runtime {count} {counter} ..."
        print(message)
    except Exception:
        traceback.print_exc()
        sys.exit(1)

    sys.exit(0)
