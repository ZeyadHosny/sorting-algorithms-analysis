"""Tests for all six chart outputs. Fixture numbers are invented, not project results."""
import builtins
import copy
import math
import os
import struct
import tempfile
import unittest
from unittest.mock import patch

from sorting_analysis.plots import (matplotlib_available, plot_bubble_extrapolation, plot_growth,
                                    plot_input_order, plot_repeated_values, plot_scaling)


# Function to construct a labelled test case with invented timing values
def chart_case(experiment, algorithm, column, order, size, seconds):
    """
    Description:
    - Construct a complete typed chart fixture; the numbers are only for tests.

    Input arguments:
       experiment (str): 'scaling', 'order' or 'dupes'.
       algorithm (str): Sorting algorithm name.
       column (str): Dataset column.
       order (str): Input arrangement.
       size (int): Input size.
       seconds (float): Invented median seconds per sort.

    Return:
        dict: Typed case row for plotting tests.
    """
    return {"experiment": experiment, "algorithm": algorithm, "column": column, "order": order,
            "input_size": size, "comparisons": size * (size - 1) // 2,
            "writes": 0 if order == "sorted" else size * 2, "swaps": None if algorithm == "merge" else 0,
            "sorts_per_batch": 1000 if size <= 20 else 1,
            "median_s": seconds, "min_s": seconds * 0.8, "max_s": seconds * 1.4}


class TestAvailability(unittest.TestCase):
    """Availability checks also work when matplotlib is absent."""

    def test_matplotlib_available_returns_bool(self):
        """Returns True or False without raising."""
        self.assertIs(type(matplotlib_available()), bool)

    def test_missing_matplotlib_returns_false_and_no_files(self):
        """Without matplotlib, availability is False and every plot function returns an empty list."""
        original_import = builtins.__import__

        # Function to simulate an environment where optional matplotlib is not installed
        def without_matplotlib(name, *arguments, **keywords):
            """
            Description:
            - Reject matplotlib imports while leaving all other imports unchanged.

            Input arguments:
               name (str): Imported module name.
               arguments (tuple): Remaining positional import arguments.
               keywords (dict): Keyword import arguments.

            Return:
                module: Imported module (raises ImportError for matplotlib).
            """
            if name == "matplotlib" or name.startswith("matplotlib."):
                raise ImportError("matplotlib intentionally unavailable in this test")
            return original_import(name, *arguments, **keywords)

        with tempfile.TemporaryDirectory() as folder:
            with patch("builtins.__import__", side_effect=without_matplotlib):
                self.assertFalse(matplotlib_available())
                self.assertEqual(plot_scaling([], folder), [])
                self.assertEqual(plot_input_order([], folder), [])
                self.assertEqual(plot_repeated_values([], folder), [])
                self.assertEqual(plot_growth([], folder), [])
                self.assertEqual(plot_bubble_extrapolation([], {}, [], folder), [])
            self.assertEqual(os.listdir(folder), [])


