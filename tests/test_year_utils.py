import pytest

from app.utils import year_utils
from app.utils.year_utils import normalize_year_input


@pytest.fixture
def frozen_2026(frozen_now):
    """
    Freezes "now" to 2026-01-01, so the 2-digit-year heuristic in
    normalize_year_input (which compares against the current year's last
    two digits) is deterministic no matter when the suite actually runs.
    With this freeze, the century boundary sits at 26: "00".."26" -> 2000s,
    "27".."99" -> 1900s.
    """
    frozen_now.apply_to(year_utils)
    return frozen_now


class TestTwoDigitYears:
    def test_low_two_digit_maps_to_2000s(self, frozen_2026):
        assert normalize_year_input("05") == 2005

    def test_two_digit_at_boundary_maps_to_2000s(self, frozen_2026):
        # Equal to the current year's last two digits (26) is inclusive.
        assert normalize_year_input("26") == 2026

    def test_two_digit_just_above_boundary_maps_to_1900s(self, frozen_2026):
        assert normalize_year_input("27") == 1927

    def test_high_two_digit_maps_to_1900s(self, frozen_2026):
        assert normalize_year_input("99") == 1999

    def test_zero_maps_to_2000(self, frozen_2026):
        assert normalize_year_input("00") == 2000

    def test_strips_surrounding_whitespace(self, frozen_2026):
        assert normalize_year_input(" 05 ") == 2005


class TestFourDigitYears:
    def test_four_digit_string_passes_through(self, frozen_2026):
        assert normalize_year_input("1994") == 1994

    def test_four_digit_string_passes_through_future_year(self, frozen_2026):
        assert normalize_year_input("2020") == 2020


class TestInvalidInput:
    def test_empty_string_raises_value_error(self, frozen_2026):
        with pytest.raises(ValueError):
            normalize_year_input("")

    def test_non_numeric_string_raises_value_error(self, frozen_2026):
        with pytest.raises(ValueError):
            normalize_year_input("abcd")

    def test_mixed_alnum_raises_value_error(self, frozen_2026):
        with pytest.raises(ValueError):
            normalize_year_input("20x0")


class TestKnownLimitations:
    """
    These tests document existing, slightly surprising behavior of
    normalize_year_input rather than prescribing it as correct. They exist
    so that if this function is ever refactored, the change in behavior is
    a visible, deliberate decision instead of an accidental regression.
    """

    def test_single_digit_string_is_not_expanded_to_four_digits(self, frozen_2026):
        # len(year) == 1 skips the 2-digit branch entirely and falls through
        # to int(year), so "5" comes back as the literal int 5, not 2005.
        # In practice this is caught downstream by the min/max year range
        # check in years_flow.get_year_range, so it's not user-visible today.
        assert normalize_year_input("5") == 5
