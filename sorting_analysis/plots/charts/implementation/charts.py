"""
Description:
- Charts and result tables of the experiment results. The only module that uses matplotlib.
- matplotlib is optional: it is imported inside the functions, never at module level.
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
METRICS = (("median_s", "Median runtime", "Median runtime (s)"),
           ("comparisons", "Comparisons", "Comparisons"),
           ("writes", "Element writes", "Element writes"))
# Input orders appear in the same sequence in every chart.
ORDER_LABELS = {"random": "Random", "sorted": "Already\nsorted",
                "reversed": "Reverse\nsorted", "nearly": "Nearly\nsorted"}
# Readable labels for the selected dataset columns.
COLUMN_LABELS = {"median_income": "Median\nincome", "housing_median_age": "Housing\nmedian age",
                 "median_house_value": "Median\nhouse value"}
# Caption line explaining every plotted or tabulated runtime.
RUNTIME_NOTE = "Measured runtime: median of batch averages."
# Heading, summary focus and file prefix of each experiment.
EXPERIMENT_NAMES = {"scaling": ("Scaling Experiment", "Performance by Input Size", "scaling"),
                    "order": ("Input-Order Experiment", "Effect of Input Arrangement", "input_order"),
                    "dupes": ("Repeated-Values Experiment", "Comparison Across Columns", "repeated_values")}
# Column headings of the result tables, after the category column.
TABLE_HEADINGS = ("Algorithm", "Comparisons", "Writes", "Swaps", "Median runtime")
# Category column heading of each result table.
TABLE_CATEGORY_HEADINGS = {"scaling": "Input size, n", "order": "Input order", "dupes": "Column"}
# Column widths (fractions of the table width); the second set fits the longer column names.
TABLE_WIDTHS = ((0.17, 0.17, 0.17, 0.15, 0.13, 0.21), (0.23, 0.16, 0.16, 0.14, 0.12, 0.19))
# PNG resolution in dots per inch.
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


# Function to draw one result table per experiment
def plot_result_tables(cases, output_folder):
    """
    Description:
    - Comparisons, writes, swaps and median runtime of every case, one table figure per experiment.

    Input arguments:
       cases (list[dict]): Case rows from case_row or read_cases.
       output_folder (str): Folder for the PNG files.

    Return:
        list[str]: paths of the files written (raises ValueError for inconsistent or invalid cases).
    """
    if not matplotlib_available():
        return []
    paths = []
    for experiment in ("scaling", "order", "dupes"):
        rows = _experiment_rows(cases, experiment)
        if rows:
            paths.append(_result_table(rows, experiment, output_folder))
    return paths


# Function to format a runtime with a readable unit
def _format_seconds(seconds):
    """
    Description:
    - Below 1,000 s: three significant figures in µs, ms or s, whichever keeps the number below 1,000.
    - From 1,000 s: whole seconds with thousands separators.

    Input arguments:
       seconds (float): Positive runtime in seconds.

    Return:
        str: e.g. 0.0000118 -> '11.8 µs', 0.00383 -> '3.83 ms', 1.116 -> '1.12 s', 1234.5 -> '1,234 s'.
    """
    units = (("µs", 0.000001), ("ms", 0.001), ("s", 1.0))
    for index, (unit, size) in enumerate(units):
        # '#' keeps trailing zeros (20.0, not 20); a bare trailing point (272.) is dropped.
        text = format(seconds / size, "#.3g").rstrip(".")
        # Move to the next unit when rounding reaches 1,000 (e.g. 999.96 µs).
        if float(text) < 1000:
            return text + " " + unit
        if index == len(units) - 1:
            return format(seconds, ",.0f") + " s"


# Function to draw the result table of one experiment
def _result_table(rows, experiment, output_folder):
    """
    Description:
    - One row per case, grouped by category (size, input order or column) in the summary-chart order.

    Input arguments:
       rows (list[dict]): Validated rows of one experiment.
       experiment (str): 'scaling', 'order' or 'dupes'.
       output_folder (str): PNG destination.

    Return:
        str: Written table path.
    """
    categories, category_field, context = _experiment_layout(rows, experiment)
    name, focus, prefix = EXPERIMENT_NAMES[experiment]
    lookup = {(row["algorithm"], row[category_field]): row for row in rows}
    labels = ORDER_LABELS if experiment == "order" else COLUMN_LABELS
    body = []
    shading = []
    missing = 0
    for category_index, category in enumerate(categories):
        first = True
        for algorithm, style in ALGORITHM_STYLES.items():
            row = lookup.get((algorithm, category))
            if row is None:
                missing += 1
                continue
            # The category is written once, on the first row of its group.
            category_text = format(category, ",") if experiment == "scaling" else \
                labels.get(category, category).replace("\n", " ")
            swaps = "n/a" if row["swaps"] is None else format(int(row["swaps"]), ",")
            body.append([category_text if first else "", style[0], format(int(row["comparisons"]), ","),
                         format(int(row["writes"]), ","), swaps, _format_seconds(float(row["median_s"]))])
            shading.append("#F4F6F8" if category_index % 2 == 0 else "white")
            first = False
    height = 1.6 + 0.27 * (len(body) + 1)
    figure, axes = _new_figure(1, height)
    axis = axes[0]
    axis.axis("off")
    # Title, subtitle and caption keep fixed distances in inches from the figure edges.
    figure.subplots_adjust(left=0.04, right=0.96, top=1 - 1.0 / height, bottom=0.7 / height)
    figure.suptitle(name + ": Results Table", y=1 - 0.2 / height, fontsize=14, fontweight="bold")
    figure.text(0.5, 1 - 0.62 / height, context, ha="center", fontsize=11, color="#465365")
    table = axis.table(cellText=body, colLabels=[TABLE_CATEGORY_HEADINGS[experiment]] + list(TABLE_HEADINGS),
                       colWidths=TABLE_WIDTHS[experiment == "dupes"], bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    for (row_index, column_index), cell in table.get_celld().items():
        cell.set_edgecolor("#D0D5DB")
        cell.set_linewidth(0.5)
        # Text columns are left-aligned, numbers right-aligned.
        cell.get_text().set_horizontalalignment("left" if column_index < 2 else "right")
        cell.PAD = 0.04
        if row_index == 0:
            cell.set_facecolor("#E3E7EC")
            cell.get_text().set_fontweight("bold")
            cell.get_text().set_horizontalalignment("center")
        else:
            cell.set_facecolor(shading[row_index - 1])
    note = RUNTIME_NOTE + "\nSwaps: not applicable to merge sort."
    if missing:
        note += " Missing cases: " + str(missing) + "."
    figure.text(0.04, 0.12 / height, note, fontsize=9, color="#465365", va="bottom")
    return _save_figure(figure, output_folder, prefix + "_table.png")


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
    # Table cell text is not reached by findobj, so it is set separately.
    for axis in figure.axes:
        for table in axis.tables:
            for cell in table.get_celld().values():
                cell.get_text().set_fontfamily(font_family)
    try:
        os.makedirs(output_folder, exist_ok=True)
        path = os.path.join(output_folder, filename)
        figure.savefig(path, dpi=EXPORT_DPI, facecolor="white")
        return path
    finally:
        figure.clear()


# Function to choose the categories and subtitle of one experiment
def _experiment_layout(rows, experiment):
    """
    Description:
    - Shared by the summary charts and the result tables.

    Input arguments:
       rows (list[dict]): Validated rows of one experiment.
       experiment (str): 'scaling', 'order' or 'dupes'.

    Return:
        tuple: (categories in display order, row field holding the category, subtitle),
         e.g. ([5, 10, 20], 'input_size', 'Median income · random order').
    """
    column_label = COLUMN_LABELS.get(rows[0]["column"], rows[0]["column"]).replace("\n", " ")
    sample_size = "n = " + format(rows[0]["input_size"], ",")
    if experiment == "scaling":
        # Sizes are ordered with merge sort, not sorted().
        categories = ALGORITHMS["merge"][0](list({row["input_size"] for row in rows}))
        return categories, "input_size", column_label + " · random order"
    if experiment == "order":
        return list(ORDER_LABELS), "order", column_label + " · " + sample_size
    categories = list(DEFAULT_SELECTED_COLUMNS)
    for row in rows:
        if row["column"] not in categories:
            categories.append(row["column"])
    return categories, "column", "Same sampled rows and row order · " + sample_size


# Function to draw a shared three-panel experiment summary
def _summary_chart(rows, experiment, output_folder):
    """
    Description:
    - Draw runtime, comparisons and writes using consistent algorithm styles.
    - Scaling uses measured-size lines; categorical experiments use unconnected grouped dots.
    - Runtime uses a log axis; writes use a symmetric log axis (linear from 0 to 1), so true zeros
      and small counts stay visible beside counts in the millions.

    Input arguments:
       rows (list[dict]): Validated rows of one experiment.
       experiment (str): 'scaling', 'order' or 'dupes'.
       output_folder (str): PNG destination.

    Return:
        str: Written summary path.
    """
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FixedLocator, FuncFormatter, LogLocator, NullLocator

    categories, category_field, context = _experiment_layout(rows, experiment)
    name, focus, prefix = EXPERIMENT_NAMES[experiment]
    title = name + ": " + focus
    filename = prefix + "_summary.png"
    lookup = {(row["algorithm"], row[category_field]): row for row in rows}
    missing = len(ALGORITHM_STYLES) * len(categories) - len(lookup)
    figure, axes = _new_figure(3, 8.0)
    figure.subplots_adjust(left=0.17, right=0.97, top=0.83, hspace=0.80)
    figure.suptitle(title, y=0.98, fontsize=14, fontweight="bold")
    figure.text(0.5, 0.935, context, ha="center", fontsize=11, color="#465365")
    handles = [Line2D([], [], color=style[1], marker=style[2], linestyle="None", label=style[0])
               for style in ALGORITHM_STYLES.values()]
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.915), ncol=3,
                  frameon=False, fontsize=10)
    for axis, (field, panel_title, ylabel) in zip(axes, METRICS):
        all_values = [float(row[field]) for row in rows]
        positive_values = [value for value in all_values if value > 0]
        # Timings are validated positive; comparisons use log only when every count is positive and varies widely.
        if field == "median_s":
            scale = "log"
        elif field == "writes":
            scale = "symlog"
        elif len(positive_values) == len(all_values) and (
                experiment == "scaling" or max(positive_values) / min(positive_values) >= 100):
            scale = "log"
        else:
            scale = "linear"
        for algorithm_index, (algorithm, style) in enumerate(ALGORITHM_STYLES.items()):
            label, color, marker, line_style = style
            points = [lookup.get((algorithm, category)) for category in categories]
            if not any(point is not None for point in points):
                continue
            positions = categories if experiment == "scaling" else [
                category_index + (algorithm_index - 1) * 0.18 for category_index in range(len(categories))]
            values = [float(point[field]) if point is not None else math.nan for point in points]
            axis.plot(positions, values, marker=marker, color=color,
                      linestyle=line_style if experiment == "scaling" else "None",
                      linewidth=1.4, markersize=5, label=label, clip_on=False)
        if scale == "log":
            axis.set_yscale("log")
            # Label every decade, not only every third.
            axis.yaxis.set_major_locator(LogLocator(base=10, numticks=12))
        elif scale == "symlog":
            axis.set_yscale("symlog", base=10, linthresh=1, linscale=1)
            # The axis reaches the first power of ten above the largest count, at least 10 (also for all zeros).
            largest = max(all_values)
            top_power = max(1, math.ceil(math.log10(largest))) if largest > 1 else 1
            axis.set_ylim(0, 10 ** top_power * 1.3)
            # Ticks at 0, 1 and powers of ten counted down from the top; every second power above 10^4.
            step = 2 if top_power > 4 else 1
            powers = [power for power in range(top_power, 0, -step)]
            axis.yaxis.set_major_locator(FixedLocator([0, 1] + [10 ** power for power in powers]))
            axis.yaxis.set_major_formatter(FuncFormatter(
                lambda value, position: "0" if value == 0 else "1" if value == 1
                else "$\\mathdefault{10^{" + str(round(math.log10(value))) + "}}$"))
            axis.yaxis.set_minor_locator(NullLocator())
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
        axis.set_ylabel(ylabel + {"log": "\n(log scale)", "symlog": "\n(symlog scale)", "linear": ""}[scale],
                        fontsize=11)
    note = RUNTIME_NOTE
    note += "\nWrites: symmetric log scale, linear from 0 to 1, so zero writes remain visible."
    if missing:
        note += "\nMissing cases: " + str(missing) + "; shown as gaps, never zeros."
    note = "\n".join(textwrap.fill(line, width=82) for line in note.splitlines())
    # Leave room below the x-axis labels for every caption line.
    figure.subplots_adjust(bottom=(0.15 if experiment == "scaling" else 0.11) + 0.021 * note.count("\n"))
    figure.text(0.17, 0.025, note, fontsize=9, color="#465365", va="bottom")
    return _save_figure(figure, output_folder, filename)


# Function to draw the small-input runtime detail in microseconds
def _tiny_chart(rows, output_folder):
    """
    Description:
    - Draw the median runtime of each measured size on linear axes.
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
    figure.subplots_adjust(left=0.16, right=0.97, bottom=0.31, top=0.73)
    figure.suptitle(EXPERIMENT_NAMES["scaling"][0] + ": Very Small Inputs", y=0.98, fontsize=14, fontweight="bold")
    context = _experiment_layout(rows, "scaling")[2] + " · n ≤ " + str(DEFAULT_SMALL_INPUT_LIMIT)
    figure.text(0.5, 0.895, context, ha="center", fontsize=11, color="#465365")
    for algorithm, (label, color, marker, line_style) in ALGORITHM_STYLES.items():
        points = [lookup.get((algorithm, size)) for size in sizes]
        if not any(point is not None for point in points):
            continue
        medians = [float(point["median_s"]) * 1_000_000 if point is not None else math.nan for point in points]
        axis.plot(sizes, medians, label=label, color=color, marker=marker, linestyle=line_style,
                  linewidth=1.4, markersize=6)
    axis.set_xticks(sizes)
    axis.set_ylim(bottom=0)
    axis.set_xlabel("Input size, n", fontsize=11)
    axis.set_ylabel("Median runtime (µs)", fontsize=11)
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3, frameon=False, fontsize=10)
    # Batch sizes come from the rows, so the caption matches the data even if the settings change.
    batch_sizes = {int(row["sorts_per_batch"]) for row in rows}
    if len(batch_sizes) == 1:
        batch = format(batch_sizes.pop(), ",")
        batching = "Each batch times " + batch + " sorts; its average is the elapsed time ÷ " + batch + "."
    else:
        batching = "Each batch average is the elapsed time ÷ the number of sorts in the batch."
    figure.text(0.16, 0.025, RUNTIME_NOTE + "\n" + batching + "\n1 µs = 0.000001 s.", fontsize=9,
                color="#465365", va="bottom")
    return _save_figure(figure, output_folder, "scaling_tiny_runtime.png")


