"""
Description:
- Charts of the experiment results. The only module that uses matplotlib.
- matplotlib is optional: it is imported inside the functions, never at module level.
- Spec: ARCHITECTURE.md F-PLT-1 - F-PLT-4.
"""


import math
import os
import textwrap

from sorting_analysis.config import DEFAULT_SELECTED_COLUMNS, DEFAULT_SMALL_INPUT_LIMIT
from sorting_analysis.experiments import ALGORITHMS


# Labels, colors, markers and line styles shared by all figures.
ALGORITHM_STYLES = {
    "bubble": ("Bubble Sort", "#0072B2", "o", "-"),
    "selection": ("Selection Sort", "#E69F00", "s", "--"),
    "merge": ("Merge Sort", "#009E73", "^", "-."),
}
# Field, panel title and axis label of each summary panel.
METRICS = (("median_s", "Median runtime", "Median runtime (s per sort)"),
           ("comparisons", "Comparisons", "Comparisons per sort"),
           ("writes", "Element writes", "Element writes per sort"))
# Input orders appear in the same sequence in every chart.
ORDER_LABELS = {"random": "Random", "sorted": "Already\nsorted",
                "reversed": "Reverse\nsorted", "nearly": "Nearly\nsorted"}
# Readable labels for the required dataset columns.
COLUMN_LABELS = {"median_income": "Median\nincome", "housing_median_age": "Housing\nmedian age",
                 "median_house_value": "Median\nhouse value"}
# PNG resolution for report and slide exports.
EXPORT_DPI = 300


# Function to check whether matplotlib is installed
def matplotlib_available():
    """
    Description:
    - Try to import matplotlib.

    Input arguments:
       None

    Return:
        bool: True if the charts can be drawn.
    """
    try:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure
    except ImportError:
        return False
    return callable(Figure) and callable(FigureCanvasAgg)


# Function to draw the scaling charts
def plot_scaling(cases, output_folder):
    """
    Description:
    - Runtime, comparisons and writes versus input size for each algorithm.

    Input arguments:
       cases (list[dict]): Case rows from case_row or read_cases.
       output_folder (str): Folder for the PNG files.

    Return:
        list[str]: paths of the files written.
    """
    if not matplotlib_available():
        return []
    rows = _experiment_rows(cases, "scaling")
    if not rows:
        return []
    paths = [_summary_chart(rows, "scaling", output_folder)]
    tiny_rows = [row for row in rows if row["input_size"] <= DEFAULT_SMALL_INPUT_LIMIT]
    if tiny_rows:
        paths.append(_tiny_chart(tiny_rows, output_folder))
    return paths


# Function to draw the input-order charts
def plot_input_order(cases, output_folder):
    """
    Description:
    - Runtime, comparisons and writes per input order for each algorithm.

    Input arguments:
       cases (list[dict]): Case rows from case_row or read_cases.
       output_folder (str): Folder for the PNG files.

    Return:
        list[str]: paths of the files written.
    """
    if not matplotlib_available():
        return []
    rows = _experiment_rows(cases, "order")
    return [_summary_chart(rows, "order", output_folder)] if rows else []


# Function to draw the repeated-values charts
def plot_repeated_values(cases, output_folder):
    """
    Description:
    - Runtime, comparisons and writes per column for each algorithm.

    Input arguments:
       cases (list[dict]): Case rows from case_row or read_cases.
       output_folder (str): Folder for the PNG files.

    Return:
        list[str]: paths of the files written.
    """
    if not matplotlib_available():
        return []
    rows = _experiment_rows(cases, "dupes")
    return [_summary_chart(rows, "dupes", output_folder)] if rows else []


# Function to validate a numeric plotting value
def _finite_number(value, label, positive=False):
    """
    Description:
    - Convert one plotting value to float and reject missing or non-finite values.

    Input arguments:
       value (float): Value to check.
       label (str): Field description used in an error message.
       positive (bool): Whether zero and negative values are also invalid.

    Return:
        float: Checked value (raises ValueError for invalid values).
    """
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(label + " must be a finite number") from error
    if not math.isfinite(number) or (positive and number <= 0):
        raise ValueError(label + " must be " + ("positive and finite" if positive else "finite"))
    return number


