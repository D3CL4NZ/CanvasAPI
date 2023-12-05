"""
Bakery Helper Library - Canvas Requests
Version: 1.0.0
Author: acbart@udel.edu

Changelog:
* 11/01/2022 at 4:44pm - Initial Version Started
* 11/08/2022 at 12:20pm - Courses without submissions now return an empty list instead of an error
* 10/16/2023 at 3:03pm - Fixed unnecessary print, adjusted order of query parameters
"""
from dataclasses import dataclass
import requests

try:
    import requests_cache
    requests_cache.install_cache('bakery_canvas_cache', allowable_methods=('GET', 'POST'),
                                 ignored_parameters=[])
except ImportError:
    print("Warning! Please install requests-cache using the Tools menu (Manage Packages)")

CANVAS_API_URL = "https://udel.instructure.com/api/graphql"
HEADER = {'User-Agent': 'Bakery Canvas library for educational purposes'}
COURSE_QUERY = """
query CourseQuery {
  allCourses {
    _id
    courseCode
    name
    imageUrl
    term {
      startAt
      endAt
    }
  }
}

"""
SUBMISSION_QUERY = """
query Submissions($courseId: ID!) {
  course(id: $courseId) {
    assignmentsConnection {
      nodes {
        submissionsConnection {
          nodes {
            missing
            _id
            attempt
            body
            excused
            grade
            gradedAt
            commentsConnection {
              nodes {
                _id
                createdAt
                author {
                  name
                }
                comment
              }
            }
            score
            submittedAt
            late
            state
          }
        }
        name
        assignmentGroup {
          groupWeight
          name
          _id
        }
        _id
        createdAt
        description
        dueAt(applyOverrides: true)
        gradingType
        lockAt(applyOverrides: true)
        modules {
          name
          position
          _id
        }
        pointsPossible
        unlockAt
      }
    }
  }
}
"""

"""
Bonus questions:
* Rubric information
* 
"""

@dataclass
class Course:
    """
    Information about a given Course in Canvas.
    
    Attributes:
        id: The unique ID for this course.
        code: A short relatively human-friendly code name for this course.
        name: The full title of this course.
        url: The image URL for this course.
        start_at: The date when this course begins, in ISO format.
        end_at: The date when this course ends, in ISO format.
    """
    id: int
    code: str
    name: str
    url: str
    start_at: str
    end_at: str


@dataclass
class Group:
    """
    Information about the group (category) that this assignment belongs to.

    Attributes:
        id: The unique ID of this assignment group on Canvas.
        name: The name of this assignment group as seen on Canvas.
        weight: How much assignments in this group are weighted compared to other groups.
    """
    id: int
    name: str
    weight: int


@dataclass
class Assignment:
    """
    Information about the assignment itself.

    Attributes:
        id: The unique ID of the assignment on Canvas.
        name: The name of the assignment as seen on Canvas.
        description: The assignment instructions.
        points_possible: The total possible number of points you can earn on this assignment.
        due_at: When this assignment is due for you, in ISO format.
        locked_at: When this assignment is locked for you, in ISO format.
        unlocked_at: When this assignment is available for you, in ISO format.
        created_at: The date when this assignment was created, in ISO format.
        module: The name of the module that this assignment belongs to.
        group: The information about the group that this assignment belongs to.
    """
    id: int
    name: str
    description: str
    points_possible: int
    due_at: str
    locked_at: str
    unlocked_at: str
    created_at: str
    module: str
    group: Group


@dataclass
class Comment:
    """
    Comments posted by staff and students on a given submission.

    Attributes:
        id: The unique ID of this comment.
        text: The actual text of the comment
        author: The name of who wrote the comment
        created_at: When the comment was posted.
    """
    id: int
    text: str
    author: str
    created_at: str


@dataclass
class Submission:
    """
    Information about a student's submission for a given assignment.

    Attributes:
        id: The unique ID of this submission
        body: The content of this submission.
        assignment: The information about this submission's assignment.
        comments: The comments made on this submission.
        score: The numerical points earned on this assignment
        grade: The corresponding letter grade for this assignment
        attempts: The number of times this submission was attempted.
        status: The current workflow state of the submission (e.g., 'graded').
        missing: Whether or not there is a submission for this assignment.
        excused: Whether or not this assignment has been excused.
        late: Whether or not the submission is late.
        submitted_at: When this assignment was submitted, in ISO format.
        graded_at: When the assignment was graded
    """
    id: int
    body: str
    assignment: Assignment
    comments: list[Comment]
    score: float
    grade: str
    attempts: int
    status: str
    missing: bool
    excused: bool
    late: bool
    submitted_at: str
    graded_at: str


def get_courses(user_token: str) -> list[Course]:
    """
    Get all the courses available to this user.
    """
    request_arguments = dict(access_token=user_token, query=COURSE_QUERY)
    r = requests.post(CANVAS_API_URL, request_arguments, headers=HEADER)
    return create_courses(r.json(), user_token)

