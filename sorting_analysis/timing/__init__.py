"""Repeated, verified runtime measurement."""

# Re-exports: other areas import from here, e.g. `from sorting_analysis.timing import ...`.

from .benchmark import TimingResult, VerificationError, benchmark, median_of

__all__ = ['TimingResult', 'VerificationError', 'benchmark', 'median_of']
