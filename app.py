import os
from edupage_api import Edupage, Term

welcome_art = """
\033[91m  ______    _                                _____                      _                 _
\033[91m |  ____|  | |                              |  __ \                    | |               | |
\033[91m | |__   __| |_   _ _ __   __ _  __ _  ___  | |  | | _____      ___ __ | | ___   __ _  __| | ___ _ __
\033[91m |  __| / _` | | | | '_ \ / _` |/ _` |/ _ \ | |  | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
\033[91m | |___| (_| | |_| | |_) | (_| | (_| |  __/ | |__| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |
\033[91m |______\__,_|\__,_| .__/ \__,_|\__, |\___| |_____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|
\033[91m                   | |           __/ |
\033[91m                   |_|          |___/
\033[97m"""
print(welcome_art + "Ďakujeme, za využitie tohoto jednoduchého python programu\n ")


def get_credentials():
    meno = input("Zadaj svoje meno(meno do edupage): ")
    heslo = input("Zadaj svoje heslo(heslo do edupage): ")
    skola = input("Zadaj tvojej školy subdoménu (subdomena.eduapge.org): ")
    if not meno or not heslo or not skola:
        print("Prihlasovacie údaje nemôžu byť prázdne.")
        exit()
    
    return meno, heslo, skola


def create_grades_folder():
    try:
        os.mkdir('znamky')
    except FileExistsError:
        pass

def get_school_years(currentrok):
    return list(range(2014, currentrok))


def get_grades_by_subject(grades):
    grades_by_subject = {}
    for grade in grades:
        if grade.subject_name in grades_by_subject:
            grades_by_subject[grade.subject_name].append(grade)
        else:
            grades_by_subject[grade.subject_name] = [grade]
    return grades_by_subject


def save_grades_to_file(year, term, grades_by_subject):
    filename = f"{year}_{term}_znamky.txt"
    with open(os.path.join("znamky", filename), "w", encoding="utf-8") as f:
        for subject, subject_grades in grades_by_subject.items():
            f.write("----------------\n")
            f.write(f"{subject}:\n")
            for grade in subject_grades:
                f.write(f"    {grade.title} -> ")
                if grade.max_points != 100:
                    f.write(f"{grade.grade_n}/{grade.max_points}\n")
                else:
                    f.write(f"{grade.percent}%\n")



if __name__ == "__main__":
    edupage_client = Edupage()
    meno, heslo, skola = get_credentials()
    print("Vytváram zložku znamky")
    create_grades_folder()
    print("Prihlasujem sa do Edupage...")
    edupage_client.login(meno, heslo, skola)
    grades = edupage_client.get_grades()
    currentrok = edupage_client.get_school_year()
    school_years = get_school_years(currentrok)

    for year in school_years:
        print(f"Sťahujem známky z roku {year}")
        first_term_grades = edupage_client.get_grades_for_term(year, Term.FIRST)
        second_term_grades = edupage_client.get_grades_for_term(year, Term.SECOND)
        all_grades = first_term_grades + second_term_grades
        grades_by_subject = get_grades_by_subject(all_grades)
        save_grades_to_file(year, "1polrok", grades_by_subject)
        save_grades_to_file(year, "2polrok", grades_by_subject)

    print("Sťahujem všetkých žiakov školy...")
    zaci = edupage_client.get_all_students()
    if zaci == "[]":
        print("Škola nepovolila stiahnutie všetkých žiakov...")
    else:
        with open("ziaciskoly.txt", "w", encoding="utf-8") as f:
            f.write("Meno(ID), KrátkeMeno, Trieda\n")
            for zaci in zaci:
                f.write(f"{zaci.name}, {zaci.gender.name}, {zaci.in_school_since}, {zaci.account_type.name}\n")

    print("Sťahujem žiakov v tvojej triede...")
    nasizaci = edupage_client.get_students()
    with open("ziacivtriede.txt", "w", encoding="utf-8") as f:
        f.write("Meno(ID), KrátkeMeno, Trieda\n")
        for nasi in nasizaci:
            f.write(f"{nasi}\n")


    print("Sťahujem učiteľov na škole...")
    teachers = edupage_client.get_teachers()
    with open("ucitelia.txt", "w", encoding="utf-8") as f:
        f.write("Meno(ID), Pohlavie, Nástup do školy, Typ\n")
        for teacher in teachers:
            f.write(f"{teacher.name}({teacher.person_id}), {teacher.gender.name}, "
                    f"{teacher.in_school_since.year}/{teacher.in_school_since.month}/{teacher.in_school_since.day}, "
                    f"{teacher.account_type.name}\n")

    print("Sťahujem najnovšie notifikácie...")
    notifications = edupage_client.get_notifications()
    with open("notifikace.txt", "w", encoding="utf-8") as f:
        for notifikace in notifications:
            f.write(f"{notifikace.author}, {notifikace.event_id}, {notifikace.event_type}, {notifikace.text}, "
                    f"{notifikace.timestamp}\n------------------------------------------------------------------------------------------------------------------------------------------------------------\n")

    print("Sťahujem tvoje Edupage School ID")
    tvojeid = edupage_client.get_user_id()
    with open("tvojeid.txt", "w", encoding="utf-8") as f:
        f.write(f"{tvojeid}")