# Function to check the context and measurements of one experiment
def _experiment_rows(cases, experiment):
    """
    Description:
    - Select an experiment without changing the input and check that its rows can be compared.
    - A missing case is allowed, but duplicate cases and mixed sample contexts are rejected.

    Input arguments:
       cases (list[dict]): Typed case rows.
       experiment (str): 'scaling', 'order' or 'dupes'.

    Return:
        list[dict]: Matching rows (raises ValueError for inconsistent or invalid measurements).
    """
    rows = [row for row in cases if row["experiment"] == experiment]
    contexts = set()
    seen = set()
    for row in rows:
        if row["algorithm"] not in ALGORITHM_STYLES:
            raise ValueError("Unknown sorting algorithm: " + str(row["algorithm"]))
        size = row["input_size"]
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            raise ValueError("input_size must be a positive integer")
        if experiment == "scaling":
            contexts.add((row["column"], row["order"]))
            category = size
        elif experiment == "order":
            contexts.add((row["column"], size))
            category = row["order"]
            if category not in ORDER_LABELS:
                raise ValueError("Unknown input order: " + str(category))
        else:
            contexts.add((size, row["order"]))
            category = row["column"]
        key = (row["algorithm"], category)
        if key in seen:
            raise ValueError("Duplicate chart case: " + str(key))
        seen.add(key)
        minimum = _finite_number(row["min_s"], "min_s", positive=True)
        median = _finite_number(row["median_s"], "median_s", positive=True)
        maximum = _finite_number(row["max_s"], "max_s", positive=True)
        if not minimum <= median <= maximum:
            raise ValueError("Timings must satisfy min_s <= median_s <= max_s")
        for field in ("comparisons", "writes"):
            if _finite_number(row[field], field) < 0:
                raise ValueError(field + " cannot be negative")
    if len(contexts) > 1:
        raise ValueError("Chart rows must use one consistent column/order/sample-size context")
    if experiment in ("scaling", "dupes") and rows and rows[0]["order"] != "random":
        raise ValueError("Scaling and repeated-value charts require random-order cases")
    return rows


# Function to create a non-interactive figure with readable panels
def _new_figure(panel_count, height):
    """
    Description:
    - Use the Agg canvas directly, so PNG creation opens no GUI and changes no global backend.

    Input arguments:
       panel_count (int): Number of vertically stacked panels.
       height (float): Figure height in inches.

    Return:
        tuple: Figure and a list of its axes.
    """
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    figure = Figure(figsize=(6.5, height), facecolor="white")
    FigureCanvasAgg(figure)
    axes = [figure.add_subplot(panel_count, 1, index + 1) for index in range(panel_count)]
    for axis in axes:
        axis.set_axisbelow(True)
        axis.grid(axis="y", color="#E3E7EC", linewidth=0.6)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.tick_params(labelsize=11)
    return figure, axes


# Function to write and release one completed PNG figure
def _save_figure(figure, output_folder, filename):
    """
    Description:
    - Create the requested folder and save a PNG at the shared export resolution.

    Input arguments:
       figure (Figure): Completed matplotlib figure.
       output_folder (str): Folder for the PNG.
       filename (str): Output basename.

    Return:
        str: Written path; the figure is cleared even if saving fails.
    """
    from matplotlib.font_manager import findfont
    from matplotlib.text import Text

    try:
        findfont("Arial", fallback_to_default=False)
        font_family = "Arial"
    except ValueError:
        font_family = "DejaVu Sans"
    for artist in figure.findobj(match=Text):
        artist.set_fontfamily(font_family)
    try:
        os.makedirs(output_folder, exist_ok=True)
        path = os.path.join(output_folder, filename)
        figure.savefig(path, dpi=EXPORT_DPI, facecolor="white")
        return path
    finally:
        figure.clear()


