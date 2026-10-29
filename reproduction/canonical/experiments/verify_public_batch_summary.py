"""Independently verify compact batch exports without importing the analyzer.

This checks the public per-particle NPZ/CSV and report. It does not reread the
large raw trajectories or independently establish continuous physical work.
"""
from pathlib import Path
import csv
import hashlib
import json
import math

import numpy as np

if not __debug__:
    raise RuntimeError('Do not use Python -O: verification guards must remain enabled.')

ROOT = Path(__file__).resolve().parents[1]
BATCHES = ('inter_energy', 'high_energy')
METHODS = ('first_passage', 'left', 'symmetric', 'right')
REGIONS = ('IS1', 'IS2', 'TB', 'DS', 'CS')


def receipt(relative):
    p = ROOT / relative
    return {'path': relative, 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


def close(a, b):
    assert math.isclose(float(a), float(b), rel_tol=5e-14, abs_tol=5e-13), (a, b)


def stats(values, totals):
    # math.fsum is independent of the analyzer's NumPy reductions.
    v = list(map(float, values)); a = list(map(float, totals))
    assert all(math.isfinite(x) for x in v+a)
    assert all(x != 0 for x in a), 'Actual exports require an explicit undefined-ratio route if zero totals appear.'
    n = len(a)
    return {'particles': n,
            'mean_particle_fraction': math.fsum(x/y for x, y in zip(v, a))/n,
            'share_of_total_net_gain': math.fsum(v)/math.fsum(a),
            'regional_net_gain_sum': math.fsum(v),
            'total_net_gain_sum': math.fsum(a),
            'negative_total_count': sum(x < 0 for x in a),
            'negative_regional_gain_count': sum(x < 0 for x in v),
            'fraction_below_zero_count': sum(x/y < 0 for x, y in zip(v, a)),
            'fraction_above_one_count': sum(x/y > 1 for x, y in zip(v, a))}


def channels(data, method, mask):
    x = data[method][mask]
    if method == 'first_passage':
        return {'CS': x[:, 0], 'DS': x[:, 1], 'phase_residual': x[:, 2],
                'CS_plus_phase_residual': x[:, 0]+x[:, 2]}
    return {**{k: x[:, j] for j, k in enumerate(REGIONS)},
            'CS_plus_IS1_plus_IS2': x[:, 4]+x[:, 0]+x[:, 1],
            'all_nonDS_including_TB': x[:, 4]+x[:, 0]+x[:, 1]+x[:, 2]}


def main():
    paths = ['results/public-batch-checks.json',
             'results/public-batch-per-particle.npz',
             'results/public-batch-per-particle.csv',
             'experiments/analyze_public_batches.py',
             'data/upstream-cc0/released-cohort-inventory.json',
             'data/upstream-cc0/first_passage_function.py',
             'data/batch-example-link-verification.json',
             'data/figure6-population-comparison.json',
             *[f'data/upstream-cc0/trajectory_sf{x}.npz' for x in (3, 4, 5)]]
    inputs = [receipt(x) for x in paths]
    before = {x['path']: x['sha256'] for x in inputs}
    report = json.loads((ROOT/paths[0]).read_text(encoding='utf-8'))
    inventory = json.loads((ROOT/paths[4]).read_text(encoding='utf-8'))
    assert report['status'] == 'pass'
    assert report['implementation']['analysis_script_sha256'] == before[paths[3]]
    assert report['implementation']['input_manifest_sha256'] == before[paths[4]]
    assert report['implementation']['source_excerpt_sha256'] == before[paths[5]]
    assert len(inventory['files']) == 32
    records = {x['batch']: x for x in report['batches']}
    assert set(records) == {*BATCHES, 'released_union'}
    data = {}
    with np.load(ROOT/paths[1], allow_pickle=False) as f:
        for batch in BATCHES:
            prefix = batch+'__'
            data[batch] = {k[len(prefix):]: f[k].copy()
                           for k in f.files if k.startswith(prefix)}
    for batch, d in data.items():
        assert len(d['tag']) == records[batch]['particles']
        assert len(set(map(int, d['tag']))) == len(d['tag'])
        assert d['initial_gamma'].dtype == d['final_gamma'].dtype == np.float32
        assert all(np.isfinite(v).all() for v in d.values())
        assert np.array_equal(d['total_net_gain'],
                              d['final_gamma'].astype(float)-d['initial_gamma'].astype(float))
        expected = [x for x in inventory['files'] if x['released_batch'] == batch]
        validated = {x['id']: x for x in records[batch]['raw_inputs_verified']}
        assert len(expected) == len(validated) == 16
        for e in expected:
            v = validated[e['id']]
            assert all(v[k] == e[k] for k in ('sha256', 'size', 'local_relative_path'))
    tags0 = set(map(int, data[BATCHES[0]]['tag']))
    tags1 = set(map(int, data[BATCHES[1]]['tag']))
    assert tags0.isdisjoint(tags1)

    # Verify the full CSV against the NPZ by identity, not row position.
    with (ROOT/paths[2]).open(newline='', encoding='utf-8') as f:
        csv_rows = list(csv.DictReader(f))
    seen = set()
    for row in csv_rows:
        batch, tag = row['released_batch'], int(row['tag'])
        key = batch, tag
        assert key not in seen
        seen.add(key)
        d = data[batch]
        index = np.flatnonzero(d['tag'] == tag)
        assert len(index) == 1
        i = int(index[0])
        expected = {'initial_gamma': d['initial_gamma'][i],
                    'final_gamma': d['final_gamma'][i], 'A': d['total_net_gain'][i],
                    **{f'FP_{k}': d['first_passage'][i, j]
                       for j, k in enumerate(('CS', 'DS', 'phase_residual'))},
                    **{f'{m}_{k}': d[m][i, j]
                       for m in ('left', 'right', 'symmetric')
                       for j, k in enumerate(REGIONS)},
                    **{k: d[k][i] for k in ('region_transitions', 'transition_L1',
                       'CS_samples_after_first_subsequent_DS',
                       'CS_entries_after_first_subsequent_DS')}}
        for k, value in expected.items():
            assert float(row[k]) == float(value), (key, k)
    assert len(seen) == len(csv_rows) == sum(len(x['tag']) for x in data.values())

    pooled = {k: np.concatenate([data[b][k] for b in BATCHES], axis=0)
              for k in data[BATCHES[0]]}
    data['released_union'] = pooled
    checked = {}
    for batch, d in data.items():
        a = d['total_net_gain']
        mask = {'all_posted': np.ones(len(a), dtype=bool),
                'intermediate': (d['final_gamma'] > 5.77) & (d['final_gamma'] < 16.40),
                'high': d['final_gamma'] > 16.40}
        for k, m in mask.items():
            assert int(m.sum()) == records[batch]['strict_band_counts'][k]
        assert np.all(a > 0)  # Recorded result, not an imposed data filter.
        closures = {}
        for method in METHODS:
            residual = np.asarray([math.fsum(map(float, row))-float(total)
                                   for row, total in zip(d[method], a)])
            closures[method] = float(np.max(np.abs(residual)))
            if method != 'first_passage':
                assert closures[method] < 1e-9
        assert np.array_equal(d['symmetric'], .5*(d['left']+d['right']))
        for method in ('left', 'right'):
            assert np.allclose(d[method+'_gross_positive']+d[method+'_gross_negative'],
                               d[method], rtol=0, atol=1e-9)
        assert np.all(np.abs(d['right']-d['left']) <= d['endpoint_difference_bound']+1e-9)
        assert np.all(np.abs(d['right']-d['left']).sum(axis=1) <= 2*d['transition_L1']+1e-9)
        bands = {}
        for band, m in mask.items():
            if not m.any():
                continue
            claimed = records[batch]['subsets'][band]
            methods = {}
            for method in METHODS:
                c = channels(d, method, m)
                for label, values in c.items():
                    computed = stats(values, a[m])
                    target = claimed[method][label]
                    for own, theirs in [('mean_particle_fraction', 'unfiltered_particle_mean_fraction'),
                                         ('share_of_total_net_gain', 'aggregate_net_gain_share'),
                                         ('regional_net_gain_sum', 'regional_net_gain_sum'),
                                         ('total_net_gain_sum', 'total_net_gain_sum')]:
                        close(computed[own], target[theirs])
                    for own, theirs in [('negative_total_count', 'negative_total_count'),
                                         ('negative_regional_gain_count', 'negative_regional_net_gain_count'),
                                         ('fraction_below_zero_count', 'fraction_below_zero_count'),
                                         ('fraction_above_one_count', 'fraction_above_one_count')]:
                        assert computed[own] == target[theirs]
                methods[method] = stats(c['DS'], a[m])
                if method != 'first_passage':
                    assert np.allclose(c['all_nonDS_including_TB']-c['CS_plus_IS1_plus_IS2'],
                                       c['TB'], rtol=0, atol=1e-12)
                    assert np.allclose(c['all_nonDS_including_TB']+c['DS'], a[m],
                                       rtol=0, atol=1e-9)
            fp = d['first_passage'][m]
            assert np.array_equal(fp[:, 1], fp[:, 1].astype(np.float32).astype(np.float64))
            old_denominator = fp.sum(axis=1)
            native = stats(fp[:, 1], old_denominator)
            native_target = claimed['first_passage']['original_source_mean_DS_using_source_sum_denominator']
            close(native['mean_particle_fraction'], native_target['unfiltered_particle_mean_fraction'])
            shifts = {}
            for method in ('left', 'symmetric', 'right'):
                difference = d[method][m, 3]-fp[:, 1]
                shifts[method] = {
                    'mean_particle_fraction_change_percentage_points':
                        100*math.fsum(float(v)/float(t) for v, t in zip(difference, a[m]))/int(m.sum()),
                    'batch_net_gain_share_change_percentage_points':
                        100*math.fsum(map(float, difference))/math.fsum(map(float, a[m]))}
                close(shifts[method]['mean_particle_fraction_change_percentage_points'],
                      100*(methods[method]['mean_particle_fraction']-methods['first_passage']['mean_particle_fraction']))
            # Every FP DS branch is either zero or one native float32
            # subtraction. Standard round-to-nearest error gives this bound
            # relative to subtracting the same stored endpoints in float64.
            # Include the subnormal half-ulp term for completeness. This says
            # nothing about unrecorded gamma or temporal/physical error.
            u32 = float(np.finfo(np.float32).eps)/2
            half_subnormal = float(np.nextafter(np.float32(0), np.float32(1)))/2
            ds_rounding_bound = u32/(1-u32)*np.abs(fp[:, 1])+half_subnormal
            bands[band] = {'particles': int(m.sum()), 'downstream': methods,
                           'paired_changes_from_FP': shifts,
                           'FP_source_sum_vs_common_endpoint_denominator_mean_difference':
                               native['mean_particle_fraction']-methods['first_passage']['mean_particle_fraction'],
                           'FP_source_closure_max_abs': float(np.max(np.abs(fp.sum(axis=1)-a[m]))),
                           'FP_DS_single_subtraction_rounding_mean_fraction_error_bound':
                               math.fsum(float(v)/float(t) for v, t in zip(ds_rounding_bound, a[m]))/int(m.sum()),
                           'FP_DS_single_subtraction_rounding_aggregate_share_error_bound':
                               math.fsum(map(float, ds_rounding_bound))/math.fsum(map(float, a[m])),
                           'particles_with_CS_after_first_subsequent_DS':
                               int(np.sum(d['CS_samples_after_first_subsequent_DS'][m] > 0)),
                           'CS_entries_after_first_subsequent_DS':
                               int(d['CS_entries_after_first_subsequent_DS'][m].sum()),
                           'region_transition_count': int(d['region_transitions'][m].sum()),
                           'transition_L1_net_increment_sum':
                               math.fsum(map(float, d['transition_L1'][m])),
                           'zero_total_count': int(np.sum(a[m] == 0)),
                           'negative_total_count': int(np.sum(a[m] < 0))}
        checked[batch] = {'particles': len(a), 'signed_closure_max_abs': closures,
                          'minimum_total_net_gain': float(a.min()), 'subsets': bands}
    assert len(pooled['tag']) == 1003
    assert records['released_union']['strict_band_counts']['intermediate'] == 667
    assert records['released_union']['strict_band_counts']['high'] == 84
    assert int(np.sum(pooled['final_gamma'] < 5.77)) == 252
    assert not np.any((pooled['final_gamma'] == 5.77) | (pooled['final_gamma'] == 16.40))

    # Verify the separate source agent's exact-history linkage receipt against
    # the small public fixtures and the matching compact per-particle records.
    # No second read of the raw GB batches is performed here.
    linkage = json.loads((ROOT/paths[6]).read_text(encoding='utf-8'))
    assert {x['figure'] for x in linkage['matches_summary']} == {9, 10, 11}
    example_checks = []
    for figure in (9, 10, 11):
        sf = figure-6
        summary = next(x for x in linkage['matches_summary'] if x['figure'] == figure)
        assert summary['folder'] == 'high_energy' and summary['all_four_arrays_exact'] is True
        comparison = next(x for x in linkage['comparisons']
                          if x['preprint_figure'] == figure and x['posted_folder'] == summary['folder'])
        assert len(comparison['matches']) == 1
        match = comparison['matches'][0]
        d = data[summary['folder']]
        index = int(np.flatnonzero(d['tag'] == summary['particle_tag'])[0])
        assert index == summary['column_zero_based'] == match['column_zero_based']
        with np.load(ROOT/f'data/upstream-cc0/trajectory_sf{sf}.npz', allow_pickle=False) as f:
            fixture = {k: f[k].copy() for k in ('gamma', 'xx', 'zz', 'regiondata')}
        for name, values in fixture.items():
            evidence = match['fields'][name]
            digest = hashlib.sha256(values.tobytes(order='C')).hexdigest()
            assert evidence['all_values_equal'] is evidence['digest_matches'] is True
            assert digest == evidence['fixture_c_order_bytes_sha256']
            assert digest == evidence['concatenated_batch_values_in_fixture_dtype_sha256']
            assert len(values) == evidence['samples_compared'] == 40764
        g = fixture['gamma']; r = fixture['regiondata'].astype(np.int64)
        assert g[0] == d['initial_gamma'][index] and g[-1] == d['final_gamma'][index]
        dg = np.diff(g.astype(np.float64))
        for method, labels in (('left', r[:-1]), ('right', r[1:])):
            reference = np.bincount(labels, weights=dg, minlength=6)[1:6]
            assert np.array_equal(reference, d[method][index])
        cs = np.flatnonzero(r == 5); ds = np.flatnonzero(r == 4)
        fp = np.zeros(3)
        if len(cs):
            a, z = int(cs[0]), int(cs[-1]); subsequent = ds[ds > a]
            if len(subsequent):
                b = int(subsequent[0]); fp[:] = (g[b]-g[a], g[-1]-g[b], g[a]-g[0])
            else:
                fp[:] = (g[z]-g[a], 0, (g[a]-g[0])+(g[-1]-g[z]))
        elif len(ds):
            b = int(ds[0]); fp[:] = (0, g[-1]-g[b], g[b]-g[0])
        else:
            fp[:] = (0, 0, g[-1]-g[0])
        assert np.array_equal(fp, d['first_passage'][index])
        example_checks.append({'source_figure': figure, 'fixture': f'trajectory_sf{sf}.npz',
                               'tag': int(d['tag'][index]), 'fixture_digest_linkage_verified': True,
                               'compact_FP_and_full_history_values_verified': True})

    figure6 = json.loads((ROOT/paths[7]).read_text(encoding='utf-8'))
    # This dependency must use a primary report, avoiding a circular hash link
    # through this derived independent-verification receipt.
    primary = figure6['released_calculation']
    assert primary['report'] == paths[0] and primary['report_sha256'] == before[paths[0]]
    for item in figure6['L320_comparisons']:
        band = item['band']
        own = checked['released_union']['subsets'][band]['downstream']['first_passage']['mean_particle_fraction']
        close(own, item['released_union_FP_DS_mean_particle_fraction'])
        source_point = next(x for x in figure6['source_vector_points'][band+'_DS'] if x['L_over_de'] == 320)
        axis = figure6['axis_calibration'][band]
        y0, y1 = axis['y_pdf_top_origin'][0], axis['y_pdf_top_origin'][-1]
        v0, v1 = axis['tick_values'][0], axis['tick_values'][-1]
        calibrated = v0+(source_point['y_pdf_points_top_origin']-y0)*(v1-v0)/(y1-y0)
        close(calibrated, source_point['fraction_from_axis_calibration'])
        close(calibrated, item['published_L320_DS_plotted_fraction'])
        close(own-calibrated, item['difference_fraction'])
        close(100*(own-calibrated), item['difference_percentage_points'])
        assert item['matches_at_three_decimal_reporting_precision'] == (f'{own:.3f}' == f'{calibrated:.3f}')
        assert item['exact_plot_coordinate_match_within_tolerance'] is False
    assert all(receipt(x)['sha256'] == before[x] for x in paths), 'An input changed during verification'
    result = {'schema_version': 1, 'status': 'pass',
              'method': 'No analyzer import; math.fsum reductions, identity-keyed CSV/NPZ equality, direct endpoint differences and named region channels.',
              'scope': 'Independent verification of compact per-particle outputs and their report; raw GB arrays were not reread.',
              'inputs': inputs, 'verifier': receipt('experiments/verify_public_batch_summary.py'),
              'CSV_NPZ_exact_numeric_agreement': True,
              'disjoint_unique_processed_tags': True,
              'input_manifest_report_32_bindings_consistent': True,
              'all_signed_closures_and_TB_groupings_verified': True,
              'three_source_example_linkages_checked_against_small_fixtures': example_checks,
              'figure6_comparison': {
                  'intermediate_published_point_not_reproduced': True,
                  'high_agrees_at_three_decimal_reporting_precision_only': True,
                  'does_not_establish_historical_complete_cohort_identity': True},
              'pooled_counts': {'released': 1003, 'strict_selected': 751,
                                'intermediate': 667, 'high': 84, 'below_lower_cut': 252,
                                'at_separator': 0},
              'results': checked,
              'interpretation_limits': [
                  'The released convenience batches have unknown inclusion probabilities.',
                  'The comparisons are saved-increment estimators, not continuous regional-work validation.',
                  'Native FP denominator effects are measured separately; they do not explain the large attribution shifts.',
                  'Source endpoint annotations and plotting reconstruction do not identify the original full Fig. 6 execution.']}
    output = ROOT/'results/public-batch-independent-verification.json'
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'pooled_counts': result['pooled_counts'],
                      'pooled_results': checked['released_union']['subsets']}, indent=2))


if __name__ == '__main__':
    main()
