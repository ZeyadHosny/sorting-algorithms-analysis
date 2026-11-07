"""Charts of the experiment results."""

# Re-exports: other areas import from here, e.g. `from sorting_analysis.plots import ...`.

from .charts import (matplotlib_available, plot_bubble_extrapolation, plot_growth,
                     plot_input_order, plot_repeated_values, plot_scaling)

__all__ = ['matplotlib_available', 'plot_input_order', 'plot_repeated_values', 'plot_scaling',
           'plot_growth', 'plot_bubble_extrapolation']