# Function to draw a shared three-panel experiment summary
def _summary_chart(rows, experiment, output_folder):
    """
    Description:
    - Draw runtime, comparisons and writes using consistent algorithm styles.
    - Scaling uses measured-size lines; categorical experiments use unconnected grouped dots.

    Input arguments:
       rows (list[dict]): Validated rows of one experiment.
       experiment (str): 'scaling', 'order' or 'dupes'.
       output_folder (str): PNG destination.

    Return:
        str: Written summary path.
    """
    from matplotlib.lines import Line2D

    if experiment == "scaling":
        # Metadata sizes are ordered with the project's own Merge Sort, not sorted().
        categories = ALGORITHMS["merge"][0](list({row["input_size"] for row in rows}))
        category_field = "input_size"
        title = "Scaling performance — " + rows[0]["column"]
        filename = "scaling_summary.png"
    elif experiment == "order":
        categories = list(ORDER_LABELS)
        category_field = "order"
        title = "Effect of input order — " + rows[0]["column"]
        filename = "input_order_summary.png"
    else:
        categories = list(DEFAULT_SELECTED_COLUMNS)
        for row in rows:
            if row["column"] not in categories:
                categories.append(row["column"])
        category_field = "column"
        title = "Results across dataset columns"
        filename = "repeated_values_summary.png"
    lookup = {(row["algorithm"], row[category_field]): row for row in rows}
    missing = len(ALGORITHM_STYLES) * len(categories) - len(lookup)
    figure, axes = _new_figure(3, 8.0)
    figure.subplots_adjust(left=0.17, right=0.97, bottom=0.15 if experiment == "scaling" else 0.11, top=0.83,
                           hspace=0.80)
    figure.suptitle(title, y=0.98, fontsize=14, fontweight="bold")
    context = "Random order" if experiment == "scaling" else "n = " + format(rows[0]["input_size"], ",")
    figure.text(0.5, 0.935, context, ha="center", fontsize=11, color="#465365")
    handles = [Line2D([], [], color=style[1], marker=style[2], linestyle="None", label=style[0])
               for style in ALGORITHM_STYLES.values()]
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.915), ncol=3,
                  frameon=False, fontsize=10)
    for axis, (field, panel_title, ylabel) in zip(axes, METRICS):
        all_values = [float(row[field]) for row in rows]
        positive_values = [value for value in all_values if value > 0]
        logarithmic = field != "writes" and len(positive_values) == len(all_values) and (
            experiment == "scaling" or max(positive_values) / min(positive_values) >= 100)
        for algorithm_index, (algorithm, style) in enumerate(ALGORITHM_STYLES.items()):
            label, color, marker, line_style = style
            points = [lookup.get((algorithm, category)) for category in categories]
            if not any(point is not None for point in points):
                continue
            positions = categories if experiment == "scaling" else [
                category_index + (algorithm_index - 1) * 0.18 for category_index in range(len(categories))]
            values = [float(point[field]) if point is not None else math.nan for point in points]
            if field == "median_s":
                lower = [float(point["median_s"]) - float(point["min_s"]) if point is not None else math.nan
                         for point in points]
                upper = [float(point["max_s"]) - float(point["median_s"]) if point is not None else math.nan
                         for point in points]
                axis.errorbar(positions, values, yerr=[lower, upper], marker=marker, color=color,
                              linestyle=line_style if experiment == "scaling" else "None",
                              linewidth=1.4, markersize=5, capsize=2, label=label)
            else:
                axis.plot(positions, values, marker=marker, color=color,
                          linestyle=line_style if experiment == "scaling" else "None",
                          linewidth=1.4, markersize=5, label=label, clip_on=False)
        if logarithmic:
            axis.set_yscale("log")
        else:
            axis.set_ylim(bottom=0)
            axis.ticklabel_format(axis="y", style="sci", scilimits=(-3, 4), useMathText=True)
        if experiment == "scaling":
            axis.set_xscale("log")
            axis.set_xticks(categories, [str(size) for size in categories], rotation=25)
            axis.set_xlabel("Input size, n (log scale)", fontsize=11)
        else:
            axis.set_xticks(range(len(categories)), [ORDER_LABELS[category] if experiment == "order"
                                                    else COLUMN_LABELS.get(category, category)
                                                    for category in categories])
            axis.set_xlim(-0.55, len(categories) - 0.45)
        axis.set_title(panel_title, loc="left", fontsize=12, fontweight="bold", pad=8)
        axis.set_ylabel(ylabel + ("\n(log scale)" if logarithmic else ""), fontsize=11)
    note = "Runtime: median with observed min–max range; not a confidence interval."
    if missing:
        note += "\nMissing cases: " + str(missing) + "; shown as gaps, never zeros."
    note = "\n".join(textwrap.fill(line, width=82) for line in note.splitlines())
    figure.text(0.17, 0.025, note, fontsize=9, color="#465365", va="bottom")
    return _save_figure(figure, output_folder, filename)


