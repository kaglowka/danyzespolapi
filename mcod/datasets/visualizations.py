from collections import defaultdict


def analyze_col(col):
    name = col.name

    min_val = col.min()
    max_val = col.max()

    col_type = 'string'
    if col.dtype in (int, float):
        col_type = 'number'

        cast_to = int if col.dtype == int else float
        min_val = cast_to(min_val)
        max_val = cast_to(max_val)

    num_uniques = col.unique().size

    summary = {
        'header': name,
        'type': col_type,
        'unique': num_uniques,
        'rangeFrom': min_val,
        'rangeTo': max_val
    }
    print(summary)
    return summary


def analyze_df(df):
    summaries = []
    for col_name in df:
        column = df[col_name]
        col_summ = analyze_col(column)
        summaries.append(col_summ)

    return summaries


COMPARISON_TYPES = ['=']


def translate_comparison(comp_str_frontend):
    """
    Changes the comparison string/character sent from frontend into pandas query operator,
    eg. '=' -> '=='
    """
    if comp_str_frontend == '=':
        return '=='
    return comp_str_frontend


def filter_df(df, params):
    # parse params
    x_name = params['x']
    y_name = params['y']
    aggr_operation = params['operation']
    filter_str = params['filter']

    # parse and construct filter strings
    # dict containing lists of pandas query strings for particular columns (keys)
    col_filters = defaultdict(list)

    for filter in filter_str.split(','):
        comparison = None
        # parse comparison type
        for comp_type in COMPARISON_TYPES:
            if comp_type in filter:
                comparison = comp_type
        if not comparison:
            # could not parse comparison operation type - ignore this filter
            continue

        col_name, comp_val = filter.split(comparison)
        # comparison unused for now
        comparison = translate_comparison(comparison)
        col_filters[col_name].append(comp_val)

    # filter out data
    for col_name, vals in col_filters.items():
        df = df.loc[df[col_name].isin(vals)]

    if aggr_operation:
        if aggr_operation == 'unique':
            df = df.groupby(x_name)[x_name].agg('count')
            x = df.index.values
            y = df.values
    else:
        # default aggregation - SUM
        df = df.groupby(x_name)[y_name].agg('sum')
        x = df.index.values
        y = df.values

    return x.tolist(), y.tolist()
