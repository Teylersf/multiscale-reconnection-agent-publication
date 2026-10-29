"""v1.2 diagnostics: execute the complete pinned routine and paired resampling.

No downloads. Supply the external cache of the 32 verified public NPY files.
The old v1.1 outputs are read only. Resampling ranges are conditional iid
empirical diagnostics, not population confidence intervals or significance tests.
"""
from pathlib import Path
import argparse
import ast
import contextlib
import csv
import gc
import hashlib
import io
import json
import math
import sys
import time

import numpy as np

if not __debug__:
    raise RuntimeError('Python -O is forbidden: integrity checks must remain enabled.')
ROOT = Path(__file__).resolve().parents[1]
SCRIPT_BYTES = Path(__file__).read_bytes()
SOURCE_SHA = '2909f9e6acec3c48f3838e86c15ffd18a9563dc57984e400b0baadd22f16655f'
BATCHES = ('inter_energy', 'high_energy')
METHODS = ('left', 'symmetric', 'right')
OUTPUTS = ('full-source-validation-v1.2.0.json',
           'paired-history-bootstrap-v1.2.0.json',
           'paired-history-bootstrap-v1.2.0.npz',
           'paired-history-bootstrap-ranges-v1.2.0.csv')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(8*1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def receipt(relative):
    p = ROOT/relative
    return {'path': relative, 'bytes': p.stat().st_size, 'sha256': sha(p)}


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n').encode('utf-8')


def peak_resident_memory():
    """Optional execution metadata; no effect on numerical calculations."""
    try:
        if sys.platform == 'win32':
            import ctypes
            from ctypes import wintypes
            class Counters(ctypes.Structure):
                _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD),
                            *[(name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize',
                              'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
                              'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]]
            counters = Counters(); counters.cb = ctypes.sizeof(counters)
            kernel = ctypes.windll.kernel32; kernel.GetCurrentProcess.restype = wintypes.HANDLE
            fn = ctypes.windll.psapi.GetProcessMemoryInfo
            fn.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
            if not fn(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
                return None
            return {'bytes': int(counters.PeakWorkingSetSize), 'measure': 'Windows process peak working set'}
        import resource
        n = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return {'bytes': int(n if sys.platform == 'darwin' else n*1024), 'measure': 'Process ru_maxrss'}
    except (ImportError, AttributeError, OSError, ValueError):
        return None


def load_compact():
    p = ROOT/'results/public-batch-per-particle.npz'
    with np.load(p, allow_pickle=False) as f:
        keys = [k.split('__', 1)[1] for k in f.files if k.startswith(BATCHES[0]+'__')]
        data = {k: np.concatenate([f[b+'__'+k] for b in BATCHES], axis=0) for k in keys}
        sizes = {b: len(f[b+'__tag']) for b in BATCHES}
    assert len(data['tag']) == len(np.unique(data['tag'])) == 1003
    assert np.array_equal(data['total_net_gain'], data['final_gamma'].astype(float)-data['initial_gamma'].astype(float))
    return data, sizes


def assemble_raw(cache, manifest, compact, sizes):
    entries = manifest['files']
    assert len(entries) == 32 and len({e['id'] for e in entries}) == 32
    assert len({e['local_relative_path'] for e in entries}) == 32
    assert sum(e['size'] for e in entries) == 3107362288
    # The actual common sample count is checked against every input header.
    ns, total = 40764, sum(sizes.values())
    gamma = np.empty((ns, total), dtype=np.float32)
    region = np.empty((ns, total), dtype=np.uint8)
    assert gamma.nbytes+region.nbytes < 500000000
    verified = []; column = 0
    for batch in BATCHES:
        n = sizes[batch]; offset = 0
        selected = [e for e in entries if e['released_batch'] == batch]
        assert len(selected) == 16
        assert {(e['kind'], e['time_batch']) for e in selected} == {(k, t) for k in ('tracer', 'region') for t in range(8)}
        expected_tags = compact['tag'][column:column+n]
        for chunk in range(8):
            pair = {e['kind']: e for e in selected if e['time_batch'] == chunk}
            maps = {}; stats = {}; verification_rows = {}
            try:
                for kind, e in pair.items():
                    p = (cache/e['local_relative_path']).resolve()
                    assert p.is_relative_to(cache.resolve())
                    stat = p.stat(); stats[kind] = (stat.st_size, stat.st_mtime_ns)
                    assert stat.st_size == e['size'] and sha(p) == e['sha256']
                    maps[kind] = np.load(p, mmap_mode='r', allow_pickle=False)
                    verified.append({'id': e['id'], 'relative_path': e['local_relative_path'],
                                     'bytes': e['size'], 'sha256': e['sha256'],
                                     'hash_verified_before_read': True})
                    verification_rows[kind] = verified[-1]
                t, r = maps['tracer'], maps['region']
                assert t.dtype == np.float32 and r.dtype == np.float64
                assert t.ndim == 3 and t.shape[0] == 17 and t.shape[1:] == r.shape
                assert r.ndim == 2 and r.shape[1] == n and offset+len(r) <= ns
                for lo in range(0, len(r), 256):
                    hi = min(lo+256, len(r))
                    g = t[0, lo:hi]; rr = r[lo:hi]; tags = t[3, lo:hi]
                    assert np.isfinite(g).all() and np.isfinite(rr).all() and np.isfinite(tags).all()
                    assert np.array_equal(rr, np.rint(rr)) and np.isin(rr, [1, 2, 3, 4, 5]).all()
                    assert np.array_equal(tags, np.broadcast_to(expected_tags, tags.shape))
                    gamma[offset+lo:offset+hi, column:column+n] = g
                    region[offset+lo:offset+hi, column:column+n] = rr.astype(np.uint8)
                offset += len(r)
                for kind, e in pair.items():
                    p = cache/e['local_relative_path']; st = p.stat()
                    assert (st.st_size, st.st_mtime_ns) == stats[kind]
                    verification_rows[kind]['metadata_unchanged_after_read'] = True
            finally:
                for mmap in maps.values():
                    mmap._mmap.close()
        assert offset == ns
        column += n
    assert np.array_equal(gamma[0], compact['initial_gamma'])
    assert np.array_equal(gamma[-1], compact['final_gamma'])
    return gamma, region, verified


def execute_source(gamma, region, compact):
    source = ROOT/'data/upstream-cc0/first_passage_function.py'
    assert sha(source) == SOURCE_SHA
    tree = ast.parse(source.read_text(encoding='utf-8'))
    assert len(tree.body) == 1 and isinstance(tree.body[0], ast.FunctionDef)
    namespace = {'np': np, 'tqdm': lambda sequence, **kw: sequence}
    exec(compile(tree, 'pinned-upstream-first-passage-function', 'exec'), namespace)
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        result = namespace['get_energy_by_region_w_bands'](gamma, region, 5.77, 16.40)
    bands = {}
    masks = {'intermediate': (gamma[-1] > 5.77) & (gamma[-1] < 16.40),
             'high': gamma[-1] > 16.40}
    for band, start, index_slot in (('intermediate', 0, 6), ('high', 3, 7)):
        indices = np.flatnonzero(masks[band])
        assert np.array_equal(result[index_slot], indices)
        expected = compact['first_passage'][indices]
        checks = []
        for j, label in enumerate(('CS', 'DS', 'phase_residual')):
            actual = result[start+j]
            assert np.array_equal(actual, expected[:, j])
            checks.append({'channel': label, 'returned_dtype': actual.dtype.str,
                           'mismatching_values': 0, 'maximum_absolute_difference': 0.0})
        a = compact['total_net_gain'][indices]
        native_total = expected.sum(axis=1)
        common_mean = math.fsum(map(float, expected[:, 1]/a))/len(indices)
        native_mean = math.fsum(map(float, expected[:, 1]/native_total))/len(indices)
        bands[band] = {'selected_histories': len(indices), 'source_indices_exact': True,
                       'all_three_returned_arrays_exact': True, 'channels': checks,
                       'common_endpoint_A_mean_DS_fraction': common_mean,
                       'source_native_sum_denominator_mean_DS_fraction': native_mean,
                       'native_minus_common_mean_fraction': native_mean-common_mean,
                       'maximum_native_phase_sum_minus_A': float(np.max(np.abs(native_total-a)))}
    assert bands['intermediate']['selected_histories'] == 667 and bands['high']['selected_histories'] == 84
    return {'input_histories': gamma.shape[1], 'input_samples_per_history': gamma.shape[0],
            'gamma_dtype': gamma.dtype.str, 'region_dtype': region.dtype.str,
            'region_uint8_conversion_exact': True,
            'assembled_payload_bytes': gamma.nbytes+region.nbytes,
            'source_function_executed_once_on_all_1003_inputs': True,
            'selected_output_histories': 751, 'excluded_by_original_strict_cuts': 252,
            'function_stdout_suppressed_lines': len(printed.getvalue().splitlines()), 'bands': bands}


def paired_replicates(a, difference, replicates, seed, band_index, block):
    assert a.ndim == 1 and difference.shape == (len(a), 3)
    assert np.isfinite(a).all() and np.isfinite(difference).all() and (a > 0).all()
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(seed, spawn_key=(band_index,))))
    mean = np.empty((replicates, 3)); energy = np.empty_like(mean)
    ratio_difference = difference/a[:, None]
    for lo in range(0, replicates, block):
        hi = min(lo+block, replicates)
        ids = rng.integers(0, len(a), size=(hi-lo, len(a)), dtype=np.int64)
        # One shared history-index draw is used for all methods, both estimands
        # and their FP comparator. No independent numerator/denominator draws.
        mean[lo:hi] = ratio_difference[ids].mean(axis=1)
        energy[lo:hi] = difference[ids].sum(axis=1)/a[ids].sum(axis=1)[:, None]
    return mean, energy


def bootstrap_self_check():
    a = np.array([1., 2., 3., 4., 5., 6., 7.])
    d = np.column_stack((-.13*a, .2*a, .4*a))
    x, y = paired_replicates(a, d, 503, 1937, 0, 17)
    assert np.allclose(x, [-.13, .2, .4], atol=1e-14, rtol=0)
    assert np.allclose(y, [-.13, .2, .4], atol=1e-14, rtol=0)
    # Signed heterogeneous gains and block-size invariance, with a scalar
    # reference using the same seeded indices but separate arithmetic.
    d = np.column_stack(([-1., 4., -6., 3., -2., 1., 2.], a*.2, a*-.1))
    x, y = paired_replicates(a, d, 503, 1937, 1, 17)
    xx, yy = paired_replicates(a, d, 503, 1937, 1, 31)
    assert np.array_equal(x, xx) and np.array_equal(y, yy)
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(1937, spawn_key=(1,))))
    for k in range(503):
        ids = rng.integers(0, len(a), size=len(a), dtype=np.int64)
        for j in range(3):
            expected_mean = math.fsum(float(d[i, j]/a[i]) for i in ids)/len(a)
            expected_energy = math.fsum(float(d[i, j]) for i in ids)/math.fsum(float(a[i]) for i in ids)
            assert math.isclose(x[k, j], expected_mean, rel_tol=1e-13, abs_tol=1e-14)
            assert math.isclose(y[k, j], expected_energy, rel_tol=1e-13, abs_tol=1e-14)
    return {'status': 'pass', 'paired_constant_shift_control': True,
            'signed_scalar_reference': True, 'block_size_invariance': True}