# Function to draw the small-input runtime detail in microseconds
def _tiny_chart(rows, output_folder):
    """
    Description:
    - Draw individual measured sizes on linear axes, retaining min–max timing ranges.
    - Convert seconds to microseconds for display only; batch repetitions are not divided again.

    Input arguments:
       rows (list[dict]): Validated tiny scaling rows.
       output_folder (str): PNG destination.

    Return:
        str: Written tiny-runtime path.
    """
    sizes = ALGORITHMS["merge"][0](list({row["input_size"] for row in rows}))
    lookup = {(row["algorithm"], row["input_size"]): row for row in rows}
    figure, axes = _new_figure(1, 4.6)
    axis = axes[0]
    figure.subplots_adjust(left=0.16, right=0.97, bottom=0.23, top=0.79)
    figure.suptitle("Very small inputs — " + rows[0]["column"], y=0.98, fontsize=14, fontweight="bold")
    for algorithm, (label, color, marker, line_style) in ALGORITHM_STYLES.items():
        points = [lookup.get((algorithm, size)) for size in sizes]
        if not any(point is not None for point in points):
            continue
        medians = [float(point["median_s"]) * 1_000_000 if point is not None else math.nan for point in points]
        lower = [(float(point["median_s"]) - float(point["min_s"])) * 1_000_000
                 if point is not None else math.nan for point in points]
        upper = [(float(point["max_s"]) - float(point["median_s"])) * 1_000_000
                 if point is not None else math.nan for point in points]
        axis.errorbar(sizes, medians, yerr=[lower, upper], label=label, color=color, marker=marker,
                      linestyle=line_style, capsize=3, linewidth=1.4, markersize=6)
    axis.set_xticks(sizes)
    axis.set_ylim(bottom=0)
    axis.set_xlabel("Input size, n", fontsize=11)
    axis.set_ylabel("Median runtime (µs per sort)", fontsize=11)
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3, frameon=False, fontsize=10)
    figure.text(0.16, 0.06, "Whiskers: observed min–max range. 1 µs = 0.000001 s.\n"
                "Very small inputs: n ≤ " + str(DEFAULT_SMALL_INPUT_LIMIT) + ", as confirmed by the instructor.",
                fontsize=9, color="#465365")
    return _save_figure(figure, output_folder, "scaling_tiny_runtime.png")


# Function to draw measured and theoretical runtime growth factors
def plot_growth(growth_rows, output_folder):
    """
    Description:
    - Show observed and theoretical factors separately for every supplied doubling pair.
    - Use the prepared growth rows; do not recompute or rerun the timing experiments.

    Input arguments:
       growth_rows (list[dict]): Typed rows returned by growth_factors or read from growth.csv.
       output_folder (str): Folder for the PNG.

    Return:
        list[str]: Written file paths; empty if no rows or matplotlib is unavailable
                   (raises ValueError for duplicate or invalid growth rows).
    """
    if not matplotlib_available() or not growth_rows:
        return []
    from matplotlib.lines import Line2D

    lookup = {}
    for row in growth_rows:
        algorithm = row["algorithm"]
        smaller, larger = row["size_from"], row["size_to"]
        if algorithm not in ALGORITHM_STYLES or smaller <= 0 or larger != 2 * smaller:
            raise ValueError("Growth charts require a known algorithm and a doubling pair")
        key = (algorithm, smaller, larger)
        if key in lookup:
            raise ValueError("Duplicate growth row: " + str(key))
        _finite_number(row["observed_factor"], "observed_factor", positive=True)
        _finite_number(row["theoretical_factor"], "theoretical_factor", positive=True)
        lookup[key] = row
    pairs = ALGORITHMS["merge"][0](list({(row["size_from"], row["size_to"]) for row in growth_rows}))
    maximum = max(float(row[field]) for row in growth_rows for field in ("observed_factor", "theoretical_factor"))
    figure, axes = _new_figure(3, 8.4)
    figure.subplots_adjust(left=0.16, right=0.97, bottom=0.15, top=0.86, hspace=0.90)
    figure.suptitle("Runtime growth when input size doubles", y=0.98, fontsize=14, fontweight="bold")
    handles = [Line2D([], [], marker="o", color="#465365", linestyle="None", label="Observed"),
               Line2D([], [], marker="D", markerfacecolor="none", color="#596579",
                      linestyle="None", label="Theoretical reference")]
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.945), ncol=2,
                  frameon=False, fontsize=10)
    for axis, (algorithm, style) in zip(axes, ALGORITHM_STYLES.items()):
        label, color, marker, line_style = style
        points = [lookup.get((algorithm, smaller, larger)) for smaller, larger in pairs]
        observed = [float(point["observed_factor"]) if point is not None else math.nan for point in points]
        theoretical = [float(point["theoretical_factor"]) if point is not None else math.nan for point in points]
        axis.plot([index - 0.06 for index in range(len(pairs))], observed, linestyle="None", marker=marker,
                  color=color, markersize=6, label="Observed")
        axis.plot([index + 0.06 for index in range(len(pairs))], theoretical, linestyle="None", marker="D",
                  markerfacecolor="none", color="#596579", markersize=6, label="Theoretical reference")
        axis.set_xticks(range(len(pairs)), [format(smaller, ",") + "\n→ " + format(larger, ",")
                                          for smaller, larger in pairs])
        axis.set_ylim(0, maximum * 1.15)
        axis.set_ylabel("Runtime multiplier (×)", fontsize=11)
        axis.set_title(label, loc="left", fontsize=12, fontweight="bold", pad=8)
        if not any(point is not None for point in points):
            axis.text(0.5, 0.45, "No measured doubling pairs", transform=axis.transAxes, ha="center", fontsize=11)
    figure.text(0.16, 0.025, "Observed: T(2n) / T(n). References are theoretical, not measurements.\n"
                "Non-doubling steps are excluded; missing pairs remain gaps.", fontsize=9, color="#465365")
    return [_save_figure(figure, output_folder, "growth_factors.png")]


