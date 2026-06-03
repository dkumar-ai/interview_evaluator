def calculate_mastery(report):

    readiness = report.get(
        "readiness_score",
        0
    )

    return round(
        readiness / 100,
        2
    )