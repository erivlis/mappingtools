import timeit
from collections import Counter, defaultdict

from mappingtools.aggregation import Aggregation
from mappingtools.operators import pivot, rekey


# Mock of the old inline logic for pivot (for comparison)
def pivot_old_logic(iterable, index, columns, values, mode=Aggregation.LAST):
    if mode == Aggregation.ALL:
        result = defaultdict(lambda: defaultdict(list))
    elif mode == Aggregation.COUNT:
        result = defaultdict(lambda: defaultdict(Counter))
    elif mode == Aggregation.DISTINCT:
        result = defaultdict(lambda: defaultdict(set))
    else:
        result = defaultdict(dict)

    for item in iterable:
        if index not in item or columns not in item or values not in item:
            continue
        row_key = item[index]
        col_key = item[columns]
        val = item[values]

        target = result[row_key]
        if mode == Aggregation.ALL:
            target[col_key].append(val)
        elif mode == Aggregation.COUNT:
            target[col_key].update({val: 1})
        elif mode == Aggregation.DISTINCT:
            target[col_key].add(val)
        elif mode == Aggregation.FIRST:
            if col_key not in target:
                target[col_key] = val
        else:  # LAST
            target[col_key] = val

    final_result = {}
    for row_k, row_v in result.items():
        final_result[row_k] = dict(row_v)
    return final_result


# Benchmarking data
data = [{"city": f"city_{i % 100}", "month": f"month_{i % 12}", "temp": i} for i in range(10000)]


# Functional primitive using if-elif instead of match
def collect_if_elif(mapping, key, value, mode):
    if mode == Aggregation.ALL:
        mapping[key].append(value)
    elif mode == Aggregation.COUNT:
        mapping[key].update({value: 1})
    elif mode == Aggregation.DISTINCT:
        mapping[key].add(value)
    elif mode == Aggregation.FIRST:
        if key not in mapping:
            mapping[key] = value
    elif mode == Aggregation.LAST:
        mapping[key] = value


def pivot_if_elif(iterable, index, columns, values, aggregation=Aggregation.LAST):
    ctype = aggregation.collection_type
    result = defaultdict(lambda: defaultdict(ctype)) if ctype else defaultdict(dict)

    for item in iterable:
        if index not in item or columns not in item or values not in item:
            continue
        row_key = item[index]
        col_key = item[columns]
        val = item[values]
        collect_if_elif(result[row_key], col_key, val, aggregation)

    final_result = {}
    for row_k, row_v in result.items():
        final_result[row_k] = dict(row_v)
    return final_result


# Optimized pivot using local binding
def pivot_optimized(iterable, index, columns, values, mode=Aggregation.LAST):
    ctype = mode.collection_type
    result = defaultdict(lambda: defaultdict(ctype)) if ctype else defaultdict(dict)

    # Optimization: Bind the global collect to a local variable
    local_collect = mode.aggregate_one

    for item in iterable:
        if index not in item or columns not in item or values not in item:
            continue
        row_key = item[index]
        col_key = item[columns]
        val = item[values]
        local_collect(result[row_key], col_key, val)

    final_result = {}
    for row_k, row_v in result.items():
        final_result[row_k] = dict(row_v)
    return final_result


# Hyper-optimized pivot using specialized local binding
def pivot_hyper_opt(iterable, index, columns, values, mode=Aggregation.LAST):
    ctype = mode.collection_type
    result = defaultdict(lambda: defaultdict(ctype)) if ctype else defaultdict(dict)

    # Specialization: Create a specialized closure or bind the specific operation
    if mode == Aggregation.ALL:

        def aggregate(target, k, v):
            target[k].append(v)
    elif mode == Aggregation.COUNT:

        def aggregate(target, k, v):
            target[k].update({v: 1})
    elif mode == Aggregation.DISTINCT:

        def aggregate(target, k, v):
            target[k].add(v)
    elif mode == Aggregation.FIRST:

        def aggregate(target, k, v):
            if k not in target:
                target[k] = v
    else:  # LAST

        def aggregate(target, k, v):
            target[k] = v

    for item in iterable:
        if index not in item or columns not in item or values not in item:
            continue
        row_key = item[index]
        col_key = item[columns]
        val = item[values]
        aggregate(result[row_key], col_key, val)

    final_result = {}
    for row_k, row_v in result.items():
        final_result[row_k] = dict(row_v)
    return final_result


def benchmark():
    print("Benchmarking pivot (10,000 records)...")

    for mode in Aggregation:
        t_old = timeit.timeit(
            lambda: pivot_old_logic(data, index="city", columns="month", values="temp", mode=mode),
            number=100
        )
        t_new = timeit.timeit(
            lambda: pivot(data, index="city", columns="month", values="temp", aggregation=mode),
                              number=100
        )
        t_hyper = timeit.timeit(
            lambda: pivot_hyper_opt(data, index="city", columns="month", values="temp", mode=mode),
            number=100
        )

        diff_new = (t_new - t_old) / t_old * 100
        diff_hyper = (t_hyper - t_old) / t_old * 100
        print(
            f"Mode {mode.name:8}: Old: {t_old:.4f}s,"
            f" New: {t_new:.4f}s"
            f" ({diff_new:+.2f}%), Hyper (Closure): {t_hyper:.4f}s ({diff_hyper:+.2f}%)"
        )

    print("\nBenchmarking rekey (10,000 items)...")
    mapping = {i: i for i in range(10000)}

    # Old rekey would have used MappingCollector internally which had the match logic
    # Actually, before the extraction, rekey was using MappingCollector which had the match logic in its 'add' method.

    t_rekey = timeit.timeit(lambda: rekey(mapping, lambda k, v: k % 100, aggregation=Aggregation.LAST), number=100)
    print(f"Rekey (New): {t_rekey:.4f}s")


if __name__ == "__main__":
    benchmark()
