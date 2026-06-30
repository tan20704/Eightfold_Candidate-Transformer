from validator.schema import Provenance


def build_provenance(csv_data, resume_data, merged_profile):

    provenance = []

    fields = [
        "full_name",
        "emails",
        "phones",
        "location",
        "headline",
        "skills",
        "experience",
        "education"
    ]

    for field in fields:

        csv_value = csv_data.get(field)
        resume_value = resume_data.get(field)

        if csv_value and resume_value:

            if csv_value == resume_value:
                source = "csv,resume"

            else:
                source = "csv"

        elif csv_value:

            source = "csv"

        elif resume_value:

            source = "resume"

        else:

            continue

        provenance.append(

            Provenance(
                field=field,
                source=source
            )

        )

    return provenance