# Function to draw measured and theoretical runtime growth factors
def plot_growth(growth_rows, output_folder):
    """
    Description:
    - Show observed and theoretical factors separately for every supplied doubling pair.
    - The growth rows are drawn as given; nothing is recomputed.

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
    - The model is drawn as given, never refitted.

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
    figure.subplots_adjust(left=0.16, right=0.97, top=0.87, hspace=0.65)
    figure.suptitle("Bubble Sort — measured fit and extrapolation", y=0.98, fontsize=14, fontweight="bold")
    for axis in axes:
        axis.plot(sizes, measured_times, color=color, marker="o", linestyle="None", label="Measured median")
        axis.plot(fitted_x, fitted_y, color=color, linestyle="-", linewidth=1.5, label="Quadratic fit")
        axis.set_xlabel("Input size, n", fontsize=11)
        axis.set_ylabel("Runtime (s)", fontsize=11)
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
                     ha="right", fontsize=10,
                     # White background keeps the label readable where the curve passes behind it.
                     bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none"})
    axes[1].set_title("Full range — shaded area is extrapolation", loc="left", fontsize=12, fontweight="bold")
    axes[1].set_xlim(0, target * 1.06)
    axes[1].set_xticks([target * step / 4 for step in range(5)])
    axes[1].legend(frameon=False, fontsize=9, loc="upper left")
    for axis, curve_values in ((axes[0], fitted_y), (axes[1], fitted_y + extrapolated_y)):
        if min(curve_values) >= 0 and prediction >= 0:
            axis.set_ylim(bottom=0)
    # The runtime line, plus a warning when the model gives non-positive runtimes.
    note = RUNTIME_NOTE
    if min(fitted_y + extrapolated_y + [prediction]) <= 0:
        note += "\nWarning: the model includes non-positive runtimes, which are not physically meaningful."
    note = "\n".join(textwrap.fill(line, width=84) for line in note.splitlines())
    # Each caption line takes about 0.021 of the figure height.
    figure.subplots_adjust(bottom=0.10 + 0.021 * (note.count("\n") + 1))
    figure.text(0.16, 0.025, note, fontsize=9, color="#465365", va="bottom")
    return [_save_figure(figure, output_folder, "bubble_extrapolation.png")]
