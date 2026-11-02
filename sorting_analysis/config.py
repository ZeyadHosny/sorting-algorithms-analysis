"""
Description:
- Central settings of a run: every seed, size, column name, path and timing value.
- Spec: ARCHITECTURE.md F-CFG-1, F-CFG-2.
"""


# Dataset path, relative to the repository root.
DEFAULT_CSV_PATH = "housing.csv"
# Folder of the official outputs.
DEFAULT_RESULTS_FOLDER = "results"
# The three numeric columns the PDF requires.
DEFAULT_SELECTED_COLUMNS = ("median_income", "housing_median_age", "median_house_value")
# Column with little duplication, used by the scaling and input-order experiments.
DEFAULT_SCALING_COLUMN = "median_income"
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
# Inputs up to this size are 'very small'.
DEFAULT_SMALL_INPUT_LIMIT = 20
# Sorts per timed batch for very small inputs.
DEFAULT_SMALL_INPUT_REPETITIONS = 1000
# Sorts per timed batch for all other inputs.
DEFAULT_NORMAL_INPUT_REPETITIONS = 1
# Full dataset size for the bubble sort estimate.
DEFAULT_EXTRAPOLATION_TARGET_SIZE = 20640
# Measured sizes used as bases for the estimate.
DEFAULT_EXTRAPOLATION_BASE_SIZES = (1000, 2000, 4000)


