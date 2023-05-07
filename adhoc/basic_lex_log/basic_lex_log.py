import click
import csv
import hashlib
import re
from datetime import datetime


def extract_log_info(line):
    # Extract timestamp
    timestamp_str = line.split()[3][1:]
    timestamp = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S")
    formatted_timestamp = timestamp.strftime("%Y/%m/%d %H.%M.%S")

    # Extract IP address
    ip_address = hashlib.sha256(line.split()[0].encode("utf-8")).hexdigest()

    # Extract query parameter and type
    try:
        query_params = line.split()[6].split("?")[1].split("&")
    except IndexError:
        query_type = "error"
        query = None
    else:
        query_param_dict = dict(
            param.split("=") for param in query_params if param.count("=") == 1
        )
        if len(query_param_dict) == 1 and "query" in query_param_dict:
            query_type = "query"
            query = query_param_dict["query"]
        else:
            query_type = "other"
            query = None

    # Extract caller type
    user_agent = line.split('"')[-2]
    if re.search(r"(bot|spider|crawler|slurp)", user_agent, re.IGNORECASE):
        caller_type = "robot"
    else:
        caller_type = "human"

    return formatted_timestamp, query_type, query, caller_type, ip_address


@click.command()
@click.argument("logfile", type=click.Path(exists=True))
@click.argument("outputfile", type=click.Path())
def analyze_logs(logfile, outputfile) -> None:
    with open(outputfile, "w", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter="\t")
        writer.writerow(
            [
                "timestamp",
                "query_type",
                "query",
                "caller_type",
                "hashed_ip_address",
            ]
        )
        with open(logfile) as f:
            for line in f:
                log_info = extract_log_info(line)
                writer.writerow(log_info)


if __name__ == "__main__":
    analyze_logs()
