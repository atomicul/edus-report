from typing import List

from scraper.base_edus_scraper import BaseEdusScraper


def absences(scraper: BaseEdusScraper):
    absences = sorted(scraper.get_absences(), key=lambda x: x.date, reverse=True)

    head = ["subject", "date", "motivated?"]
    body = [[a.subject, str(a.date), str(a.is_motivated)] for a in absences]

    return [head, *body]


def grades(scraper: BaseEdusScraper):
    grades = sorted(scraper.get_grades(), key=lambda x: x.date, reverse=True)

    head = ["subject", "date", "grade"]
    body = [[g.subject, str(g.date), str(g.grade)] for g in grades]

    return [head, *body]


def per_subject_report(scraper: BaseEdusScraper):
    grades = scraper.get_grades_by_subject()
    absences = scraper.get_absences_by_subject()

    head = ["subject", "absences", "unmotivated absences", "grades", "average"]
    body = []

    for subject in set(grades.keys()) | set(absences.keys()):
        row = []
        row.append(subject)
        row.append(len(absences[subject]) if subject in absences else 0)
        row.append(sum(1 for a in absences.get(subject, []) if not a.is_motivated))
        row.append(len(grades[subject]) if subject in grades else 0)

        if subject in grades:
            row.append(
                round(sum(g.grade for g in grades[subject]) / len(grades[subject]))
            )
        else:
            row.append(0)
        body.append(row)

    return [head, *body]


def aggregates(scraper: BaseEdusScraper) -> List[List[str]]:
    absences = scraper.get_absences()
    head = ["total absences", "unmotivated absences", "grade average"]
    body = []
    body.append(len(absences))
    body.append(sum(1 for a in absences if not a.is_motivated))
    body.append(scraper.get_year_wide_average())

    return [head, body]
