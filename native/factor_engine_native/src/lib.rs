use std::collections::VecDeque;
use std::time::Instant;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use rayon::prelude::*;

mod rolling_moments;

#[derive(Clone, Copy)]
enum ExtremeMode {
    ArgMax,
    ArgMin,
}

impl ExtremeMode {
    fn parse(raw: &str) -> PyResult<Self> {
        match raw {
            "argmax" => Ok(Self::ArgMax),
            "argmin" => Ok(Self::ArgMin),
            other => Err(PyValueError::new_err(format!(
                "mode must be 'argmax' or 'argmin', got {other}"
            ))),
        }
    }

    fn should_drop_tail(self, current: f64, tail: f64) -> bool {
        match self {
            // Equal values drop the older candidate so nearest tie wins.
            Self::ArgMax => current >= tail,
            Self::ArgMin => current <= tail,
        }
    }
}

fn py_value_error(message: impl Into<String>) -> PyErr {
    PyValueError::new_err(message.into())
}

fn grouped_distance_scan(
    values: &[Option<f64>],
    group_lengths: &[usize],
    window: usize,
    mode: ExtremeMode,
) -> PyResult<Vec<Option<i64>>> {
    if window == 0 {
        return Err(py_value_error("window must be positive"));
    }

    let row_count = values.len();
    let planned_rows: usize = group_lengths.iter().sum();
    if planned_rows != row_count {
        return Err(py_value_error(format!(
            "group_lengths sum ({planned_rows}) must match value length ({row_count})"
        )));
    }

    let mut output = vec![None; row_count];
    let mut group_start = 0usize;

    for &group_len in group_lengths {
        let group_end = group_start + group_len;
        let mut candidates: VecDeque<usize> = VecDeque::new();

        for index in group_start..group_end {
            let first_valid_index = index.saturating_sub(window - 1);
            while candidates
                .front()
                .is_some_and(|front| *front < first_valid_index)
            {
                candidates.pop_front();
            }

            if let Some(current_value) = values[index] {
                while let Some(&tail_index) = candidates.back() {
                    let Some(tail_value) = values[tail_index] else {
                        candidates.pop_back();
                        continue;
                    };
                    if !mode.should_drop_tail(current_value, tail_value) {
                        break;
                    }
                    candidates.pop_back();
                }
                candidates.push_back(index);
            }

            output[index] = candidates
                .front()
                .map(|best_index| (index - *best_index) as i64);
        }

        group_start = group_end;
    }

    Ok(output)
}

fn bit_is_set(bytes: &[u8], index: usize) -> bool {
    let byte = bytes[index / 8];
    ((byte >> (index % 8)) & 1) == 1
}

fn set_bit(bytes: &mut [u8], index: usize) {
    bytes[index / 8] |= 1 << (index % 8);
}

fn scan_group_f64(
    values: &[f64],
    validity: Option<&[u8]>,
    validity_offset: usize,
    start: usize,
    end: usize,
    window: usize,
    mode: ExtremeMode,
) -> (usize, Vec<i64>, Vec<bool>) {
    let mut data = vec![0_i64; end - start];
    let mut valid = vec![false; end - start];
    let mut candidates: VecDeque<usize> = VecDeque::new();

    for index in start..end {
        let first_valid_index = index.saturating_sub(window - 1);
        while candidates
            .front()
            .is_some_and(|front| *front < first_valid_index)
        {
            candidates.pop_front();
        }

        let is_valid = validity
            .map(|bitmap| bit_is_set(bitmap, validity_offset + index))
            .unwrap_or(true);
        if is_valid {
            let current_value = values[index];
            while let Some(&tail_index) = candidates.back() {
                let tail_valid = validity
                    .map(|bitmap| bit_is_set(bitmap, validity_offset + tail_index))
                    .unwrap_or(true);
                if !tail_valid {
                    candidates.pop_back();
                    continue;
                }
                let tail_value = values[tail_index];
                if !mode.should_drop_tail(current_value, tail_value) {
                    break;
                }
                candidates.pop_back();
            }
            candidates.push_back(index);
        }

        if let Some(best_index) = candidates.front() {
            let local_index = index - start;
            data[local_index] = (index - *best_index) as i64;
            valid[local_index] = true;
        }
    }

    (start, data, valid)
}

