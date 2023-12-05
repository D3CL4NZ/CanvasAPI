"""
Spring 2023 Canvas final project
UD CS1 Bakery
"""

import sys
from bakery import assert_equal
from bakery_canvas import get_courses, get_submissions
import matplotlib.pyplot as plt
from datetime import datetime

def count_courses(user_token: str) -> int:
    """Counts the user's courses"""
    
    courses = get_courses(user_token)
    count = 0
    
    for course in courses:
        count += 1
    return count

def find_cs1(user_token: str) -> int:
    """
    Produces an integer representing the id of the first Course
    that has the text "CISC1" in their code field. If no Course can be
    found that satisfies the criteria, then return 0 instead.
    """
    
    id = 0 # defaults to 0
    
    courses = get_courses(user_token)
    for course in courses:
        if "CISC1" in course.code:
            id = course.id
    return id

def find_course(user_token:str, course_id:int) -> str:
    """
    returns the full name of the course using the given id.
    If no course is found, then return "no course" instead.
    """
    
    _class = "no course" # "class" is a reserved word in Python, so we use _class instead
    courses = get_courses(user_token)
    for course in courses:
        if course.id == course_id:
            _class = course.name
    return _class

def render_courses(user_token:str) -> str:
    """
    Renders the user_token's courses as a string and returns it.
    """
    
    courses_str = "";
    courses = get_courses(user_token);
    
    for i in courses:
        courses_str += str(i.id) + ": " + i.code + "\n";
    return courses_str;

def execute(command:str, user_token:str, course_id:int) -> int:
    """
    Accepts user command input and executes it.
    """
    
    if command == "course":
        print(render_courses(user_token))
        _input = input("COURSE ID: ")
        _input = int(_input)
        print(find_course(user_token, _input))
        return _input
    elif command == "exit":
        return 0
    elif command == "points":
        print(total_points(user_token, course_id))
        return course_id
    elif command == "comments":
        print(count_comments(user_token, course_id))
        return course_id
    elif command == "graded":
        print(ratio_graded(user_token, course_id))
        return course_id
    elif command == "score_unweighted":
        print(average_score(user_token, course_id))
        return course_id
    elif command == "score":
        print(average_weighted(user_token, course_id))
        return course_id
    elif command == "group":
        group_name = input("GROUP NAME: ")
        print(average_group(user_token, course_id, group_name))
        return course_id
    elif command == "assignment":
        assignment_id = input("ASSIGNMENT ID: ")
        assignment_id = int(assignment_id)
        print(render_assignment(user_token, course_id, assignment_id))
        return course_id
    elif command == "list":
        print(render_all(user_token, course_id))
        return course_id
    elif command == "scores":
        plot_scores(user_token, course_id)
        return course_id
    elif command == "earliness":
        print(plot_earliness(user_token, course_id))
        return course_id
    elif command == "compare":
        print(plot_points(user_token, course_id))
        return course_id
    elif command == "predict":
        print(predict_grades(user_token, course_id))
        return course_id
    elif command == "help":
        print("""
exit > Exit the application
help > List all the commands
course > Change current course
points > Print total points in course
comments > Print how many comments in course
graded > Print ratio of ungraded/graded assignments
score_unweighted > Print average unweighted score
score > Print average weighted score
group > Print average of assignment group, by name
assignment > Print the details of a specific assignment, by ID
list > List all the assignments in the course
scores > Plot the distribution of grades in the course
earliness > Plot the distribution of the days assignments were submitted early
compare > Plot the relationship between assignments' points possible and their weighted points possible
predict > Plot the trends in grades over assignments, showing max ever possible, max still possible, and minimum still possible
""")
        return course_id
    else:
        return course_id
    
def main(user_token:str) -> str:
    """
    Takes a user token and returns course id(s).
    """
    
    curr_id = 0
    courses = get_courses(user_token)
    
    if count_courses(user_token) == 0:
        return "No courses available"
    elif find_cs1(user_token) == 0:
        curr_id = courses[0].id
    else:
        curr_id = find_cs1(user_token)
    while curr_id > 0:
        _command = input("Enter [help], [course] or [exit]: ")
        curr_id = execute(_command, user_token, curr_id)

