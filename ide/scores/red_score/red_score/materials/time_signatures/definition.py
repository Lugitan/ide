import abjad
from red_score.materials.magic_numbers.definition import magic_numbers


numerators = magic_numbers[:8]
numerators = [_ % 11 + 1 for _ in numerators]
pairs = [(_, 8) for _ in numerators]
time_signatures = [abjad.TimeSignature(_) for _ in pairs]