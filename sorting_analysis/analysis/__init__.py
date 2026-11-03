"""Growth factors and the bubble sort runtime estimate (quadratic regression)."""

# Re-exports: other areas import from here, e.g. `from sorting_analysis.analysis import ...`.

from .common import scaling_cases
from .growth import GROWTH_FIELDS, growth_factors, theoretical_factor
from .extrapolation import (EXTRAPOLATION_FIELDS, FIT_METHOD, FITTED_FIELDS, bubble_times, determinant_3x3,
                            extrapolate_bubble, fit_quadratic, predict_time)

__all__ = ['scaling_cases', 'GROWTH_FIELDS', 'growth_factors', 'theoretical_factor', 'EXTRAPOLATION_FIELDS',
           'FIT_METHOD', 'FITTED_FIELDS', 'bubble_times', 'determinant_3x3', 'extrapolate_bubble', 'fit_quadratic',
           'predict_time']
