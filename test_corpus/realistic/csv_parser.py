
import csv
from io import StringIO

def parse_csv(content, delimiter=','):
    reader = csv.DictReader(StringIO(content), delimiter=delimiter)
    return list(reader)

def write_csv(rows, fields, delimiter=','):
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