def bootstrap(compact, replicates, seed, block):
    out = {}; arrays = {}; rows = []
    masks = {'intermediate': (compact['final_gamma'] > 5.77) & (compact['final_gamma'] < 16.40),
             'high': compact['final_gamma'] > 16.40}
    for band_index, (band, mask) in enumerate(masks.items()):
        a = compact['total_net_gain'][mask]
        difference = np.column_stack([compact[m][mask, 3]-compact['first_passage'][mask, 1] for m in METHODS])
        mean, energy = paired_replicates(a, difference, replicates, seed, band_index, block)
        arrays[band+'__mean_fraction_change'] = mean
        arrays[band+'__total_net_gain_share_change'] = energy
        arrays[band+'__selected_tags'] = compact['tag'][mask]
        methods = {}
        for j, method in enumerate(METHODS):
            values = {}
            for estimand, draws in (('mean_particle_fraction_change', mean[:, j]),
                                    ('total_net_gain_share_change', energy[:, j])):
                point = (math.fsum(map(float, difference[:, j]/a))/len(a)
                         if estimand.startswith('mean') else math.fsum(map(float, difference[:, j]))/math.fsum(map(float, a)))
                q = np.quantile(draws, [.025, .5, .975], method='linear')
                values[estimand] = {'point_fraction': point, 'point_percentage_points': 100*point,
                    'conditional_empirical_percentile_probabilities': [.025, .5, .975],
                    'conditional_empirical_percentile_fractions': q.tolist(),
                    'conditional_empirical_percentile_percentage_points': (100*q).tolist(),
                    'bootstrap_replicate_standard_deviation_fraction': float(draws.std(ddof=1))}
                rows.append([band, len(a), method, estimand, replicates, 100*point, *(100*q).tolist()])
            methods[method] = values
        out[band] = {'histories': len(a), 'zero_or_negative_A': int(np.sum(a <= 0)),
                     'seed_sequence_spawn_key': [band_index], 'methods': methods}
    return out, arrays, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cohort-dir', type=Path)
    parser.add_argument('--output-dir', type=Path, default=ROOT/'results')
    parser.add_argument('--replicates', type=int, default=20000)
    parser.add_argument('--seed', type=int, default=20261029)
    parser.add_argument('--bootstrap-block', type=int, default=256)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--replace-v1-2-outputs', action='store_true')
    args = parser.parse_args()
    assert args.replicates >= 2 and args.bootstrap_block > 0 and args.seed >= 0
    checks = bootstrap_self_check()
    if args.self_test and args.cohort_dir is None:
        print(json.dumps(checks)); return
    if args.cohort_dir is None:
        parser.error('--cohort-dir is required; no download is performed')
    output = args.output_dir.resolve(); output.mkdir(parents=True, exist_ok=True)
    if any((output/n).exists() for n in OUTPUTS) and not args.replace_v1_2_outputs:
        raise FileExistsError('New v1.2 outputs already exist; preserve them or explicitly choose replacement')
    inputs = [receipt(n) for n in ('data/upstream-cc0/released-cohort-inventory.json',
              'data/upstream-cc0/first_passage_function.py', 'results/public-batch-per-particle.npz',
              'results/public-batch-checks.json', 'results/public-batch-independent-verification.json')]
    manifest = json.loads((ROOT/inputs[0]['path']).read_text(encoding='utf-8'))
    compact, sizes = load_compact()
    start = time.perf_counter()
    gamma, region, raw_receipts = assemble_raw(args.cohort_dir, manifest, compact, sizes)
    validation = execute_source(gamma, region, compact)
    validation['observed_process_peak_resident_memory'] = peak_resident_memory()
    del gamma, region; gc.collect()
    bands, arrays, rows = bootstrap(compact, args.replicates, args.seed, args.bootstrap_block)
    assert Path(__file__).read_bytes() == SCRIPT_BYTES
    assert all(sha(ROOT/x['path']) == x['sha256'] for x in inputs)
    common = {'schema_version': 1, 'script': {'path': 'experiments/validate_full_source_and_bootstrap.py',
               'sha256': hashlib.sha256(SCRIPT_BYTES).hexdigest()}, 'numpy_version': np.__version__, 'inputs': inputs}
    full = {**common, 'status': 'pass', 'source_excerpt_sha256': SOURCE_SHA,
            'execution': validation, 'raw_input_bindings': raw_receipts,
            'time_scope': 'Filename t00–t07 order follows the posted loader; physical timestamp continuity is not independently established.',
            'no_original_module_top_level_IO': True, 'raw_downloads_performed': 0}
    boot = {**common, 'status': 'pass', 'replicates': args.replicates, 'seed': args.seed,
            'bit_generator': 'PCG64', 'bootstrap_block': args.bootstrap_block,
            'quantile_method': 'NumPy linear', 'self_checks': checks,
            'resampling_unit': 'One complete selected particle history; iid sampling with replacement from each band empirical distribution, same resampled IDs for every convention and estimand.',
            'difference_direction': 'Full-history convention minus first-passage, using common fixed A=gamma_final−gamma_initial; no clipping of signed regional gains.',
            'interpretation': 'Central 95% conditional iid empirical bootstrap percentile ranges, NOT population confidence intervals, physical uncertainty bounds or significance tests.',
            'limitations': ['Release probabilities are unknown, so no correction for archive selection is supplied.',
              'Particles share one simulation and can be correlated; iid history resampling can understate uncertainty.',
              'No independent-run or structure-cluster replication is available; no population-wide significance is inferred.',
              'Temporal/mask cadence, hidden recrossings and continuous electric work are not validated by these ranges.'],
            'bands': bands, 'runtime_seconds': time.perf_counter()-start}
    npz = output/OUTPUTS[2]; np.savez_compressed(npz, **arrays)
    table = output/OUTPUTS[3]
    with table.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['band','histories','method','estimand','replicates',
            'point_percentage_points','conditional_p2_5_percentage_points',
            'conditional_p50_percentage_points','conditional_p97_5_percentage_points']); w.writerows(rows)
    boot['replicate_output'] = {'filename': npz.name, 'bytes': npz.stat().st_size, 'sha256': sha(npz),
        'arrays': {k: {'shape': list(v.shape), 'dtype': v.dtype.str} for k, v in arrays.items()}}
    boot['range_table_output'] = {'filename': table.name, 'bytes': table.stat().st_size, 'sha256': sha(table)}
    for name, obj in ((OUTPUTS[0], full), (OUTPUTS[1], boot)):
        (output/name).write_bytes(json_bytes(obj))
    print(json.dumps({'status': 'pass', 'full_source_selected': validation['selected_output_histories'],
                      'assembled_payload_bytes': validation['assembled_payload_bytes'], 'replicates': args.replicates,
                      'outputs': [{'filename': n, 'sha256': sha(output/n)} for n in OUTPUTS]}, indent=2))


if __name__ == '__main__':
    main()