def total_points(user_token:str, course_id:int) -> int:
    """
    Represents the total points possible in a course (NOT adjusted by group weights).
    """
    
    totalpoints = 0
    
    submissions = get_submissions(user_token, course_id)
    for submission in submissions:
        totalpoints += submission.assignment.points_possible
    return totalpoints

def count_comments(user_token:str, course_id:int) -> int:
    """
    Represents the total number of comments across ALL submissions.
    """
    
    total_comments = 0
    
    submissions = get_submissions(user_token, course_id)
    for submission in submissions:
        for comment in submission.comments:
            total_comments += 1
    return total_comments

def ratio_graded(user_token:str, course_id:int) -> str:
    """
    Produces a string value representing the number of assignments that have been graded compared to the number of total assignments in the course.
    """
    
    total_assignments = 0
    assignments_graded = 0
    
    submissions = get_submissions(user_token, course_id)
    for submission in submissions:
        total_assignments += 1
        if submission.grade != "":
            assignments_graded += 1
    
    return str(assignments_graded) + "/" + str(total_assignments)

def average_score(user_token:str, course_id:int) -> float:
    """
    Produces a float representing the average, unweighted score of all the GRADED assignments in the course.
    """
    
    submissions = get_submissions(user_token, course_id)
    
    total_points_graded = 0
    score_graded = 0
    
    for submission in submissions:
        if submission.grade != "":
            total_points_graded += submission.assignment.points_possible
            score_graded += submission.score
    return score_graded / total_points_graded
    
def average_weighted(user_token:str, course_id:int) -> float:
    """
    Produces a float representing the average, WEIGHTED score of all the graded assignments in the course.
    """
    
    submissions = get_submissions(user_token, course_id)
    
    total_points_graded = 0
    score_graded = 0
    
    for submission in submissions:
        if submission.grade != "":
            total_points_graded += submission.assignment.points_possible * submission.assignment.group.weight
            score_graded += submission.score * submission.assignment.group.weight
    return score_graded / total_points_graded

def average_group(user_token:str, course_id:int, group_name:str) -> float:
    """
    Returns a float representing the average, unweighted grade ratio for all the graded submissions with that group_name.
    """
    
    submissions = get_submissions(user_token, course_id)
    
    total_points_graded = 0
    score_graded = 0
    
    for submission in submissions:
        if submission.grade != "":
            if submission.assignment.group.name.lower() == group_name.lower():
                total_points_graded += submission.assignment.points_possible
                score_graded += submission.score
                
    # Division by zero check
    if total_points_graded == 0.0:
        return 0.0
    return score_graded / total_points_graded

def render_assignment(user_token:str, course_id:int, assignment_id:int) -> str:
    """
    Produces a string representing the assignment and its submission details.
    If the assignment cannot be found in the user's submissions, then return 
    the string "Assignment missing: " followed by the assignment_id.
    """
    
    submission = None
    
    submissions = get_submissions(user_token, course_id)
    for _submission in submissions:
        if _submission.assignment.id == assignment_id:
            submission = _submission
            break
    if submission == None:
        return "Assignment missing: " + str(assignment_id)
    if submission.grade == "":
        return str(assignment_id) + ": " + submission.assignment.name + "\nGroup: " + submission.assignment.group.name + "\nModule: " + submission.assignment.module + "\nGrade: (missing)"
    return str(assignment_id) + ": " + submission.assignment.name + "\nGroup: " + submission.assignment.group.name + "\nModule: " + submission.assignment.module + "\nGrade: " + str(submission.score) + "/" + str(submission.assignment.points_possible) + " (" + submission.grade + ")"

def render_all(user_token:str, course_id:int) -> str:
    """
    Produces a single string that describes all of the submissions in the course.
    """
    
    submissions = get_submissions(user_token, course_id)
    return_string = ""
    
    for submission in submissions:
        if submission.grade == "":
            return_string += str(submission.assignment.id) + ": " + submission.assignment.name + " (ungraded)\n"
        else:
            return_string += str(submission.assignment.id) + ": " + submission.assignment.name + " (graded)\n"
    return return_string.strip()