def get_submissions(user_token: str, course_id: int) -> list[Submission]:
    """
    For a given course, retrieve the submissions related to that course.
    """
    request_arguments = dict(query=SUBMISSION_QUERY, access_token=user_token)
    request_arguments['variables[courseId]'] = course_id
    s = requests_cache.patcher.get_cache()
    r = requests.post(CANVAS_API_URL, request_arguments, headers=HEADER)
    return create_submissions(r.json(), user_token, course_id)


#############################################################################
# Helper Functions

def create_courses(raw: dict, user_token: str) -> list[Course]:
    """
    Create a list of Courses from the raw dictionary data previously retrieved.
    """
    if 'data' not in raw:
        error = ("\n" + raw['error']) if 'error' in raw else ''
        raise ValueError("Fields are unexpectedly missing from the response returned by the server. "
                         "Check your token!\n"
                         f" user_token={user_token}" + error)
    raw_courses = raw['data']['allCourses']
    return [Course(parse_int(raw_course.get('_id')),
                   parse_str(raw_course.get('courseCode')),
                   parse_str(raw_course.get('name')),
                   parse_str(raw_course.get('imageUrl')),
                   parse_str(raw_course.get('term', {}).get('startAt')),
                   parse_str(raw_course.get('term', {}).get('endAt'))
                   )
            for raw_course in raw_courses]


def create_submissions(raw: dict, user_token: str, course_id: int) -> list[Submission]:
    """
    Create a list of Submissions from the raw dictionary data previously retrieved.
    """
    if 'data' not in raw:
        error = ("\n" + raw['error']) if 'error' in raw else ''
        raise ValueError("Fields are unexpectedly missing from the response returned by the server. "
                         "Check your course_id and token!\n"
                         f" course_id={course_id}, user_token={user_token}" + error)
    if not raw['data']['course']:
        return []
        #raise ValueError("The course returned by the server was empty. "
        #                 "Check your course_id and token!\n"
        #                 f" course_id={course_id}, user_token={user_token}")
    raw_nodes = raw['data']['course']['assignmentsConnection']['nodes']
    return [create_submission(raw) for raw in raw_nodes]

def create_submission(raw_assignment: dict) -> Submission:
    """
    Create one individual Submission from the raw assignment data.
    """
    raw_modules = raw_assignment.get('modules')
    raw_group = raw_assignment.get('assignmentGroup')
    assignment = Assignment(parse_int(raw_assignment.get('_id')),
                            parse_str(raw_assignment.get('name')),
                            parse_str(raw_assignment.get('description')),
                            parse_int(raw_assignment.get('pointsPossible')),
                            parse_str(raw_assignment.get('dueAt')),
                            parse_str(raw_assignment.get('lockAt')),
                            parse_str(raw_assignment.get('unlockAt')),
                            parse_str(raw_assignment.get('createdAt')),
                            parse_str(raw_modules[0].get('name')) if raw_modules else '',
                            Group(parse_int(raw_group.get('_id')),
                                  parse_str(raw_group.get('name')),
                                  parse_int(raw_group.get('groupWeight')))
                            )
    raw_submission = raw_assignment.get('submissionsConnection', {}).get('nodes', [])
    if raw_submission:
        raw_submission = raw_submission[0]
        raw_comments = raw_submission.get('commentsConnection', {}).get('nodes', [])
        submission = Submission(parse_int(raw_submission.get('_id')),
                                parse_str(raw_submission.get('body')),
                                assignment,
                                [Comment(parse_int(raw_comment.get('_id')),
                                         parse_str(raw_comment.get('comment')),
                                         parse_str(raw_comment.get('author', {}).get('name', '')),
                                         parse_str(raw_comment.get('createdAt'))
                                         )
                                 for raw_comment in raw_comments],
                                parse_float(raw_submission.get('score')),
                                parse_str(raw_submission.get('grade')),
                                parse_int(raw_submission.get('attempt')),
                                parse_str(raw_submission.get('state')),
                                parse_boolean(raw_submission.get('missing')),
                                parse_boolean(raw_submission.get('excused')),
                                parse_boolean(raw_submission.get('late')),
                                parse_str(raw_submission.get('submittedAt')),
                                parse_str(raw_submission.get('gradedAt'))
                                )
    else:
        submission = Submission(0, '', assignment, [], 0, '', 0, 'missing',
                                True, False, False, '', '')
    return submission


def parse_int(value, default=0):
    """
    Attempt to cast *value* into an integer, returning *default* if it fails.
    """
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def parse_float(value, default=0.0):
    """
    Attempt to cast *value* into a float, returning *default* if it fails.
    """
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def parse_boolean(value, default=False):
    """
    Attempt to cast *value* into a bool, returning *default* if it fails.
    """
    if value is None:
        return default
    try:
        return bool(value)
    except ValueError:
        return default


def parse_str(value, default=''):
    """
    Make sure that the returned result is definitely a string.
    """
    if value is None:
        return default
    try:
        return str(value)
    except ValueError:
        return default


if __name__ == '__main__':
    TOKEN = "jeff"
    COURSE_ID = 679554
    print("Warning! You should not run this file directly. You should import it!")
    from pprint import pprint
    pprint(get_courses(TOKEN))
    pprint(get_submissions(TOKEN, COURSE_ID)[0])

