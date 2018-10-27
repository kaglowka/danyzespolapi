def analyze_col(col):
    name = col.name

    min_val = col.min()
    max_val = col.max()

    col_type = 'tekst'
    if col.dtype in (int, float):
        col_type = 'liczba'
        min_val = int(min_val)
        max_val = int(max_val)

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