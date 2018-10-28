def detect_delimiter(csvFile, encoding='iso-8859-2'):
    with open(csvFile, 'r', encoding=encoding) as myCsvfile:
        header = myCsvfile.readline()
        if header.find(";") != -1:
            return ";"
        if header.find(",") != -1:
            return ","
    # default delimiter (MS Office export)
    return ";"
