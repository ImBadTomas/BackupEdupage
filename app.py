from edupage_api import Edupage, Term
import os
from getpass import getpass
edupage = Edupage()

meno = input("Zadaj svoje meno(meno do edupage): ")
heslo = getpass(prompt="Zadaj svoje heslo(heslo do edupage) - (Heslo je neviditeľné): ")
skola = input("Zadaj svoju školu pred-domenu (tvojaskola.edupage.org)")


edupage.login(meno, heslo, skola)

try:
    os.mkdir('znamky')
except FileExistsError:
    pass

grades = edupage.get_grades()
grades_by_subject = {}

def get_school_years():
  school_years = []
  for year in range(2014, edupage.get_school_year()):
    school_years.append(year)
  return school_years

def get_grades_for_term(year, term):
  grades = edupage.get_grades_for_term(year, term)
  return grades

def save_grades_to_file(year, grades, term):
  filename = f"{year}_{term}_grades.txt"
  with open(os.path.join("znamky", filename), "w", encoding="utf-8") as f:
    grades_by_subject = {}
    for grade in grades:
      if grades_by_subject.get(grade.subject_name):
        grades_by_subject[grade.subject_name] += [grade]
      else:
        grades_by_subject[grade.subject_name] = [grade]
    for subject in grades_by_subject:
      f.write(f"{subject}:\n")
      for grade in grades_by_subject[subject]:
        f.write(f"    {grade.title} -> ")
        if grade.max_points != 100:
          f.write(f"{grade.grade_n}/{grade.max_points}\n")
        else:
          f.write(f"{grade.percent}%\n")

if __name__ == "__main__":
  school_years = get_school_years()
  for year in school_years:
    print(f"Downloading grades from {year} year")
    first_term_grades = get_grades_for_term(year, Term.FIRST)
    save_grades_to_file(year, first_term_grades, "1polrok")
    second_term_grades = get_grades_for_term(year, Term.SECOND)
    save_grades_to_file(year, second_term_grades, "2polrok")

print("Downloading all students")
zaci = edupage.get_all_students()

with open("ziaciskoly.txt", "w", encoding="utf-8") as f:
    f.write("Meno(ID), KrátkeMeno, Trieda")
    for zaci in zaci:
        f.write(f"UnknownStudent ({zaci.person_id}), {zaci.name_short}, {zaci.class_id}\n")
print("Downloading students in our class")

nasizaci = edupage.get_students()

with open("nasizaci.txt", "w", encoding="utf-8") as f:
    f.write("Meno(ID), Gender, DatumOdSkoly, TypUctu\n")
    f.write(f"----------------------------\n")
    for nasizaci in nasizaci:
        f.write(f"{nasizaci.name}({nasizaci.person_id}) {nasizaci.gender} {nasizaci.in_school_since} {nasizaci.account_type}\n")

print("Downloading teachers")
teachers = edupage.get_teachers()

with open("ucitelia.txt", "w", encoding="utf-8") as f:
    f.write("Meno(ID), Pohlavie, Nástup do školy, Typ")
    for teacher in teachers:
        f.write(f"{teacher.name}({teacher.person_id}), {teacher.gender.name}, {teacher.in_school_since.year}/{teacher.in_school_since.month}/{teacher.in_school_since.day}, {teacher.account_type.name}\n")
print("Downloading notifications")
notifikace = edupage.get_notifications()

with open("notifikace.txt", "w", encoding="utf-8") as f:
    for notifikace in notifikace:
        f.write(f"{notifikace.author}, {notifikace.event_id}, {notifikace.event_type},{notifikace.text}, {notifikace.timestamp}\n------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
print("Downloading your student id")
tvojeid = edupage.get_user_id()

with open("tvojeid.txt", "w", encoding="utf-8") as f:
    f.write(f"{tvojeid}")

print("Done :)")