class Settings:
    """
    Description:
    - All tunable values of one run: seeds, sizes, columns, paths and timing.
    - One object is passed into every function that needs it; tests build a small one.
    - Every attribute is private and read through a getter.

    Attributes:
        __csv_path (str): PRIVATE. Dataset path, e.g. 'housing.csv'.
        __results_folder (str): PRIVATE. Folder for official outputs, e.g. 'results'.
        __selected_columns (tuple[str]): PRIVATE. The three numeric columns used by the experiments.
        __scaling_column (str): PRIVATE. Column of the scaling and input-order experiments.
        __sample_seed (int): PRIVATE. Seed for drawing sample row indices.
        __shuffle_seed (int): PRIVATE. Seed for the random order shared by the input-order and repeated-values experiments.
        __nearly_sorted_seed (int): PRIVATE. Seed for the swaps of the nearly sorted input.
        __scaling_sizes (tuple[int]): PRIVATE. Input sizes of the scaling experiment.
        __order_sample_size (int): PRIVATE. Sample size of the input-order and repeated-values experiments.
        __timed_batches (int): PRIVATE. Timed batches per case.
        __small_input_limit (int): PRIVATE. Largest input size that uses small_input_repetitions.
        __small_input_repetitions (int): PRIVATE. Sorts per timed batch for very small inputs.
        __normal_input_repetitions (int): PRIVATE. Sorts per timed batch for all other inputs.
        __extrapolation_target_size (int): PRIVATE. Input size of the bubble sort estimate.
        __extrapolation_base_sizes (tuple[int]): PRIVATE. Measured sizes used as bases for the estimate.

    Methods:
        __init__: constructor.
        get_csv_path, get_results_folder, get_selected_columns, get_scaling_column,
            get_sample_seed, get_shuffle_seed, get_nearly_sorted_seed, get_scaling_sizes,
            get_order_sample_size, get_timed_batches, get_small_input_limit,
            get_small_input_repetitions, get_normal_input_repetitions,
            get_extrapolation_target_size,
            get_extrapolation_base_sizes: the only way to read each attribute.
        with_csv_path: a copy with another dataset path.
        repetitions_for: sorts per timed batch for an input size.
    """

    # Constructor
    def __init__(self, csv_path=DEFAULT_CSV_PATH, results_folder=DEFAULT_RESULTS_FOLDER, selected_columns=DEFAULT_SELECTED_COLUMNS, scaling_column=DEFAULT_SCALING_COLUMN, sample_seed=DEFAULT_SAMPLE_SEED, shuffle_seed=DEFAULT_SHUFFLE_SEED, nearly_sorted_seed=DEFAULT_NEARLY_SORTED_SEED, scaling_sizes=DEFAULT_SCALING_SIZES, order_sample_size=DEFAULT_ORDER_SAMPLE_SIZE, timed_batches=DEFAULT_TIMED_BATCHES, small_input_limit=DEFAULT_SMALL_INPUT_LIMIT, small_input_repetitions=DEFAULT_SMALL_INPUT_REPETITIONS, normal_input_repetitions=DEFAULT_NORMAL_INPUT_REPETITIONS, extrapolation_target_size=DEFAULT_EXTRAPOLATION_TARGET_SIZE, extrapolation_base_sizes=DEFAULT_EXTRAPOLATION_BASE_SIZES):
        """
        Description:
        - Constructor for the Settings class.

        Input arguments:
           csv_path (str): Dataset path, e.g. 'housing.csv'.
           results_folder (str): Folder for official outputs, e.g. 'results'.
           selected_columns (tuple[str]): The three numeric columns used by the experiments.
           scaling_column (str): Column of the scaling and input-order experiments.
           sample_seed (int): Seed for drawing sample row indices.
           shuffle_seed (int): Seed for the random order shared by the input-order and repeated-values experiments.
           nearly_sorted_seed (int): Seed for the swaps of the nearly sorted input.
           scaling_sizes (tuple[int]): Input sizes of the scaling experiment.
           order_sample_size (int): Sample size of the input-order and repeated-values experiments.
           timed_batches (int): Timed batches per case.
           small_input_limit (int): Largest input size that uses small_input_repetitions.
           small_input_repetitions (int): Sorts per timed batch for very small inputs.
           normal_input_repetitions (int): Sorts per timed batch for all other inputs.
           extrapolation_target_size (int): Input size of the bubble sort estimate.
           extrapolation_base_sizes (tuple[int]): Measured sizes used as bases for the estimate.

        Return:
            None
        """
        self.__csv_path = csv_path
        self.__results_folder = results_folder
        self.__selected_columns = selected_columns
        self.__scaling_column = scaling_column
        self.__sample_seed = sample_seed
        self.__shuffle_seed = shuffle_seed
        self.__nearly_sorted_seed = nearly_sorted_seed
        self.__scaling_sizes = scaling_sizes
        self.__order_sample_size = order_sample_size
        self.__timed_batches = timed_batches
        self.__small_input_limit = small_input_limit
        self.__small_input_repetitions = small_input_repetitions
        self.__normal_input_repetitions = normal_input_repetitions
        self.__extrapolation_target_size = extrapolation_target_size
        self.__extrapolation_base_sizes = extrapolation_base_sizes

    # Method to read the dataset path
    def get_csv_path(self):
        """
        Description:
        - Return the dataset path.

        Input arguments:
           None

        Return:
            str: Dataset path, e.g. 'housing.csv'.
        """
        return self.__csv_path

    # Method to read the results folder
    def get_results_folder(self):
        """
        Description:
        - Return the results folder.

        Input arguments:
           None

        Return:
            str: Folder for official outputs, e.g. 'results'.
        """
        return self.__results_folder

    # Method to read the selected columns
    def get_selected_columns(self):
        """
        Description:
        - Return the selected columns.

        Input arguments:
           None

        Return:
            tuple[str]: The three numeric columns used by the experiments.
        """
        return self.__selected_columns

    # Method to read the scaling column
    def get_scaling_column(self):
        """
        Description:
        - Return the scaling column.

        Input arguments:
           None

        Return:
            str: Column of the scaling and input-order experiments.
        """
        return self.__scaling_column

    # Method to read the sampling seed
    def get_sample_seed(self):
        """
        Description:
        - Return the sampling seed.

        Input arguments:
           None

        Return:
            int: Seed for drawing sample row indices.
        """
        return self.__sample_seed

    # Method to read the shuffle seed
    def get_shuffle_seed(self):
        """
        Description:
        - Return the shuffle seed.

        Input arguments:
           None

        Return:
            int: Seed for the random order shared by the input-order and repeated-values experiments.
        """
        return self.__shuffle_seed

    # Method to read the nearly-sorted seed
    def get_nearly_sorted_seed(self):
        """
        Description:
        - Return the nearly-sorted seed.

        Input arguments:
           None

        Return:
            int: Seed for the swaps of the nearly sorted input.
        """
        return self.__nearly_sorted_seed

    # Method to read the scaling sizes
    def get_scaling_sizes(self):
        """
        Description:
        - Return the scaling sizes.

        Input arguments:
           None

        Return:
            tuple[int]: Input sizes of the scaling experiment.
        """
        return self.__scaling_sizes

    # Method to read the order sample size
    def get_order_sample_size(self):
        """
        Description:
        - Return the order sample size.

        Input arguments:
           None

        Return:
            int: Sample size of the input-order and repeated-values experiments.
        """
        return self.__order_sample_size

    # Method to read the number of timed batches
    def get_timed_batches(self):
        """
        Description:
        - Return the number of timed batches.

        Input arguments:
           None

        Return:
            int: Timed batches per case.
        """
        return self.__timed_batches

    # Method to read the very-small input limit
    def get_small_input_limit(self):
        """
        Description:
        - Return the very-small input limit.

        Input arguments:
           None

        Return:
            int: Largest input size that uses small_input_repetitions.
        """
        return self.__small_input_limit

    # Method to read the sorts per batch for very small inputs
    def get_small_input_repetitions(self):
        """
        Description:
        - Return the sorts per batch for very small inputs.

        Input arguments:
           None

        Return:
            int: Sorts per timed batch for very small inputs.
        """
        return self.__small_input_repetitions

    # Method to read the sorts per batch for other inputs
    def get_normal_input_repetitions(self):
        """
        Description:
        - Return the sorts per batch for other inputs.

        Input arguments:
           None

        Return:
            int: Sorts per timed batch for all other inputs.
        """
        return self.__normal_input_repetitions

    # Method to read the extrapolation target size
    def get_extrapolation_target_size(self):
        """
        Description:
        - Return the extrapolation target size.

        Input arguments:
           None

        Return:
            int: Input size of the bubble sort estimate.
        """
        return self.__extrapolation_target_size

    # Method to read the extrapolation base sizes
    def get_extrapolation_base_sizes(self):
        """
        Description:
        - Return the extrapolation base sizes.

        Input arguments:
           None

        Return:
            tuple[int]: Measured sizes used as bases for the estimate.
        """
        return self.__extrapolation_base_sizes

    # Method to make a copy with another dataset path
    def with_csv_path(self, csv_path):
        """
        Description:
        - Return a new Settings object equal to this one except for the dataset path.
        - Used by main.py for the --csv option.

        Input arguments:
           csv_path (str): The new dataset path.

        Return:
            Settings: the copy.
        """
        return Settings(csv_path=csv_path, results_folder=self.__results_folder, selected_columns=self.__selected_columns, scaling_column=self.__scaling_column, sample_seed=self.__sample_seed, shuffle_seed=self.__shuffle_seed, nearly_sorted_seed=self.__nearly_sorted_seed, scaling_sizes=self.__scaling_sizes, order_sample_size=self.__order_sample_size, timed_batches=self.__timed_batches, small_input_limit=self.__small_input_limit, small_input_repetitions=self.__small_input_repetitions, normal_input_repetitions=self.__normal_input_repetitions, extrapolation_target_size=self.__extrapolation_target_size, extrapolation_base_sizes=self.__extrapolation_base_sizes)

    # Method to choose the number of sorts per timed batch
    def repetitions_for(self, input_size):
        """
        Description:
        - Return small_input_repetitions for very small inputs (input_size <= small_input_limit),
        - otherwise normal_input_repetitions.

        Input arguments:
           input_size (int): Number of values to sort, e.g. 5.

        Return:
            int: e.g. 1000 for 5 values, 1 for 250 values.
        """
        raise NotImplementedError("Settings.repetitions_for: not implemented yet")


# The official settings of the project.
DEFAULT_SETTINGS = Settings()
