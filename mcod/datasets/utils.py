from django.shortcuts import get_object_or_404
import os
import pandas as pd

from mcod.resources.models import Resource


def detect_delimiter(csvFile, encoding='iso-8859-2'):
    with open(csvFile, 'r', encoding=encoding) as myCsvfile:
        header = myCsvfile.readline()
        if header.find(";") != -1:
            return ";"
        if header.find(",") != -1:
            return ","
    # default delimiter (MS Office export)
    return ";"


def get_csv_path_by_resource(resource_id):
    resource = get_object_or_404(Resource, pk=resource_id)
    filename = resource.file.name
    filename = os.path.join('test-data/media/resources', filename)

    return filename


def load_df_from_csv(filename):
    delim = detect_delimiter(filename)
    df = pd.read_csv(filename, encoding='utf-8', delimiter=delim, keep_default_na=False)

    return df
