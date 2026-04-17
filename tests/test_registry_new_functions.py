from factor_engine.registry import canonical_function_name, get_function_spec


def test_alpha101_aliases_resolve_to_existing_function_specs():
    expected = {
        "sum": "ts_sum",
        "stddev": "ts_std",
        "correlation": "corr",
        "covariance": "cov",
        "min": "ts_min",
        "max": "ts_max",
    }

    for alias, canonical in expected.items():
        assert canonical_function_name(alias) == canonical
        alias_spec = get_function_spec(alias)
        canonical_spec = get_function_spec(canonical)

        assert alias_spec is canonical_spec
        assert alias_spec is not None
        assert alias_spec.name == canonical


def test_new_column_functions_are_registered():
    for name in ("ts_min", "ts_max", "delta", "pct_change", "ts_rank"):
        spec = get_function_spec(name)

        assert spec is not None
        assert spec.result_kind == "column"
        assert spec.requires_time_col is True
        assert spec.requires_code_col is True
        assert spec.numeric_arg_positions == (0,)
        assert spec.execution_kind == "time_series"
        assert spec.needs_code_group is True
        assert spec.needs_time_order is True

    assert get_function_spec("delta").window_kind == "none"
    assert get_function_spec("pct_change").window_kind == "none"
    assert get_function_spec("ts_min").window_kind == "rolling"
    assert get_function_spec("ts_max").window_kind == "rolling"
    assert get_function_spec("ts_rank").window_kind == "rolling"


def test_product_is_not_registered_until_clean_vectorized_rolling_support_exists():
    assert get_function_spec("product") is None


def test_new_boolean_time_series_functions_are_registered():
    for name in ("ts_count", "ts_any", "ts_all"):
        spec = get_function_spec(name)

        assert spec is not None
        assert spec.result_kind == "column"
        assert spec.requires_time_col is True
        assert spec.requires_code_col is True
        assert spec.boolean_arg_positions == (0,)
        assert spec.execution_kind == "time_series"
        assert spec.needs_code_group is True
        assert spec.needs_time_order is True
        assert spec.window_kind == "rolling"


def test_segmented_time_series_function_is_registered():
    for name in ("seg_mean", "seg_sum", "seglen_mean", "seglen_sum"):
        spec = get_function_spec(name)

        assert spec is not None
        assert spec.result_kind == "column"
        assert spec.requires_time_col is True
        assert spec.requires_code_col is True
        assert spec.numeric_arg_positions == (0,)
        assert spec.execution_kind == "time_series"
        assert spec.window_kind == "segmented"
        assert spec.needs_code_group is True
        assert spec.needs_time_order is True

    for name in ("seg_count", "seg_any", "seg_all", "seglen_count", "seglen_any", "seglen_all"):
        spec = get_function_spec(name)

        assert spec is not None
        assert spec.result_kind == "column"
        assert spec.requires_time_col is True
        assert spec.requires_code_col is True
        assert spec.boolean_arg_positions == (0,)
        assert spec.execution_kind == "time_series"
        assert spec.window_kind == "segmented"
        assert spec.needs_code_group is True
        assert spec.needs_time_order is True


def test_existing_time_series_specs_are_complete():
    expected_specs = {
        "delay": {"requires_time_col": True, "requires_code_col": True, "numeric_arg_positions": ()},
        "ts_mean": {"requires_time_col": True, "requires_code_col": True, "numeric_arg_positions": (0,)},
        "ts_sum": {"requires_time_col": True, "requires_code_col": True, "numeric_arg_positions": (0,)},
        "ts_std": {"requires_time_col": True, "requires_code_col": True, "numeric_arg_positions": (0,)},
        "corr": {"requires_time_col": True, "requires_code_col": True, "numeric_arg_positions": (0, 1)},
        "cov": {"requires_time_col": True, "requires_code_col": True, "numeric_arg_positions": (0, 1)},
        "skew": {"requires_time_col": True, "requires_code_col": True, "numeric_arg_positions": (0,)},
        "kurt": {"requires_time_col": True, "requires_code_col": True, "numeric_arg_positions": (0,)},
    }

    for name, expected in expected_specs.items():
        spec = get_function_spec(name)

        assert spec is not None
        assert spec.result_kind == "column"
        assert spec.requires_time_col == expected["requires_time_col"]
        assert spec.requires_code_col == expected["requires_code_col"]
        assert spec.numeric_arg_positions == expected["numeric_arg_positions"]
        assert spec.execution_kind == "time_series"
        assert spec.needs_code_group is True
        assert spec.needs_time_order is True


def test_cross_sectional_specs_declare_group_requirements():
    for name in (
        "demean",
        "zscore",
        "rank",
        "scale",
        "group_demean",
        "group_zscore",
        "group_rank",
    ):
        spec = get_function_spec(name)

        assert spec is not None
        assert spec.execution_kind == "cross_sectional"
        assert spec.needs_time_group is True
        assert spec.needs_time_order is False


def test_pointwise_and_table_specs_declare_execution_shape():
    where_spec = get_function_spec("where")
    log_spec = get_function_spec("log")
    signedpower_spec = get_function_spec("signedpower")
    fft_spec = get_function_spec("fft")

    assert where_spec is not None
    assert where_spec.execution_kind == "pointwise"
    assert where_spec.needs_code_group is False
    assert where_spec.needs_time_group is False
    assert where_spec.needs_time_order is False

    assert log_spec is not None
    assert log_spec.execution_kind == "pointwise"
    assert log_spec.numeric_arg_positions == (0,)

    assert signedpower_spec is not None
    assert signedpower_spec.execution_kind == "pointwise"
    assert signedpower_spec.numeric_arg_positions == (0, 1)

    assert fft_spec is not None
    assert fft_spec.execution_kind == "table"
    assert fft_spec.needs_code_group is True
    assert fft_spec.needs_time_order is True