fn grouped_distance_scan_f64_buffers(
    values: &[f64],
    validity: Option<&[u8]>,
    validity_offset: usize,
    group_lengths: &[usize],
    window: usize,
    mode: ExtremeMode,
    parallel: bool,
) -> PyResult<(Vec<i64>, Vec<u8>)> {
    if window == 0 {
        return Err(py_value_error("window must be positive"));
    }

    let row_count = values.len();
    let planned_rows: usize = group_lengths.iter().sum();
    if planned_rows != row_count {
        return Err(py_value_error(format!(
            "group_lengths sum ({planned_rows}) must match value length ({row_count})"
        )));
    }

    let mut starts = Vec::with_capacity(group_lengths.len());
    let mut group_start = 0usize;
    for &group_len in group_lengths {
        starts.push((group_start, group_start + group_len));
        group_start += group_len;
    }

    let groups: Vec<(usize, Vec<i64>, Vec<bool>)> = if parallel {
        starts
            .par_iter()
            .map(|(start, end)| {
                scan_group_f64(
                    values,
                    validity,
                    validity_offset,
                    *start,
                    *end,
                    window,
                    mode,
                )
            })
            .collect()
    } else {
        starts
            .iter()
            .map(|(start, end)| {
                scan_group_f64(
                    values,
                    validity,
                    validity_offset,
                    *start,
                    *end,
                    window,
                    mode,
                )
            })
            .collect()
    };

    let mut output = vec![0_i64; row_count];
    let mut output_validity = vec![0_u8; row_count.div_ceil(8)];
    for (start, group_data, group_valid) in groups {
        let end = start + group_data.len();
        output[start..end].copy_from_slice(&group_data);
        for (offset, is_valid) in group_valid.into_iter().enumerate() {
            if is_valid {
                set_bit(&mut output_validity, start + offset);
            }
        }
    }

    Ok((output, output_validity))
}

fn grouped_argmax_distance(
    values: &[Option<f64>],
    group_lengths: &[usize],
    window: usize,
) -> PyResult<Vec<Option<i64>>> {
    grouped_distance_scan(values, group_lengths, window, ExtremeMode::ArgMax)
}

fn grouped_argmin_distance(
    values: &[Option<f64>],
    group_lengths: &[usize],
    window: usize,
) -> PyResult<Vec<Option<i64>>> {
    grouped_distance_scan(values, group_lengths, window, ExtremeMode::ArgMin)
}

#[pyfunction]
fn grouped_positional_extreme(
    py: Python<'_>,
    value_series: &Bound<'_, PyAny>,
    group_lengths: Vec<usize>,
    window: usize,
    mode: &str,
) -> PyResult<(Vec<Option<i64>>, f64, f64)> {
    let mode = ExtremeMode::parse(mode)?;
    let ingest_started = Instant::now();
    let values = value_series
        .call_method0("to_list")?
        .extract::<Vec<Option<f64>>>()?;
    let ingest_ms = ingest_started.elapsed().as_secs_f64() * 1000.0;

    // The scan itself is CPU-heavy and does not touch Python objects, so release
    // the GIL while running the first native implementation.
    let scan_started = Instant::now();
    let output = py.detach(move || match mode {
        ExtremeMode::ArgMax => grouped_argmax_distance(&values, &group_lengths, window),
        ExtremeMode::ArgMin => grouped_argmin_distance(&values, &group_lengths, window),
    })?;
    let scan_ms = scan_started.elapsed().as_secs_f64() * 1000.0;
    Ok((output, ingest_ms, scan_ms))
}

#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn grouped_positional_extreme_buffers<'py>(
    py: Python<'py>,
    values_ptr: usize,
    values_offset: usize,
    len: usize,
    validity_ptr: usize,
    validity_offset: usize,
    group_lengths: Vec<usize>,
    window: usize,
    mode: &str,
    parallel: bool,
) -> PyResult<(Bound<'py, PyBytes>, Bound<'py, PyBytes>, f64, f64)> {
    let mode = ExtremeMode::parse(mode)?;
    let values = unsafe { std::slice::from_raw_parts((values_ptr as *const f64).add(values_offset), len) };
    let validity_bytes_len = if validity_ptr == 0 {
        0
    } else {
        (validity_offset + len).div_ceil(8)
    };
    let validity = if validity_ptr == 0 {
        None
    } else {
        Some(unsafe { std::slice::from_raw_parts(validity_ptr as *const u8, validity_bytes_len) })
    };

    let scan_started = Instant::now();
    let (output, output_validity) = py.detach(move || {
        grouped_distance_scan_f64_buffers(
            values,
            validity,
            validity_offset,
            &group_lengths,
            window,
            mode,
            parallel,
        )
    })?;
    let scan_ms = scan_started.elapsed().as_secs_f64() * 1000.0;

    let output_bytes = unsafe {
        std::slice::from_raw_parts(output.as_ptr() as *const u8, output.len() * std::mem::size_of::<i64>())
    };
    let data = PyBytes::new(py, output_bytes);
    let validity = PyBytes::new(py, &output_validity);
    Ok((data, validity, 0.0, scan_ms))
}

#[pymodule]
fn factor_engine_native(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(grouped_positional_extreme, module)?)?;
    module.add_function(wrap_pyfunction!(grouped_positional_extreme_buffers, module)?)?;
    module.add_function(wrap_pyfunction!(rolling_moments::grouped_corr_cov, module)?)?;
    Ok(())
}