def plot_scores(user_token:str, course_id:int) -> None:
    """
    Plots the distribution of scores.
    """
    
    submissions = get_submissions(user_token, course_id)
    
    data = []
    
    for submission in submissions:
        if submission.grade != "":
            data.append((submission.score/submission.assignment.points_possible)*100)
    plt.hist(data)
    plt.title("Score Distribution for " + user_token)
    plt.xlabel("Score")
    plt.ylabel("# of Assignments")
    plt.show()

def days_apart(first_date: str, second_date: str) -> int:
    """
    Determines the days between `first` and `second` date.
    Do not modify this function!
    """
    first_date = datetime.strptime(first_date, "%Y-%m-%dT%H:%M:%S%z")
    second_date = datetime.strptime(second_date, "%Y-%m-%dT%H:%M:%S%z")
    difference = second_date - first_date
    return difference.days

def plot_earliness(user_token:str, course_id:int) -> None:
    """
    Plots the lateness (earlyness) distribution for a specified course.
    """
    
    submissions = get_submissions(user_token, course_id)
    
    data = []
    
    for submission in submissions:
        if (submission.assignment.due_at != "") & (submission.submitted_at != ""):
            data.append(days_apart(submission.submitted_at, submission.assignment.due_at))
    plt.hist(data)
    plt.title("Lateness Distribution for " + user_token)
    plt.xlabel("Days Early")
    plt.ylabel("# of Assignments")
    plt.show()

def plot_points(user_token:str, course_id:int) -> None:
    """
    Returns nothing but creates a graph comparing the points possible for each
    assignment with the weighted points possible for that assignment.
    """
    
    submissions = get_submissions(user_token, course_id)
    
    points_possible = []
    total_weighted_points = 0
    weighted_points_possible = []
    
    for submission in submissions:
        points_possible.append(submission.assignment.points_possible)
        total_weighted_points += (submission.assignment.points_possible * submission.assignment.group.weight)
    total_weighted_points /= 100
    for submission in submissions:
        weighted_points_possible.append((submission.assignment.points_possible * submission.assignment.group.weight) / total_weighted_points)
    plt.scatter(points_possible, weighted_points_possible)
    plt.title("Points Possible v. Weighted Points Possible")
    plt.xlabel("Points Possible")
    plt.ylabel("Weighted Points Possible")
    plt.show()

def predict_grades(user_token:str, course_id:int) -> None:
    """
    Produces 3 plots representing the ideal grades for a given assignment.
    """
    
    submissions = get_submissions(user_token, course_id)
    total_weighted_points = 0
    max_scores = []
    max_scores_sum = 0
    max_points = []
    max_points_sum = 0
    min_scores = []
    min_scores_sum = 0
    
    # Total weighted points
    for submission in submissions:
        total_weighted_points += (submission.assignment.points_possible * submission.assignment.group.weight) / 100
    
    # Ideal maximum score (running total)
    for submission in submissions:
        max_scores_sum += (submission.assignment.points_possible * submission.assignment.group.weight) / total_weighted_points
        max_scores.append(max_scores_sum)
    
    # Maximum points (running total)
    for submission in submissions:
        if submission.status == "graded":
            max_points_sum += (submission.score * submission.assignment.group.weight) / total_weighted_points
            max_points.append(max_points_sum)
        else:
            max_points_sum += (submission.assignment.points_possible * submission.assignment.group.weight) / total_weighted_points
            max_points.append(max_points_sum)
    
    # Minimum score (running total)
    for submission in submissions:
        if submission.status == "graded":
            min_scores_sum += (submission.score * submission.assignment.group.weight) / total_weighted_points
            min_scores.append(min_scores_sum)
        else:
            min_scores.append(min_scores_sum)
    
    # The graphs lol
    plt.plot(max_scores)
    plt.plot(max_points)
    plt.plot(min_scores)
    plt.title("Ideal Score Predictions")
    plt.xlabel("Assignments")
    plt.ylabel("Percentage Grade")
    plt.show()

if __name__ == '__main__':
    my_user_token = sys.argv[1]
    main(my_user_token)