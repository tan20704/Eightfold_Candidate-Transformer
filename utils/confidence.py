def calculate_confidence(csv_data, resume_data, profile):

    score = 0
    total = 0

    fields = [
        "full_name",
        "emails",
        "phones",
        "location",
        "headline",
        "skills"
    ]

    for field in fields:

        total += 1

        csv_value = csv_data.get(field)
        resume_value = resume_data.get(field)

        if csv_value and resume_value:

            if csv_value == resume_value:

                score += 1.0

            else:

                score += 0.6

        elif csv_value:

            score += 0.9

        elif resume_value:

            score += 0.8

    if total == 0:
        return 0

    return round(score / total, 2)