# Function to draw the measured Bubble Sort fit and its extrapolated prediction
def plot_bubble_extrapolation(cases, estimate_row, fitted_rows, output_folder):
    """
    Description:
    - Show measured Bubble Sort scaling points and the supplied quadratic model in two panels.
    - The left panel covers the fitted sizes; the right includes the explicitly labelled prediction.
    - Do not fit another model or time the full dataset here.

    Input arguments:
       cases (list[dict]): Typed case rows, used for the measured Bubble Sort base sizes only.
       estimate_row (dict): EXTRAPOLATION_FIELDS row returned by extrapolate_bubble.
       fitted_rows (list[dict]): Its measured-versus-fitted rows with FITTED_FIELDS keys.
       output_folder (str): Folder for the PNG.

    Return:
        list[str]: Written paths; empty if no estimate, fitted rows or matplotlib
                   (raises ValueError for inconsistent or non-finite model data).
    """
    if not matplotlib_available() or not estimate_row or not fitted_rows:
        return []
    if estimate_row.get("method") != "quadratic_fit":
        raise ValueError("Extrapolation chart expects the supplied quadratic_fit model")
    coefficients = [_finite_number(estimate_row[field], field) for field in ("a0", "a1", "a2")]
    target = _finite_number(estimate_row["target_size"], "target_size", positive=True)
    prediction = _finite_number(estimate_row["estimate_s"], "estimate_s")
    model_prediction = coefficients[0] + coefficients[1] * target + coefficients[2] * target ** 2
    if not math.isclose(prediction, model_prediction, rel_tol=1e-9, abs_tol=1e-12):
        raise ValueError("estimate_s does not match the supplied coefficients")
    fit_by_size = {}
    for row in fitted_rows:
        size = row["input_size"]
        if size <= 0 or size in fit_by_size:
            raise ValueError("Fit sizes must be positive and unique")
        measured = _finite_number(row["measured_s"], "measured_s", positive=True)
        fitted = _finite_number(row["fitted_s"], "fitted_s")
        expected = coefficients[0] + coefficients[1] * size + coefficients[2] * size ** 2
        if not math.isclose(fitted, expected, rel_tol=1e-9, abs_tol=1e-12):
            raise ValueError("fitted_s does not match the supplied coefficients")
        fit_by_size[size] = measured
    sizes = ALGORITHMS["merge"][0](list(fit_by_size))
    if len(sizes) < 3 or target <= sizes[-1]:
        raise ValueError("Extrapolation needs at least three fitted sizes and a target beyond them")
    declared_sizes = [int(size) for size in str(estimate_row["sizes_used"]).split(";")]
    if ALGORITHMS["merge"][0](declared_sizes) != sizes:
        raise ValueError("sizes_used must match the fitted rows")
    base_cases = [row for row in cases if row["experiment"] == "scaling" and row["algorithm"] == "bubble"
                  and row["input_size"] in fit_by_size]
    checked = _experiment_rows(base_cases, "scaling")
    if len(checked) != len(sizes):
        raise ValueError("Every fitted size must have one measured Bubble Sort case")
    for row in checked:
        if not math.isclose(float(row["median_s"]), fit_by_size[row["input_size"]], rel_tol=1e-9, abs_tol=1e-12):
            raise ValueError("Fitted rows and cases contain different measured medians")
    measured_times = [fit_by_size[size] for size in sizes]
    fitted_x = [sizes[0] + (sizes[-1] - sizes[0]) * step / 119 for step in range(120)]
    extrapolated_x = [sizes[-1] + (target - sizes[-1]) * step / 119 for step in range(120)]
    fitted_y = [coefficients[0] + coefficients[1] * size + coefficients[2] * size ** 2 for size in fitted_x]
    extrapolated_y = [coefficients[0] + coefficients[1] * size + coefficients[2] * size ** 2
                      for size in extrapolated_x]
    if not all(math.isfinite(value) for value in fitted_y + extrapolated_y):
        raise ValueError("Quadratic curve contains non-finite values")
    color = ALGORITHM_STYLES["bubble"][1]
    figure, axes = _new_figure(2, 7.3)
    figure.subplots_adjust(left=0.16, right=0.97, bottom=0.14, top=0.87, hspace=0.65)
    figure.suptitle("Bubble Sort — measured fit and extrapolation", y=0.98, fontsize=14, fontweight="bold")
    for axis in axes:
        axis.plot(sizes, measured_times, color=color, marker="o", linestyle="None", label="Measured median")
        axis.plot(fitted_x, fitted_y, color=color, linestyle="-", linewidth=1.5, label="Quadratic fit")
        axis.set_xlabel("Input size, n", fontsize=11)
        axis.set_ylabel("Runtime (s per sort)", fontsize=11)
        axis.ticklabel_format(axis="y", style="sci", scilimits=(-3, 4), useMathText=True)
    axes[0].set_title("Measured range — view of model fit", loc="left", fontsize=12, fontweight="bold")
    axes[0].set_xlim(0, sizes[-1] * 1.06)
    axes[0].set_xticks([sizes[-1] * step / 4 for step in range(5)])
    axes[0].legend(frameon=False, fontsize=9)
    axes[1].axvspan(sizes[-1], target, color="#E3E7EC", alpha=0.6)
    axes[1].plot(extrapolated_x, extrapolated_y, color=color, linestyle="--", linewidth=1.5,
                 label="Extrapolated model")
    axes[1].plot([target], [prediction], color=color, marker="X", markersize=8, linestyle="None",
                 label="Predicted, not measured")
    axes[1].annotate("Predicted at n = " + format(int(target), ",") + ": " + format(prediction, ".4g") + " s",
                     xy=(target, prediction), xytext=(-8, -25), textcoords="offset points",
                     ha="right", fontsize=10)
    axes[1].set_title("Full range — shaded area is extrapolation", loc="left", fontsize=12, fontweight="bold")
    axes[1].set_xlim(0, target * 1.06)
    axes[1].set_xticks([target * step / 4 for step in range(5)])
    axes[1].legend(frameon=False, fontsize=9, loc="upper left")
    for axis, curve_values in ((axes[0], fitted_y), (axes[1], fitted_y + extrapolated_y)):
        if min(curve_values) >= 0 and prediction >= 0:
            axis.set_ylim(bottom=0)
    note = "Dashed curve and X marker are predictions, not additional timing measurements.\n"
    note += "The model is extended beyond the largest fitted input; prediction accuracy is not established."
    if min(fitted_y + extrapolated_y + [prediction]) <= 0:
        note += "\nWarning: the model includes non-positive runtimes, which are not physically meaningful."
    note = "\n".join(textwrap.fill(line, width=84) for line in note.splitlines())
    figure.text(0.16, 0.025, note, fontsize=9, color="#465365", va="bottom")
    return [_save_figure(figure, output_folder, "bubble_extrapolation.png")]
