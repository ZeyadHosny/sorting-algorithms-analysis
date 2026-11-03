"""
Description:
- Central settings of a run: every path, column, seed, size and timing value.
- Values only: the code that uses them lives in the feature modules.
- Spec: ARCHITECTURE.md F-CFG-1.
"""

# Dataset path, relative to the repository root.
DEFAULT_CSV_PATH = "housing.csv"
# Folder of the official outputs.
DEFAULT_RESULTS_FOLDER = "results"
# The three numeric columns the PDF requires.
DEFAULT_SELECTED_COLUMNS = ("median_income", "housing_median_age", "median_house_value")
# Column of the scaling experiment (PDF 4.2: median_income, little duplication).
DEFAULT_SCALING_COLUMN = "median_income"
# Column of the input-order experiment (PDF 4.3: median_income); must be one of the selected columns,
# so the repeated-values experiment repeats this exact input.
DEFAULT_ORDER_COLUMN = "median_income"
# Seed for drawing sample row indices.
DEFAULT_SAMPLE_SEED = 42
# Seed for the random order shared by the input-order and repeated-values experiments.
DEFAULT_SHUFFLE_SEED = 43
# Seed for the swaps that build the nearly sorted input.
DEFAULT_NEARLY_SORTED_SEED = 44
# Input sizes of the scaling experiment.
DEFAULT_SCALING_SIZES = (5, 10, 20, 250, 500, 1000, 2000, 4000)
# Sample size of the input-order and repeated-values experiments.
DEFAULT_ORDER_SAMPLE_SIZE = 2000
# Timed batches per case; their median is reported.
DEFAULT_TIMED_BATCHES = 5
# Inputs up to this size are "very small" (5, 10 and 20, as confirmed by the instructor).
DEFAULT_SMALL_INPUT_LIMIT = 20
# Sorts per timed batch for very small inputs.
DEFAULT_SMALL_INPUT_REPETITIONS = 1000
# Sorts per timed batch for all other inputs.
DEFAULT_NORMAL_INPUT_REPETITIONS = 1
# Full dataset size for the bubble sort estimate.
DEFAULT_EXTRAPOLATION_TARGET_SIZE = 20640
# Measured sizes the quadratic curve is fitted to (instructor's choice).
DEFAULT_EXTRAPOLATION_BASE_SIZES = (250, 500, 1000, 2000, 4000)


class Settings:
    """
    Description:
    - All settings of one run, passed into every function that needs them.
    - Read the values as attributes, e.g. settings.order_sample_size. Never change them
      after construction; tests build a small Settings(...) instead.
    """

    # Constructor
    def __init__(self, csv_path=DEFAULT_CSV_PATH, results_folder=DEFAULT_RESULTS_FOLDER,
                 selected_columns=DEFAULT_SELECTED_COLUMNS, scaling_column=DEFAULT_SCALING_COLUMN,
                 order_column=DEFAULT_ORDER_COLUMN,
                 sample_seed=DEFAULT_SAMPLE_SEED, shuffle_seed=DEFAULT_SHUFFLE_SEED,
                 nearly_sorted_seed=DEFAULT_NEARLY_SORTED_SEED, scaling_sizes=DEFAULT_SCALING_SIZES,
                 order_sample_size=DEFAULT_ORDER_SAMPLE_SIZE, timed_batches=DEFAULT_TIMED_BATCHES,
                 small_input_limit=DEFAULT_SMALL_INPUT_LIMIT,
                 small_input_repetitions=DEFAULT_SMALL_INPUT_REPETITIONS,
                 normal_input_repetitions=DEFAULT_NORMAL_INPUT_REPETITIONS,
                 extrapolation_target_size=DEFAULT_EXTRAPOLATION_TARGET_SIZE,
                 extrapolation_base_sizes=DEFAULT_EXTRAPOLATION_BASE_SIZES):
        """
        Description:
        - Constructor for the Settings class. Every argument defaults to the constant above it.

        Input arguments:
           csv_path (str): Dataset path, e.g. 'housing.csv'.
           results_folder (str): Folder for official outputs, e.g. 'results'.
           selected_columns (tuple[str]): The three numeric columns used by the experiments.
           scaling_column (str): Column of the scaling experiment.
           order_column (str): Column of the input-order experiment; one of selected_columns.
           sample_seed (int): Seed for drawing sample row indices.
           shuffle_seed (int): Seed for the random order shared by the input-order and repeated-values experiments.
           nearly_sorted_seed (int): Seed for the swaps of the nearly sorted input.
           scaling_sizes (tuple[int]): Input sizes of the scaling experiment.
           order_sample_size (int): Sample size of the input-order and repeated-values experiments.
           timed_batches (int): Timed batches per case.
           small_input_limit (int): Largest input size that counts as very small.
           small_input_repetitions (int): Sorts per timed batch for very small inputs.
           normal_input_repetitions (int): Sorts per timed batch for all other inputs.
           extrapolation_target_size (int): Input size of the bubble sort estimate.
           extrapolation_base_sizes (tuple[int]): Measured sizes the quadratic curve is fitted to.

        Return:
            None
        """
        self.csv_path = csv_path
        self.results_folder = results_folder
        self.selected_columns = selected_columns
        self.scaling_column = scaling_column
        self.order_column = order_column
        self.sample_seed = sample_seed
        self.shuffle_seed = shuffle_seed
        self.nearly_sorted_seed = nearly_sorted_seed
        self.scaling_sizes = scaling_sizes
        self.order_sample_size = order_sample_size
        self.timed_batches = timed_batches
        self.small_input_limit = small_input_limit
        self.small_input_repetitions = small_input_repetitions
        self.normal_input_repetitions = normal_input_repetitions
        self.extrapolation_target_size = extrapolation_target_size
        self.extrapolation_base_sizes = extrapolation_base_sizes


# The official settings of the project.
DEFAULT_SETTINGS = Settings()
