import os
from edupage_api import Edupage, Term, exceptions
from requests import exceptions as requestexceptions

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
print(welcome_art + "Thank you for using this simple python program\n ")


def get_credentials():
    print("Please fill up login information")
    username = input("Enter your name(name in edupage): ")
    password = input("Enter your password(edupage password): ")
    schooldomain = input("Enter your school's subdomain (subdomain.eduapge.org): ")
    if not username or not password or not schooldomain:
        print("Login details cannot be blank.")
        exit()
    
    return username, password, schooldomain


def create_grades_folder():
    try:
        os.mkdir('grades')
    except FileExistsError:
        pass

def get_school_years(currentrok):
    yearyoustarted = int(input("Which year was your Edupage registered? (Propably when you get into the school) "))
    if not str(yearyoustarted).isdigit():
        print(f"I don´t know if {yearyoustarted} is a year :D ")
        exit()
    if yearyoustarted < 2012:
        print(f"I don´t know if you started in year {yearyoustarted} or do you want to timeout your Edupage?.")
        exit()
    if yearyoustarted > 2023:
        print(f"Yes, you are very funny...")
        exit()
    return list(range(yearyoustarted, currentrok))


def get_grades_by_subject(grades):
    grades_by_subject = {}
    for grade in grades:
        if grade.subject_name in grades_by_subject:
            grades_by_subject[grade.subject_name].append(grade)
        else:
            grades_by_subject[grade.subject_name] = [grade]
    return grades_by_subject


def save_grades_to_file(year, term, grades_by_subject):
    filename = f"{year}_{term}_grades.txt"
    with open(os.path.join("grades", filename), "w", encoding="utf-8") as f:
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
    try:
        edupage_client = Edupage()
        username, password, schooldomain = get_credentials()
        print("Creating grades folder")
        create_grades_folder()
        print("Logging in to Edupage...")
        try:
            edupage_client.login(username, password, schooldomain)
        except exceptions.BadCredentialsException:
            print("You entered wrong username or password")
            exit()
        else:
            print("Logged in!")
       
        grades = edupage_client.get_grades()
        currentyear = edupage_client.get_school_year()
        school_years = get_school_years(currentyear)
    
        for year in school_years:
            print(f"Downloading grades from year {year}")
            first_term_grades = edupage_client.get_grades_for_term(year, Term.FIRST)
            second_term_grades = edupage_client.get_grades_for_term(year, Term.SECOND)
            all_grades = first_term_grades + second_term_grades
            grades_by_subject = get_grades_by_subject(all_grades)
            save_grades_to_file(year, "1term", grades_by_subject)
            save_grades_to_file(year, "2term", grades_by_subject)

        print("Downloading all students from your school...")
        allstudents = edupage_client.get_all_students()
        if allstudents == "[]":
            print("The school did not authorise the download of all pupils...")
        else:
           with open("allstudents.txt", "w", encoding="utf-8") as f:
                f.write("User(ID), ShortName, Class\n")
                for allstudents in allstudents:
                    f.write(f"{allstudents.name}, {allstudents.gender.name}, {allstudents.in_school_since}, {allstudents.account_type.name}\n")

        print("Downloading the students in your class...")
        ourstudents = edupage_client.get_students()
        with open("studentsinyourclass.txt", "w", encoding="utf-8") as f:
            f.write("NumberInClass User, Gender, InSchoolSince\n")
            for ourstudents in ourstudents:
                f.write(f"{ourstudents.number_in_class} {ourstudents.name} {ourstudents.gender} {ourstudents.in_school_since} {ourstudents.account_type}\n")


        print("Downloading teachers in schools...")
        teachers = edupage_client.get_teachers()
        with open("teachers.txt", "w", encoding="utf-8") as f:
           f.write("User(ID), Gender, InSchoolSince, Type\n")
           for teacher in teachers:
                f.write(f"{teacher.name}({teacher.person_id}), {teacher.gender.name}, "
                    f"{teacher.in_school_since.year}/{teacher.in_school_since.month}/{teacher.in_school_since.day}, "
                    f"{teacher.account_type.name}\n")

        print("Downloading your notifications...")
        notifications = edupage_client.get_notifications()
        with open("notifications.txt", "w", encoding="utf-8") as f:
            for notifikace in notifications:
                f.write(f"{notifikace.author}, {notifikace.event_id}, {notifikace.event_type}, {notifikace.text}, "
                        f"{notifikace.timestamp}\n------------------------------------------------------------------------------------------------------------------------------------------------------------\n")

        print("Download your Edupage School ID")
        tvojeid = edupage_client.get_user_id()
        with open("yourid.txt", "w", encoding="utf-8") as f:
            f.write(f"{tvojeid}")

        print("Successfully downloaded your Edupage profile! Thank you for using this simple python program!")
        exit()
    except ConnectionError:
        print("Edupage timeouted your connection please wait like 30minutes!")
        exit()
    except exceptions.NotLoggedInException:
        print("Wtf? How you cannot be logged in, please try again later. This can be some bug or error. I dont have any idea how to fix this.")
        exit()
    except exceptions.RequestError:
        print("Edupage is so laggy and old. So request error is something that i except, so try again please.")
        exit()
    except requestexceptions.ConnectionError:
        print("Edupage timeouted your connection please wait like 30minutes!")
        exit()
    else:
        print("Something went wrong, please try again later.")
        exit()