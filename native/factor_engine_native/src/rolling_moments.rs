use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use rayon::prelude::*;
use std::collections::VecDeque;
use std::time::Instant;

#[derive(Clone, Copy)]
enum MomentMode {
    Corr,
    Cov,
}

impl MomentMode {
    fn parse(raw: &str) -> PyResult<Self> {
        match raw {
            "corr" => Ok(Self::Corr),
            "cov" => Ok(Self::Cov),
            other => Err(PyValueError::new_err(format!(
                "mode must be 'corr' or 'cov', got {other}"
            ))),
        }
    }
}

#[derive(Clone, Copy)]
struct Pair {
    x: f64,
    y: f64,
}

#[derive(Default)]
struct MomentState {
    count: usize,
    sum_x: f64,
    sum_y: f64,
    sum_x2: f64,
    sum_y2: f64,
    sum_xy: f64,
}

impl MomentState {
    fn push(&mut self, pair: Pair) {
        self.count += 1;
        self.sum_x += pair.x;
        self.sum_y += pair.y;
        self.sum_x2 += pair.x * pair.x;
        self.sum_y2 += pair.y * pair.y;
        self.sum_xy += pair.x * pair.y;
    }

    fn pop(&mut self, pair: Pair) {
        self.count -= 1;
        self.sum_x -= pair.x;
        self.sum_y -= pair.y;
        self.sum_x2 -= pair.x * pair.x;
        self.sum_y2 -= pair.y * pair.y;
        self.sum_xy -= pair.x * pair.y;
    }

    fn covariance(&self) -> f64 {
        let count = self.count as f64;
        (self.sum_xy - (self.sum_x * self.sum_y / count)) / (count - 1.0)
    }

    fn value(&self, mode: MomentMode) -> Option<f64> {
        if self.count < 2 {
            return None;
        }
        let covariance = self.covariance();
        match mode {
            MomentMode::Cov => Some(covariance),
            MomentMode::Corr => {
                let count = self.count as f64;
                let var_x = (self.sum_x2 - (self.sum_x * self.sum_x / count)) / (count - 1.0);
                let var_y = (self.sum_y2 - (self.sum_y * self.sum_y / count)) / (count - 1.0);
                Some(covariance / (var_x * var_y).sqrt())
            }
        }
    }
}

fn scan_group(
    x_values: &[Option<f64>],
    y_values: &[Option<f64>],
    start: usize,
    end: usize,
    window: usize,
    mode: MomentMode,
) -> (usize, Vec<Option<f64>>, usize) {
    let mut state = MomentState::default();
    let mut queue: VecDeque<(usize, Pair)> = VecDeque::new();
    let mut output = vec![None; end - start];
    let mut pair_count = 0usize;

    for index in start..end {
        let first_valid_index = index.saturating_sub(window - 1);
        while queue.front().is_some_and(|(pair_index, _)| *pair_index < first_valid_index) {
            if let Some((_, pair)) = queue.pop_front() {
                state.pop(pair);
            }
        }

        if let (Some(x), Some(y)) = (x_values[index], y_values[index]) {
            let pair = Pair { x, y };
            state.push(pair);
            queue.push_back((index, pair));
            pair_count += 1;
        }

        output[index - start] = state.value(mode);
    }

    (start, output, pair_count)
}

pub fn grouped_corr_cov_scan(
    x_values: &[Option<f64>],
    y_values: &[Option<f64>],
    group_lengths: &[usize],
    window: usize,
    mode: &str,
    parallel: bool,
) -> PyResult<(Vec<Option<f64>>, usize)> {
    if window < 2 {
        return Err(PyValueError::new_err("window must be >= 2"));
    }
    if x_values.len() != y_values.len() {
        return Err(PyValueError::new_err("x and y lengths must match"));
    }
    let planned_rows: usize = group_lengths.iter().sum();
    if planned_rows != x_values.len() {
        return Err(PyValueError::new_err(format!(
            "group_lengths sum ({planned_rows}) must match value length ({})",
            x_values.len()
        )));
    }

    let mode = MomentMode::parse(mode)?;
    let mut starts = Vec::with_capacity(group_lengths.len());
    let mut group_start = 0usize;
    for &group_len in group_lengths {
        starts.push((group_start, group_start + group_len));
        group_start += group_len;
    }

    let groups: Vec<(usize, Vec<Option<f64>>, usize)> = if parallel {
        starts
            .par_iter()
            .map(|(start, end)| scan_group(x_values, y_values, *start, *end, window, mode))
            .collect()
    } else {
        starts
            .iter()
            .map(|(start, end)| scan_group(x_values, y_values, *start, *end, window, mode))
            .collect()
    };

    let mut output = vec![None; x_values.len()];
    let mut pair_count = 0usize;
    for (start, values, group_pair_count) in groups {
        let end = start + values.len();
        output[start..end].copy_from_slice(&values);
        pair_count += group_pair_count;
    }
    Ok((output, pair_count))
}

#[pyfunction]
pub fn grouped_corr_cov(
    py: Python<'_>,
    x_values: Vec<Option<f64>>,
    y_values: Vec<Option<f64>>,
    group_lengths: Vec<usize>,
    window: usize,
    mode: &str,
    parallel: bool,
) -> PyResult<(Vec<Option<f64>>, usize, f64)> {
    let mode = mode.to_string();
    let scan_started = Instant::now();
    let (output, pair_count) = py.detach(move || {
        grouped_corr_cov_scan(
            &x_values,
            &y_values,
            &group_lengths,
            window,
            &mode,
            parallel,
        )
    })?;
    let scan_ms = scan_started.elapsed().as_secs_f64() * 1000.0;
    Ok((output, pair_count, scan_ms))
}