class TestCharts(unittest.TestCase):
    """Chart files (skipped automatically when matplotlib is missing)."""

    # Method to prepare isolated chart fixtures
    def setUp(self):
        """
        Description:
        - Prepare all experiment fixtures and temporary output paths.

        Input arguments:
           None

        Return:
            None
        """
        if not matplotlib_available():
            self.skipTest("matplotlib is not installed")
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = os.path.join(temporary.name, "charts")
        self.cases = []
        for algorithm_index, algorithm in enumerate(("bubble", "selection", "merge")):
            for size in (20, 5, 10, 250):
                self.cases.append(chart_case("scaling", algorithm, "median_income", "random", size,
                                            (algorithm_index + 1) * size * 0.000001))
            for order in ("random", "sorted", "reversed", "nearly"):
                self.cases.append(chart_case("order", algorithm, "median_income", order, 2000,
                                            (algorithm_index + 1) * 0.001))
            for column in ("median_income", "housing_median_age", "median_house_value"):
                self.cases.append(chart_case("dupes", algorithm, column, "random", 2000,
                                            (algorithm_index + 1) * 0.002))
        self.growth = [{"algorithm": algorithm, "size_from": smaller, "size_to": 2 * smaller,
                        "time_from_s": 1.0, "time_to_s": observed, "observed_factor": observed,
                        "theoretical_factor": theoretical}
                       for algorithm, observed, theoretical in (("bubble", 3.5, 4.0),
                                                                 ("selection", 4.1, 4.0), ("merge", 2.3, 2.2))
                       for smaller in (5, 10, 250, 500, 1000, 2000)]
        self.estimate = {"method": "quadratic_fit", "sizes_used": "250;500;1000;2000;4000",
                         "a0": 0.001, "a1": 0.000002, "a2": 0.0000001,
                         "target_size": 20640, "estimate_s": 42.64324}
        self.fitted = []
        self.bubble_cases = []
        for size in (250, 500, 1000, 2000, 4000):
            seconds = 0.001 + 0.000002 * size + 0.0000001 * size ** 2
            self.fitted.append({"input_size": size, "measured_s": seconds, "fitted_s": seconds})
            self.bubble_cases.append(chart_case("scaling", "bubble", "median_income", "random", size, seconds))

    # Method to verify actual PNG bytes rather than just a filename
    def assert_pngs(self, paths, expected_names):
        """
        Description:
        - Check expected basenames and non-empty PNG files with positive image dimensions.

        Input arguments:
           paths (list[str]): Returned file paths.
           expected_names (list[str]): Expected basenames, in order.

        Return:
            None
        """
        self.assertEqual([os.path.basename(path) for path in paths], expected_names)
        for path in paths:
            self.assertEqual(os.path.dirname(path), self.folder)
            with open(path, "rb") as png_file:
                header = png_file.read(24)
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
            width, height = struct.unpack(">II", header[16:24])
            self.assertGreater(width, 0)
            self.assertGreater(height, 0)
            self.assertGreater(os.path.getsize(path), 1000)

    def test_scaling_charts_written(self):
        """Small cases -> PNG files exist in a temporary folder."""
        self.assert_pngs(plot_scaling(self.cases, self.folder),
                         ["scaling_summary.png", "scaling_tiny_runtime.png"])

    def test_input_order_charts_written(self):
        """Small cases -> PNG files exist."""
        self.assert_pngs(plot_input_order(self.cases, self.folder), ["input_order_summary.png"])

    def test_repeated_values_charts_written(self):
        """Small cases -> PNG files exist."""
        self.assert_pngs(plot_repeated_values(self.cases, self.folder), ["repeated_values_summary.png"])

    def test_growth_chart_written(self):
        """Prepared growth rows produce the observed-versus-theoretical PNG."""
        self.assert_pngs(plot_growth(self.growth, self.folder), ["growth_factors.png"])

    def test_bubble_extrapolation_chart_written(self):
        """Existing model outputs produce the measured-fit and extrapolation PNG."""
        self.assert_pngs(plot_bubble_extrapolation(self.bubble_cases, self.estimate, self.fitted, self.folder),
                         ["bubble_extrapolation.png"])

    def test_empty_experiments_write_no_files(self):
        """Empty or absent experiments return no paths and create no folder."""
        self.assertEqual(plot_scaling([], self.folder), [])
        self.assertEqual(plot_input_order([], self.folder), [])
        self.assertEqual(plot_repeated_values([], self.folder), [])
        self.assertEqual(plot_growth([], self.folder), [])
        self.assertEqual(plot_bubble_extrapolation([], {}, [], self.folder), [])
        self.assertFalse(os.path.exists(self.folder))

    def test_no_tiny_values_produce_only_scaling_summary(self):
        """Scaling samples above the tiny-input limit produce only the summary file."""
        rows = [row for row in self.cases if row["experiment"] == "scaling" and row["input_size"] > 20]
        with patch("matplotlib.figure.Figure.savefig"):
            paths = plot_scaling(rows, self.folder)
        self.assertEqual([os.path.basename(path) for path in paths], ["scaling_summary.png"])

    def test_scaling_data_are_sorted_filtered_and_converted_once(self):
        """Scaling uses numeric size order and exact seconds; tiny medians are converted once to µs."""
        captured = []

        # Function to inspect public figure artists immediately before saving
        def inspect_figure(figure, path, **keywords):
            """
            Description:
            - Collect chart artists without rendering another PNG.

            Input arguments:
               figure (Figure): Figure being saved.
               path (str): Output path.
               keywords (dict): Export settings.

            Return:
                None
            """
            captured.append((os.path.basename(path), figure.axes[0].lines[0].get_xdata().tolist(),
                             figure.axes[0].lines[0].get_ydata().tolist()))

        with patch("matplotlib.figure.Figure.savefig", autospec=True, side_effect=inspect_figure):
            plot_scaling(self.cases, self.folder)
        self.assertEqual(captured[0][0:2], ("scaling_summary.png", [5, 10, 20, 250]))
        for actual, expected in zip(captured[0][2], [0.000005, 0.00001, 0.00002, 0.00025]):
            self.assertAlmostEqual(actual, expected, places=12)
        self.assertEqual(captured[1][0:2], ("scaling_tiny_runtime.png", [5, 10, 20]))
        for actual, expected in zip(captured[1][2], [5.0, 10.0, 20.0]):
            self.assertAlmostEqual(actual, expected)

    def test_zero_writes_and_missing_cases_are_not_fabricated(self):
        """True zero writes remain zero on a linear axis; an absent case is a NaN gap with a notice."""
        rows = [row for row in self.cases if row["experiment"] == "order"
                and not (row["algorithm"] == "merge" and row["order"] == "nearly")]
        captured = {}

        # Function to inspect the writes panel before the figure is released
        def inspect_figure(figure, path, **keywords):
            """
            Description:
            - Capture true zeros, missing markers and explanatory figure text.

            Input arguments:
               figure (Figure): Completed chart figure.
               path (str): Export path.
               keywords (dict): Export settings.

            Return:
                None
            """
            axis = figure.axes[2]
            captured["scale"] = axis.get_yscale()
            captured["bubble"] = axis.lines[0].get_ydata().tolist()
            captured["merge"] = axis.lines[2].get_ydata().tolist()
            captured["text"] = " ".join(text.get_text() for text in figure.texts)

        with patch("matplotlib.figure.Figure.savefig", autospec=True, side_effect=inspect_figure):
            plot_input_order(rows, self.folder)
        self.assertEqual(captured["scale"], "linear")
        self.assertEqual(captured["bubble"][1], 0)
        self.assertTrue(math.isnan(captured["merge"][3]))
        self.assertIn("Missing cases: 1", captured["text"])

    def test_invalid_duplicate_and_mixed_case_contexts_raise(self):
        """Duplicate cases, inconsistent n and invalid timing ranges raise ValueError."""
        original = [row for row in self.cases if row["experiment"] == "order"]
        duplicate = original + [original[0].copy()]
        mixed = copy.deepcopy(original)
        mixed[0]["input_size"] = 1000
        invalid = copy.deepcopy(original)
        invalid[0]["min_s"] = invalid[0]["median_s"] * 2
        for rows in (duplicate, mixed, invalid):
            with self.subTest(rows=rows):
                with self.assertRaises(ValueError):
                    plot_input_order(rows, self.folder)

    def test_plots_do_not_modify_input_rows(self):
        """All plotting functions preserve their case, growth and model input records."""
        before = copy.deepcopy((self.cases, self.growth, self.bubble_cases, self.estimate, self.fitted))
        with patch("matplotlib.figure.Figure.savefig"):
            plot_scaling(self.cases, self.folder)
            plot_input_order(self.cases, self.folder)
            plot_repeated_values(self.cases, self.folder)
            plot_growth(self.growth, self.folder)
            plot_bubble_extrapolation(self.bubble_cases, self.estimate, self.fitted, self.folder)
        self.assertEqual((self.cases, self.growth, self.bubble_cases, self.estimate, self.fitted), before)

    def test_growth_distinguishes_observed_and_theoretical_values(self):
        """Growth markers retain the supplied measured factors and distinct theoretical reference values."""
        captured = {}

        # Function to collect the first growth panel's values
        def inspect_figure(figure, path, **keywords):
            """
            Description:
            - Inspect values and legends of the Bubble Sort growth panel.

            Input arguments:
               figure (Figure): Growth figure.
               path (str): Export path.
               keywords (dict): Export settings.

            Return:
                None
            """
            captured["observed"] = figure.axes[0].lines[0].get_ydata().tolist()
            captured["theory"] = figure.axes[0].lines[1].get_ydata().tolist()

        with patch("matplotlib.figure.Figure.savefig", autospec=True, side_effect=inspect_figure):
            plot_growth(self.growth, self.folder)
        self.assertEqual(captured["observed"], [3.5] * 6)
        self.assertEqual(captured["theory"], [4.0] * 6)

    def test_invalid_growth_rows_raise(self):
        """Duplicate growth pairs, non-doubling steps and invalid factors are rejected."""
        invalid = [self.growth[0].copy()]
        invalid[0]["size_to"] = 99
        nonfinite = [self.growth[0].copy()]
        nonfinite[0]["observed_factor"] = float("nan")
        for rows in ([self.growth[0], self.growth[0]], invalid, nonfinite):
            with self.subTest(rows=rows):
                with self.assertRaises(ValueError):
                    plot_growth(rows, self.folder)

    def test_inconsistent_model_prediction_or_measurements_raise(self):
        """A prediction or fitted measurement from a different model/run is rejected."""
        bad_estimate = self.estimate.copy()
        bad_estimate["estimate_s"] += 1
        with self.assertRaises(ValueError):
            plot_bubble_extrapolation(self.bubble_cases, bad_estimate, self.fitted, self.folder)
        bad_fitted = copy.deepcopy(self.fitted)
        bad_fitted[0]["measured_s"] *= 2
        with self.assertRaises(ValueError):
            plot_bubble_extrapolation(self.bubble_cases, self.estimate, bad_fitted, self.folder)

    def test_prediction_is_labelled_and_not_added_to_measured_points(self):
        """The target prediction is a separate marker; measured markers contain only supplied base sizes."""
        captured = {}

        # Function to inspect the measured and full-range model panels
        def inspect_figure(figure, path, **keywords):
            """
            Description:
            - Check measured points and prediction labelling without creating another image.

            Input arguments:
               figure (Figure): Extrapolation figure.
               path (str): Export path.
               keywords (dict): Export settings.

            Return:
                None
            """
            captured["measured_sizes"] = figure.axes[1].lines[0].get_xdata().tolist()
            captured["prediction_size"] = figure.axes[1].lines[3].get_xdata().tolist()
            captured["prediction_label"] = figure.axes[1].lines[3].get_label()

        with patch("matplotlib.figure.Figure.savefig", autospec=True, side_effect=inspect_figure):
            plot_bubble_extrapolation(self.bubble_cases, self.estimate, self.fitted, self.folder)
        self.assertEqual(captured["measured_sizes"], [250, 500, 1000, 2000, 4000])
        self.assertEqual(captured["prediction_size"], [20640.0])
        self.assertEqual(captured["prediction_label"], "Predicted, not measured")


if __name__ == "__main__":
    unittest.main()
