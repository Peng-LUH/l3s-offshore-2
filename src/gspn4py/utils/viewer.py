import io
import matplotlib
matplotlib.use("Agg")  # headless servers
import matplotlib.pyplot as plt

from matplotlib.dates import AutoDateLocator, ConciseDateFormatter, date2num
from matplotlib.patches import Patch
from datetime import datetime
import numpy as np
from typing import Dict, List, Tuple, Union, Iterable, Optional

def _is_sentinel_empty(lst):
    return isinstance(lst, list) and len(lst) == 1 and lst[0] == -1

def _to_num(x):
    if not isinstance(x, Iterable) or isinstance(x, (str, bytes)):
        x = [x]
    x = list(x)
    if not x:
        return np.array([]), False
    sample = x[0]
    is_dt = isinstance(sample, (datetime, np.datetime64))
    if is_dt:
        x_dt = []
        for v in x:
            if isinstance(v, np.datetime64):
                ts = (v - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
                x_dt.append(datetime.utcfromtimestamp(float(ts)))
            else:
                x_dt.append(v)
        return np.array([date2num(v) for v in x_dt]), True
    return np.asarray(x, dtype=float), False

def _flatten_planned(planned: Dict):
    starts_ll = planned.get("planned_operationsStart", [])
    ends_ll   = planned.get("planned_operationsEnd", [])
    ids_ll    = planned.get("planned_operationsId", [])
    if not (isinstance(starts_ll, list) and isinstance(ends_ll, list) and isinstance(ids_ll, list)):
        raise ValueError("planned_* must be lists of lists (or [-1]).")
    if not (len(starts_ll) == len(ends_ll) == len(ids_ll)):
        raise ValueError("planned_operationsStart/End/Id must have the same outer length.")
    starts, ends, ids = [], [], []
    for s_list, e_list, i_list in zip(starts_ll, ends_ll, ids_ll):
        if _is_sentinel_empty(s_list) and _is_sentinel_empty(e_list) and _is_sentinel_empty(i_list):
            continue
        if not (len(s_list) == len(e_list) == len(i_list)):
            raise ValueError("Mismatched lengths inside planned_* sublists.")
        starts.extend(s_list); ends.extend(e_list); ids.extend(i_list)
    return starts, ends, ids

def make_schedule_figure(
    planned: Dict,
    mapping_operationId: Optional[Dict[str, int]] = None,
    title: str = "Operation Schedule",
    xlabel: str = "Time",
    show_restock: bool = True,
    figsize=(11, 4.8),
):
    op_start, op_stop, op_id = _flatten_planned(planned)
    if not op_start:
        raise ValueError("No intervals to plot (all lists were [-1]).")

    unique_ids = sorted(set(op_id))
    id_to_name = {i: f"Op {i}" for i in unique_ids}
    if mapping_operationId:
        for name, i in mapping_operationId.items():
            if i in unique_ids:
                id_to_name[i] = name

    cycle_colors = plt.rcParams['axes.prop_cycle'].by_key().get('color', [])
    id_to_color = {i: (cycle_colors[idx % len(cycle_colors)] if cycle_colors else None)
                   for idx, i in enumerate(unique_ids)}

    # group intervals per ID
    intervals_by_id = {i: [] for i in unique_ids}
    for s, e, i in zip(op_start, op_stop, op_id):
        if e < s:
            raise ValueError("Found interval with stop < start.")
        intervals_by_id[i].append((s, e))

    fig, ax = plt.subplots(figsize=figsize)
    ids_sorted = unique_ids
    y_positions = np.arange(len(ids_sorted))
    height = 0.8
    is_datetime = False

    for row, i in enumerate(ids_sorted):
        intervals = intervals_by_id[i]
        if not intervals:
            continue
        starts = [s for s, _ in intervals]
        stops  = [e for _, e in intervals]
        starts_num, dt_a = _to_num(starts)
        stops_num, dt_b  = _to_num(stops)
        is_datetime = is_datetime or dt_a or dt_b
        spans = [(float(s), float(e - s)) for s, e in zip(starts_num, stops_num)]
        ax.broken_barh(spans, (y_positions[row] - height/2, height),
                       facecolors=id_to_color[i])

    # optional restock markers
    if show_restock and "planned_restockOperations" in planned:
        restock = planned["planned_restockOperations"]
        if not _is_sentinel_empty(restock):
            if restock and isinstance(restock[0], list):
                restock_times = [t for sub in restock if not _is_sentinel_empty(sub) for t in sub]
            else:
                restock_times = restock
            times_num, dt_r = _to_num(restock_times)
            is_datetime = is_datetime or dt_r
            for t in times_num:
                ax.axvline(float(t), linestyle="--", linewidth=1)

    ax.set_yticks(y_positions, [id_to_name[i] for i in ids_sorted])
    if is_datetime:
        locator = AutoDateLocator()
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(ConciseDateFormatter(locator))
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(True, axis='x', linestyle=':', linewidth=0.8)

    # legend
    handles = [Patch(facecolor=(id_to_color[i] if id_to_color[i] else "C0"),
                     label=id_to_name[i]) for i in ids_sorted]
    if handles:
        ax.legend(handles=handles, title="Operations", loc="upper right")

    fig.tight_layout()
    return fig