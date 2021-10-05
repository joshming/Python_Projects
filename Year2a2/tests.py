"""Tests for assignment 1"""
from course import Student, Course
from survey import Survey, YesNoQuestion, Answer,\
    MultipleChoiceQuestion, NumericQuestion, CheckboxQuestion
from criterion import Criterion, HomogeneousCriterion, HeterogeneousCriterion, \
    LonelyMemberCriterion
from grouper import Group, Grouping, slice_list, windows,\
    AlphaGrouper, RandomGrouper, GreedyGrouper, WindowGrouper
import pytest
from typing import List, Set, FrozenSet

# we don't need to write tests for initializers
# we won't be marked off for style errors for pyTA for tests


class TestStudent:
    """tests for Student class"""
    def test_str(self) -> None:
        """test for __str__ in Student"""
        s = Student(1, "Joe")
        assert str(s) == "Joe"

    def test_has_answer(self) -> None:
        """test for has_answer in Student"""
        s = Student(1, 'David')
        q = YesNoQuestion(1, 'Are you David?')
        expected = False
        assert s.has_answer(q) == expected
        a = Answer(True)
        s.set_answer(q, a)
        assert s.has_answer(q)

    def test_get_answer(self) -> None:
        """test for get_answer"""
        s = Student(1, 'David')
        q = YesNoQuestion(1, 'Are you David?')
        a = Answer(True)
        s.set_answer(q, a)
        assert s.get_answer(q) == a

    def test_get_answer_empty(self) -> None:
        """test for when there are no answers for the question"""
        s = Student(1, 'David')
        q = YesNoQuestion(1, 'Are you alive')
        expected = None
        assert s.get_answer(q) == expected

    def test_no_answers(self) -> None:
        """"test all_answered when none have answered"""
        s = Student(1, 'David')
        q = YesNoQuestion(1, 'random')
        c = Course('Class')
        c.enroll_students([s])
        u = Survey([q])
        assert c.all_answered(u) is False

    def test_set_answer(self) -> None:
        """test for has_answer in Student"""
        s = Student(1, 'David')
        q = YesNoQuestion(1, 'Are you David?')
        a = Answer(True)
        s.set_answer(q, a)
        actual = q.get_answers_to_question()
        assert actual == [[1, a]]


class TestCourse:
    """tests for Course class"""
    def test_enroll_students_(self) -> None:
        """test for enroll_students in Course where students are not
        already in course"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Jo")
        s3 = Student(3, "J")
        students = [s1, s2, s3]
        c = Course("class")
        c.enroll_students(students)
        assert s1 in c.students
        assert s2 in c.students
        assert s3 in c.students

    def test_enroll_students_already_enrolled(self) -> None:
        """test for enroll_students in Course a student is already enrolled"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Jo")
        s3 = Student(3, "J")
        students = [s1, s2, s3]
        c = Course("class")
        c.enroll_students([s2])
        assert c.students == [s2]
        # this should not enroll since s2 is already in c.students
        c.enroll_students(students)
        assert c.students == [s2]

    def test_all_answered(self) -> None:
        """test all_answered basic"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Jo")
        students = [s1, s2]
        c = Course("class")
        c.enroll_students(students)
        q1 = YesNoQuestion(1, 'Are you in the right class?')
        q2 = MultipleChoiceQuestion(1, 'How old are you', ['fourteen',
                                                           'fifteen', 'one'])
        questions = [q1, q2]
        survey = Survey(questions)
        assert c.all_answered(survey) is False
        a1 = Answer(True)
        a2 = Answer('fourteen')
        s1.set_answer(q1, a1)
        s1.set_answer(q2, a2)
        s2.set_answer(q1, a1)
        s2.set_answer(q2, a2)
        assert c.all_answered(survey) is True

    def test_get_students(self) -> None:
        """test get_students"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Jo")
        students = [s1, s2]
        c = Course("class")
        c.enroll_students(students)
        assert c.get_students() == (s1, s2)

    def test_empty_get_students(self) -> None:
        """Test a course with an empty set of students"""
        c = Course('Class')
        c.enroll_students([])
        assert c.get_students() == ()


class TestGroup:
    """tests for Group class"""
    def test_len_empty(self) -> None:
        """test for __len__ on a empty group"""
        g = Group([])
        assert len(g) == 0

    def test_len_three_students(self) -> None:
        """test for __len__ on a group of 3 students"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Jo")
        s3 = Student(3, "J")
        g = Group([s1, s2, s3])
        assert len(g) == 3

    def test_contains_empty(self) -> None:
        """test for __contains__ on a empty group"""
        s1 = Student(1, "Joe")
        g = Group([])
        assert s1 not in g

    def test_contains_three_students(self) -> None:
        """test for __contains__ on a group of 2 students"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Jo")
        s3 = Student(3, "J")
        g = Group([s1, s2])
        assert s1 in g
        assert s2 in g
        assert s3 not in g

    def test_str(self) -> None:
        """test for _str_ on group of 3"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Sara")
        s3 = Student(3, "Ben")
        g = Group([s1, s2, s3])
        expected = str(g)
        assert "Joe" in expected
        assert "Sara" in expected
        assert "Ben" in expected

    def test_get_members_empty(self) -> None:
        """test for get_members on a empty group"""
        g = Group([])
        assert g.get_members() == []
        # checking that the shallow copy does not have same id
        # don't want aliasing
        assert g.get_members() is not g._members

    def test_get_members_three_students(self) -> None:
        """test for get_members on a group of 2 students"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Sara")
        s3 = Student(3, "Ben")
        g = Group([s1, s2])
        expected = g.get_members()
        assert s1 in expected
        assert s2 in expected
        assert s3 not in expected
        # checking that the shallow copy does not have same id
        # don't want aliasing
        assert expected is not g._members

    def test_eq(self) -> None:
        """test for __eq__ for Group (helper method for tests)"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Sara")
        s3 = Student(3, "Ben")
        g1 = Group([])
        g2 = Group([])
        g3 = Group([s1])
        g4 = Group([s1, s2, s3])
        g5 = Group([s2, s1, s3])
        # empty group should be equal
        assert g1 == g2
        assert g4 == g5
        assert g1 != g3
        assert g3 != g4


class TestGrouping:
    """tests for Grouping class"""
    def test_len(self) -> None:
        """test for __len__ on Grouping"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Sara")
        s3 = Student(3, "Ben")
        g1 = Group([s1])
        g2 = Group([s2])
        g3 = Group([s3])
        grouping = Grouping()
        # making sure that empty grouping has len 0
        assert len(grouping) == 0
        # adding the groups to grouping
        assert grouping.add_group(g1)  # checking group has been added
        assert len(grouping) == 1  # checking len
        assert grouping.add_group(g2)
        assert len(grouping) == 2
        assert grouping.add_group(g3)
        assert len(grouping) == 3

    def test_str(self) -> None:
        """test for __str__ on a Grouping"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Sara")
        s3 = Student(3, "Ben")
        g1 = Group([s1, s2])
        g2 = Group([s3])
        grouping = Grouping()

        # checking group has been added
        assert grouping.add_group(g1)
        assert grouping.add_group(g2)

        # checking that students's names are in str(grouping)
        assert "Joe" in str(grouping)
        assert "Sara" in str(grouping)
        assert "Ben" in str(grouping)

    def test_add_group(self) -> None:
        """test for add group on a Grouping"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Sara")
        s3 = Student(3, "Ben")
        g1 = Group([s1, s2])
        g2 = Group([s2, s3])
        g_empty = Group([])
        grouping = Grouping()
        # adding Group g1 of two students
        assert grouping.add_group(g1)
        # make sure that Group has been added
        assert g1 in grouping._groups

        # make sure that you can't add empty Groups
        assert not grouping.add_group(g_empty)
        # make sure that Group has NOT been added
        assert g_empty not in grouping._groups

        # making sure that you can't add group with student
        # already in another group
        assert not grouping.add_group(g2)
        # make sure that Group has NOT been added
        assert g2 not in grouping._groups

    def test_get_groups(self) -> None:
        """test for get_groups on a Grouping"""
        grouping = Grouping()
        assert grouping.get_groups() == []
        # checking that the shallow copy does not have same id
        # don't want aliasing
        assert grouping.get_groups() is not grouping._groups

        # now testing for a Grouping of two groups
        s1 = Student(1, "Joe")
        s2 = Student(2, "Sara")
        s3 = Student(3, "Ben")
        g1 = Group([s1])
        g2 = Group([s2])
        g3 = Group([s3])
        # checking groups has been added
        assert grouping.add_group(g1)
        assert grouping.add_group(g2)
        # checking that groups are in shallow copy
        expected = grouping.get_groups()
        assert g1 in expected
        assert g2 in expected
        assert g3 not in expected # did not add group 3 to grouping
        # checking that the shallow copy does not have same id
        assert expected is not grouping._groups

    def test_eq(self) -> None:
        """test for __eq__ for Grouping (helper method for tests)"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Sara")
        g1 = Group([s1])
        g2 = Group([s2])
        g3 = Group([s1, s2])
        grouping1 = Grouping()
        grouping2 = Grouping()
        grouping3 = Grouping()
        # empty groupings should equal
        assert grouping1 == grouping2
        grouping1.add_group(g1)
        grouping2.add_group(g1)
        assert grouping1 == grouping2
        assert grouping1 != grouping3
        grouping1.add_group(g2)
        grouping2.add_group(g2)
        grouping3.add_group(g3)
        assert grouping1 == grouping2
        assert grouping1 != grouping3


def test_slice_list() -> None:
    """"test for slice_list in grouper.py"""
    lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert slice_list(lst, 10) == [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
    assert slice_list(lst, 3) == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    assert slice_list(lst, 4) == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
    assert slice_list(lst, 5) == [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
    assert slice_list(lst, 7) == [[0, 1, 2, 3, 4, 5, 6], [7, 8, 9]]
    # empty list should return empty list
    assert slice_list([], 1) == []
    assert slice_list([], 23) == []


def test_windows() -> None:
    """"test for windows in grouper.py"""
    lst = [0, 1, 2, 3, 4, 5, 6]
    assert windows(lst, 7) == [[0, 1, 2, 3, 4, 5, 6]]
    assert windows(lst, 4) == \
           [[0, 1, 2, 3], [1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]]
    assert windows(lst, 3) == \
           [[0, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6]]
    # empty list should return empty list
    assert windows([], 1) == []
    assert windows([], 23) == []


class TestGrouper:
    """tests for Grouping class"""
    def test_alpha_grouper_make_grouping(self) -> None:
        """"test for make_grouping method in Alpha Grouper class"""
        s1 = Student(1, "Joe")
        s2 = Student(2, "Sara")
        s3 = Student(3, "Ben")
        s4 = Student(4, "Jess")
        s5 = Student(5, "Sam")
        course = Course("example course")
        # enrolling students into course
        course.enroll_students([s1, s2, s3, s4, s5])
        # alphabetical order of students is
        # Ben, Jess, Joe, Sam, Sara -> s3, s4, s1, s5, s2
        group_1 = Grouping() # grouping with group size 1
        group_1.add_group(Group([s3]))
        group_1.add_group(Group([s4]))
        group_1.add_group(Group([s1]))
        group_1.add_group(Group([s5]))
        group_1.add_group(Group([s2]))

        group_2 = Grouping() # grouping with group size 2
        group_2.add_group(Group([s3, s4]))
        group_2.add_group(Group([s1, s5]))
        group_2.add_group(Group([s2]))

        group_3 = Grouping() # grouping with group size 3
        group_3.add_group(Group([s3, s4, s1]))
        group_3.add_group(Group([s5, s2]))

        survey = Survey([])

        assert AlphaGrouper(1).make_grouping(course, survey) == group_1
        assert AlphaGrouper(2).make_grouping(course, survey) == group_2
        assert AlphaGrouper(3).make_grouping(course, survey) == group_3

    def test_random_grouper_make_grouping(self) -> None:
        """"test for make_grouping method in Random class"""
        s1 = Student(1, "s1")
        s2 = Student(2, "s2")
        s3 = Student(3, "s3")
        s4 = Student(4, "s4")
        s5 = Student(5, "s5")
        course = Course("example course")
        # enrolling students into course
        course.enroll_students([s1, s2, s3, s4, s5])
        survey = Survey([])

        # group size 1, 2 , 3, 5 accordingly
        grouping1 = RandomGrouper(1).make_grouping(course, survey)
        grouping2 = RandomGrouper(2).make_grouping(course, survey)
        grouping3 = RandomGrouper(3).make_grouping(course, survey)
        grouping5 = RandomGrouper(5).make_grouping(course, survey)

        # checking the number of groups in the grouping are correct
        assert len(grouping1) == 5
        assert len(grouping2) == 3
        assert len(grouping3) == 2
        assert len(grouping5) == 1

        # checking the number of members in each group is in correct range
        for group in grouping1.get_groups():
            assert len(group) == 1
        for group in grouping2.get_groups():
            assert len(group) == 2 or len(group) == 1
        for group in grouping3.get_groups():
            assert len(group) == 3 or len(group) == 2
        for group in grouping5.get_groups():
            assert len(group) == 5

        # checking the uniqueness of all members in the grouping
        new_grouping1 = Grouping()
        for group in grouping1.get_groups():
            # using add_group to check for member uniqueness
            # if a member in one group is in another then
            # add_group would return False
            assert new_grouping1.add_group(group)

        new_grouping2 = Grouping()
        for group in grouping2.get_groups():
            assert new_grouping2.add_group(group)

        new_grouping3 = Grouping()
        for group in grouping3.get_groups():
            assert new_grouping3.add_group(group)

        new_grouping5 = Grouping()
        for group in grouping5.get_groups():
            assert new_grouping5.add_group(group)

    def test_greedy_grouper_make_grouping(self) -> None:
        """"test for make_grouping method in GreedyGrouper class"""
        s1 = Student(1, "s1")
        s2 = Student(2, "s2")
        s3 = Student(3, "s3")
        s4 = Student(4, "s4")
        s5 = Student(5, "s5")
        s6 = Student(6, "s6")
        s7 = Student(7, "s7")
        s8 = Student(8, "s8")

        q1 = MultipleChoiceQuestion(1, 'question 1', ['a1', 'a2', 'a3'])
        a1 = Answer('a1')
        a2 = Answer('a2')
        a3 = Answer('a3')

        survey = Survey([q1])

        # setting student's answers
        # s1, s2, s7 and s8  have same answers
        # s3, s4, s6 have the same answers
        # s5 is alone with their answer
        s1.set_answer(q1, a1)
        s2.set_answer(q1, a1)
        s3.set_answer(q1, a2)
        s4.set_answer(q1, a2)
        s5.set_answer(q1, a3)
        s6.set_answer(q1, a2)
        s7.set_answer(q1, a1)
        s8.set_answer(q1, a2)

        course1 = Course("course 1 student")
        course2 = Course("course 2 students")
        course3 = Course("course 3 students")
        course4 = Course("course 4 students")
        course5 = Course("course 5 students")
        course6 = Course("course 6 students")
        # enrolling students into course
        course1.enroll_students([s1])
        course2.enroll_students([s1, s2])
        course3.enroll_students([s1, s7, s3])
        course4.enroll_students([s1, s2, s3, s7])
        course5.enroll_students([s1, s3, s4, s5, s6])
        course6.enroll_students([s1, s3, s5, s6, s7, s8])

        # groups of size 1
        expected1 = Grouping()
        expected1.add_group(Group([s1]))
        assert GreedyGrouper(1).make_grouping(course1, survey) == expected1
        expected1.add_group(Group([s2]))
        assert GreedyGrouper(1).make_grouping(course2, survey) == expected1

        # groups of size 2
        expected2 = Grouping()
        expected2.add_group(Group([s1, s2]))
        assert GreedyGrouper(2).make_grouping(course2, survey) == expected2

        expected3 = Grouping()
        expected3.add_group(Group([s1, s7]))
        expected3.add_group(Group([s3]))
        assert GreedyGrouper(2).make_grouping(course3, survey) == expected3

        expected5 = Grouping()
        expected5.add_group(Group([s1, s3]))
        expected5.add_group(Group([s4, s6]))
        expected5.add_group(Group([s5]))
        assert GreedyGrouper(2).make_grouping(course5, survey) == expected5

        # groups of size 3
        expected4 = Grouping()
        expected4.add_group(Group([s1, s2, s7]))
        expected4.add_group(Group([s3]))
        assert GreedyGrouper(3).make_grouping(course4, survey) == expected4

        expected6 = Grouping()
        expected6.add_group(Group([s1, s7, s3]))
        expected6.add_group(Group([s5, s6, s8]))
        assert GreedyGrouper(3).make_grouping(course6, survey) == expected6

    def test_greedy_grouper_get_group_members(self) -> None:
        """tests for helper method _get_group_members in GreedyGrouper"""
        s1 = Student(1, "s1")
        s2 = Student(2, "s2")
        s3 = Student(3, "s3")
        s4 = Student(4, "s4")
        s5 = Student(5, "s5")
        # note: the tests aren't putting the students into the order
        # with id number but the usage by make_grouping
        # will organize the students in order of id

        q1 = MultipleChoiceQuestion(1, 'question 1', ['a1', 'a2', 'a3'])
        a1 = Answer('a1')
        a2 = Answer('a2')
        a3 = Answer('a3')

        survey = Survey([q1])

        # setting student's answers
        s1.set_answer(q1, a1)
        s2.set_answer(q1, a1)
        s3.set_answer(q1, a2)
        s4.set_answer(q1, a1)
        s5.set_answer(q1, a3)

        # only one student
        group_list = [s1]
        GreedyGrouper(1)._get_group_members(survey, group_list, [])
        assert group_list == [s1]

        # [s1, s2] have best score
        group_list = [s1]
        students = [s3, s2]
        GreedyGrouper(2)._get_group_members(survey, group_list, students)
        assert group_list == [s1, s2]
        assert students == [s3]

        # same score for [s1, s2] and [s1, s5]
        # just takes first pair
        group_list = [s1]
        students = [s5, s3]
        GreedyGrouper(2)._get_group_members(survey, group_list, students)
        assert group_list == [s1, s5]
        assert students == [s3]

        # group size 3
        group_list = [s1]
        students = [s5, s3, s2]
        GreedyGrouper(3)._get_group_members(survey, group_list, students)
        assert group_list == [s1, s2, s5]
        assert students == [s3]

        group_list = [s1]
        students = [s2, s3, s4]
        GreedyGrouper(3)._get_group_members(survey, group_list, students)
        assert group_list == [s1, s2, s4]
        assert students == [s3]

    def test_window_grouper_make_grouping(self) -> None:
        """"test for make_grouping method in WindowGrouper class"""
        s1 = Student(1, "s1")
        s2 = Student(2, "s2")
        s3 = Student(3, "s3")
        s4 = Student(4, "s4")
        s5 = Student(5, "s5")
        s6 = Student(6, "s6")
        s7 = Student(7, "s7")
        s8 = Student(8, "s8")

        q1 = MultipleChoiceQuestion(1, 'question 1', ['a1', 'a2', 'a3'])
        a1 = Answer('a1')
        a2 = Answer('a2')
        a3 = Answer('a3')

        survey = Survey([q1])

        # setting student's answers
        # s1, s2, s7 and s8  have same answers
        # s3, s4, s6 have the same answers
        # s5 is alone with their answer
        s1.set_answer(q1, a1)
        s2.set_answer(q1, a1)
        s3.set_answer(q1, a2)
        s4.set_answer(q1, a2)
        s5.set_answer(q1, a3)
        s6.set_answer(q1, a2)
        s7.set_answer(q1, a1)
        s8.set_answer(q1, a2)

        course1 = Course("course 1 student")
        course2 = Course("course 2 students")
        course3 = Course("course 3 students")
        course4 = Course("course 4 students")
        course5 = Course("course 5 students")
        course6 = Course("course 6 students")
        # enrolling students into course
        course1.enroll_students([s1])
        course2.enroll_students([s1, s2])
        course3.enroll_students([s1, s7, s2])
        course4.enroll_students([s2, s5, s1, s7])
        course5.enroll_students([s1, s3, s4, s5, s6])
        course6.enroll_students([s1, s3, s5, s6, s7, s8])

        # groups of size 1
        expected1 = Grouping()
        expected1.add_group(Group([s1]))
        assert WindowGrouper(1).make_grouping(course1, survey) == expected1
        expected1.add_group(Group([s2]))
        assert WindowGrouper(1).make_grouping(course2, survey) == expected1

        # groups of size 2
        expected2 = Grouping()
        expected2.add_group(Group([s1, s2]))
        assert WindowGrouper(2).make_grouping(course2, survey) == expected2
        expected2.add_group(Group([s7]))
        # s1, s2 ,s7 all have same answers
        assert WindowGrouper(2).make_grouping(course3, survey) == expected2

        expected3 = Grouping()
        # all different answers - same score of 0.0
        expected3.add_group(Group([s1, s2]))
        expected3.add_group(Group([s5, s7]))
        assert WindowGrouper(2).make_grouping(course4, survey) == expected3

        expected4 = Grouping()
        expected4.add_group(Group([s3, s4]))
        expected4.add_group(Group([s1, s5]))
        expected4.add_group(Group([s6]))
        assert WindowGrouper(2).make_grouping(course5, survey) == expected4

        # groups of size 3
        expected5 = Grouping()
        expected5.add_group(Group([s3, s5, s6]))
        expected5.add_group(Group([s1, s7, s8]))
        assert WindowGrouper(3).make_grouping(course6, survey) == expected5

    def test_window_grouper_find_best_window(self) -> None:
        """test for helper method _find_best_window in WindowGrouper"""
        s1 = Student(1, "s1")
        s2 = Student(2, "s2")
        s3 = Student(3, "s3")
        s4 = Student(4, "s4")
        s5 = Student(5, "s5")
        # note: the tests aren't putting the students into the order
        # with id number but the usage by make_grouping
        # will organize the students in order of id

        q1 = MultipleChoiceQuestion(1, 'question 1', ['a1', 'a2', 'a3'])
        a1 = Answer('a1')
        a2 = Answer('a2')
        a3 = Answer('a3')

        survey = Survey([q1])

        # setting student's answers
        s1.set_answer(q1, a1)
        s2.set_answer(q1, a1)
        s3.set_answer(q1, a2)
        s4.set_answer(q1, a2)
        s5.set_answer(q1, a3)

        # only one member should be grouped by self.
        grouping1 = Grouping()
        WindowGrouper(1)._find_best_window(survey, [s1], grouping1)
        expected1 = Grouping()
        expected1.add_group(Group([s1]))
        assert grouping1 == expected1

        # only one window
        grouping2 = Grouping()
        WindowGrouper(2)._find_best_window(survey, [s1, s2], grouping2)
        expected2 = Grouping()
        expected2.add_group(Group([s1, s2]))
        assert grouping2 == expected2

        # last window with best score
        grouping3 = Grouping()
        WindowGrouper(2)._find_best_window(survey, [s1, s3, s4], grouping3)
        expected3 = Grouping()
        expected3.add_group(Group([s3, s4]))
        assert grouping3 == expected3

        # window in middle with best score
        # first window has lower as second window
        # second window has better score than third window
        # so second window should be added
        grouping4 = Grouping()
        WindowGrouper(2)._find_best_window(survey,
                                           [s3, s2, s1, s4],
                                           grouping4)
        expected4 = Grouping()
        expected4.add_group(Group([s2, s1]))
        assert grouping4 == expected4

        # window in middle with best score
        # but first window has same score as second window
        # so first window should be added
        grouping5 = Grouping()
        WindowGrouper(2)._find_best_window(survey,
                                           [s1, s5, s3, s4, s2],
                                           grouping5)
        expected5 = Grouping()
        expected5.add_group(Group([s1, s5]))
        assert grouping5 == expected5

        # last window has the same score as first window
        grouping6 = Grouping()
        WindowGrouper(2)._find_best_window(survey, [s1, s3, s2], grouping6)
        expected6 = Grouping()
        expected6.add_group(Group([s1, s3]))
        assert grouping6 == expected6


class TestQuestion:
    """tests for Question class"""
    def test_str_method(self) -> None:
        """test if each string method works"""
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2'])
        q2 = YesNoQuestion(2, 'random')
        q3 = NumericQuestion(3, 'random', 1, 10)
        q4 = CheckboxQuestion(4, 'random', ['a1', 'a2'])
        assert q1.__str__() == 'random, Possible Answers (Choose one): a1; a2'
        assert q2.__str__() == 'random, Possible Answers: True; False'
        assert q3.__str__() == 'random, Possible Answers: The answer must be ' \
                               'between 1 and 10'
        assert q4.__str__() == 'random, Possible Answers (Choose all ' \
                               'that apply): a1; a2'

    def test_validate_answer(self) -> None:
        """Test if all validation methods for each child class works"""
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        q3 = NumericQuestion(3, 'random', 1, 10)
        q4 = CheckboxQuestion(4, 'random', ['a1', 'a2'])
        a1 = Answer('a1')
        fake_a1 = Answer('a4')
        a2 = Answer(False)
        fake_a2 = Answer('True')
        a3 = Answer(5)
        fake_a3 = Answer(11)
        a4 = Answer('a2')
        fake_a4 = Answer('a3')
        assert q1.validate_answer(a1)
        assert not q1.validate_answer(fake_a1)
        assert q2.validate_answer(a2)
        assert not q2.validate_answer(fake_a2)
        assert q3.validate_answer(a3)
        assert not q3.validate_answer(fake_a3)
        assert q4.validate_answer(a4)
        assert not q4.validate_answer(fake_a4)

    def test_validity_empty_answer(self) -> None:
        """test the validity of empty answers"""
        q1 = CheckboxQuestion(1, 'random', ['a1', 'a2', 'a3'])
        a = Answer([])
        assert not q1.validate_answer(a)
        q2 = MultipleChoiceQuestion(2, 'random', ['a1', 'a2'])
        a2 = Answer('')
        assert not q2.validate_answer(a2)

    def test_validate_more_answers(self) -> None:
        """test the validity of an answer with correct options except one"""
        q = CheckboxQuestion(1, 'random', ['a', 'b', 'c'])
        a = Answer(['a', 'b', 'c', 'd'])
        assert not q.validate_answer(a)

    def test_get_similarity(self) -> None:
        """Test the similarity method for each child"""
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        q3 = NumericQuestion(3, 'random', 1, 10)
        q4 = CheckboxQuestion(4, 'random', ['a1', 'a2'])
        a1 = Answer('a1')
        a1_2 = Answer('a2')
        a2 = Answer(True)
        a2_2 = Answer(True)
        a3 = Answer(4)
        a3_2 = Answer(6)
        a4 = Answer(['a1'])
        a4_2 = Answer(['a1', 'a2'])
        assert q1.get_similarity(a1, a1_2) == 0.0
        assert q2.get_similarity(a2, a2_2) == 1.0
        assert q3.get_similarity(a3, a3_2) == 0.7777777777777778
        assert q4.get_similarity(a4, a4_2) == 0.5
        assert q4.get_similarity(a4_2, a4_2) == 1.0

    def test_get_answers(self) -> None:
        """Test get_answers_to_question for access into private attribute
        Answers
        """
        s = Student(1, 'David')
        q = YesNoQuestion(1, 'Are you David?')
        a = Answer(True)
        s.set_answer(q, a)
        assert q.get_answers_to_question() == [[1, a]]


class TestAnswer:
    """tests for Answer class"""
    def test_make_id(self) -> None:
        q = YesNoQuestion(1, 'random')
        a = Answer(True)
        a._make_id(q)
        assert a._id == 1

    def test_is_valid(self) -> None:
        """test if the answer is valid"""
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        q3 = NumericQuestion(3, 'random', 1, 10)
        q4 = CheckboxQuestion(4, 'random', ['a1', 'a2'])
        a1 = Answer('a1')
        a2 = Answer(True)
        a3 = Answer(5)
        a4 = Answer(['a1'])
        assert a1.is_valid(q1)
        assert a2.is_valid(q2)
        assert a3.is_valid(q3)
        assert a4.is_valid(q4)


class TestSurvey:
    """tests for Survey class"""
    def test_len_method(self) -> None:
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        assert survey.__len__() == 2

    def test_contains_method(self) -> None:
        """test if survey does contain the question"""
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        assert survey.__contains__(q1)

    def test_string_method(self) -> None:
        """test if survey is properly formatted as a string"""
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        assert survey.__str__() == '1. random, Possible Answers (Choose one): '\
                                   'a1; a2; a3; 2. random, Possible Answers: ' \
                                   'True; False;'

    def test_get_questions(self) -> None:
        """test to get all questions of the survey"""
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        assert survey.get_questions() == [q1, q2]

    def test_default_get_criterion(self) -> None:
        """test for default criterion"""
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        assert survey._get_criterion(q1) == survey._default_criterion

    def test_default_weight(self) -> None:
        """test for default weight"""
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        assert survey._get_weight(q1) == 1

    def test_set_criterion(self) -> None:
        """test if criteria is properly set"""
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        survey.set_criterion(HeterogeneousCriterion(), q1)
        # Check if the criteria matches
        assert survey._get_criterion(q1) == survey._criteria[q1.id]

    def test_set_weight(self) -> None:
        """test if weight is properly set"""
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        survey.set_weight(2, q1)
        assert survey._get_weight(q1) == 2

    def test_score_students(self) -> None:
        """test for scoring students"""
        s1 = Student(1, 'David')
        s2 = Student(2, 'Diane')
        s_list = [s1, s2]
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        a1 = Answer('a1')
        a2 = Answer(True)
        s1.set_answer(q1, a1)
        s1.set_answer(q2, a2)
        s2.set_answer(q1, a1)
        s2.set_answer(q2, a2)
        assert survey.score_students(s_list) == 1.0
        survey.set_criterion(LonelyMemberCriterion(), q1)
        survey.set_criterion(LonelyMemberCriterion(), q2)
        survey.set_weight(1, q1)
        survey.set_weight(1, q2)
        assert survey.score_students(s_list) == 1.0

    def test_score_empty_survey(self) -> None:
        """test when there are no questions in the survey"""
        s = Student(1, 'David')
        s2 = Student(2, 'Diane')

        survey = Survey([])
        assert survey.score_students([s, s2]) == 0.0

    def test_score_grouping(self) -> None:
        """test score_grouping for standard group"""
        s1 = Student(1, 'David')
        s2 = Student(2, 'Diane')
        s_list = [s1, s2]
        s3 = Student(3, 'Jen')
        s4 = Student(4, 'Dan')
        s_list2 = [s3, s4]
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        g = Group(s_list)
        g2 = Group(s_list2)
        g_i = Grouping()
        g_i.add_group(g)
        g_i.add_group(g2)
        a1 = Answer('a1')
        a2 = Answer(True)
        a1_2 = Answer('a2')
        a2_2 = Answer(False)
        s1.set_answer(q1, a1)
        s1.set_answer(q2, a2)
        s2.set_answer(q1, a1_2)
        s2.set_answer(q2, a2_2)
        s3.set_answer(q1, a1)
        s4.set_answer(q1, a1)
        s3.set_answer(q2, a2)
        s4.set_answer(q2, a2)
        survey.set_criterion(LonelyMemberCriterion(), q1)
        survey.set_criterion(LonelyMemberCriterion(), q2)
        survey.set_weight(1, q1)
        survey.set_weight(1, q2)
        assert survey.score_grouping(g_i) == 0.5

    def test_empty_score_grouping(self) -> None:
        """test empty grouping score"""
        grouping = Grouping()
        q = YesNoQuestion(1, 'hello')
        survey = Survey([q])
        assert survey.score_grouping(grouping) == 0.0

    def test_score_grouping_using_groupers(self) -> None:
        """test various scores for various groups"""
        s1 = Student(1, "s1")
        s2 = Student(2, "s2")
        s3 = Student(3, "s3")
        s4 = Student(4, "s4")
        s5 = Student(5, "s5")
        s6 = Student(6, "s6")
        s7 = Student(7, "s7")
        s8 = Student(8, "s8")

        q1 = MultipleChoiceQuestion(1, 'question 1', ['a1', 'a2', 'a3'])
        a1 = Answer('a1')
        a2 = Answer('a2')
        a3 = Answer('a3')

        s1.set_answer(q1, a1)
        s2.set_answer(q1, a2)
        s3.set_answer(q1, a3)
        s4.set_answer(q1, a1)
        s5.set_answer(q1, a2)
        s6.set_answer(q1, a3)
        s7.set_answer(q1, a1)
        s8.set_answer(q1, a3)

        c1 = Course('Course1')
        c2 = Course('Course2')
        c3 = Course('Course3')

        c1.enroll_students([s1, s4, s7])
        c2.enroll_students([s1, s2, s3, s4, s5, s6, s7])
        c3.enroll_students([s1, s2, s4, s6, s7])

        survey = Survey([q1])
        survey.set_criterion(LonelyMemberCriterion(), q1)
        survey.set_weight(1, q1)

        grouping1 = GreedyGrouper(2).make_grouping(c1, survey)
        grouping2 = GreedyGrouper(3).make_grouping(c2, survey)
        grouping3 = GreedyGrouper(2).make_grouping(c3, survey)

        assert survey.score_grouping(grouping1) == 0.5
        assert survey.score_grouping(grouping2) == 0.3333333333333333
        assert survey.score_grouping(grouping3) == 0.3333333333333333


class TestCriterion:
    """tests for Criterion class"""
    def test_homogeneous_criterion(self) -> None:
        """test for make grouping HomogeneousCriterion"""
        q1 = MultipleChoiceQuestion(1, 'question 1', ['a1', 'a2', 'a3'])
        a1 = Answer('a1')
        a2 = Answer('a2')
        a3 = Answer('a3')

        # one answer
        assert HomogeneousCriterion().score_answers(q1, [a1]) == 1.0
        # only different answers
        assert HomogeneousCriterion().score_answers(q1, [a1, a2, a3]) == 0.0
        # all same answers
        assert HomogeneousCriterion().score_answers(q1, [a1, a1, a1]) == 1.0
        # 2/(3+2+1) comparisons
        assert round(HomogeneousCriterion()
                     .score_answers(q1, [a1, a1, a2, a2]), 3) == 0.333
        assert round(HomogeneousCriterion()
                     .score_answers(q1, [a1, a2, a1, a2]), 3) == 0.333
        # 1/(2+1) comparisons = 1/3
        assert round(HomogeneousCriterion()
                     .score_answers(q1, [a1, a1, a2]), 3) == 0.333
        # 4/(5+4+3+2+1) comparisons = 4/15
        assert round(HomogeneousCriterion()
                     .score_answers(q1, [a1, a1, a2, a2, a2, a3]), 3) == 0.267
        # 11/(6+5+4+3+2+1) comparisons = 11/21
        assert round(HomogeneousCriterion()
                     .score_answers(q1, [a3, a1, a3, a3, a1, a3, a3]), 3)\
               == 0.524

    def test_heterogeneous_criterion(self) -> None:
        """test for make grouping HeterogeneousCriterion"""
        q1 = MultipleChoiceQuestion(1, 'question 1', ['a1', 'a2', 'a3'])
        a1 = Answer('a1')
        a2 = Answer('a2')
        a3 = Answer('a3')

        # one answer
        assert HeterogeneousCriterion().score_answers(q1, [a1]) == 0.0
        # only different answers
        assert HeterogeneousCriterion().score_answers(q1, [a1, a2, a3]) == 1.0
        # all same answers
        assert HeterogeneousCriterion().score_answers(q1, [a1, a1, a1]) == 0.0
        # 4/(3+2+1) comparisons
        assert round(HeterogeneousCriterion()
                     .score_answers(q1, [a1, a1, a2, a2]), 3) == 0.667
        assert round(HeterogeneousCriterion()
                     .score_answers(q1, [a1, a2, a1, a2]), 3) == 0.667
        # 2/(2+1) comparisons
        assert round(HeterogeneousCriterion()
                     .score_answers(q1, [a1, a1, a2]), 3) == 0.667
        # 11/(5+4+3+2+1) comparisons = 11/15
        assert round(HeterogeneousCriterion()
                     .score_answers(q1, [a1, a1, a2, a2, a2, a3]), 3) == 0.733
        # 10/(6+5+4+3+2+1) comparisons = 10/21
        assert round(HeterogeneousCriterion()
                     .score_answers(q1, [a3, a1, a3, a3, a1, a3, a3]), 3) \
               == 0.476

    def test_lonely_member_criterion(self) -> None:
        """test for make grouping LonelyMemberCriterion"""
        q1 = MultipleChoiceQuestion(1, 'question 1', ['a1', 'a2', 'a3'])
        a1 = Answer('a1')
        a2 = Answer('a2')
        a3 = Answer('a3')

        # Sam is alone in her answer for q1
        assert LonelyMemberCriterion()\
                   .score_answers(q1, [a1, a2, a1, a2, a3]) == 0.0
        # no unique answers
        assert LonelyMemberCriterion()\
                   .score_answers(q1, [a1, a1, a2, a2]) == 1.0
        assert LonelyMemberCriterion()\
                   .score_answers(q1, [a1, a1, a1]) == 1.0
        assert LonelyMemberCriterion()\
                   .score_answers(q1, [a1, a2, a1, a2]) == 1.0

        # one answer is unique
        assert LonelyMemberCriterion()\
                   .score_answers(q1, [a1]) == 0.0

        # some unique some not unique answers
        assert LonelyMemberCriterion().score_answers(q1, [a1, a1, a1, a3]) \
               == 0.0


class TestGreedyGrouper:
    def test_make_grouping(self) -> None:
        s1 = Student(1, 'David')
        s2 = Student(2, 'Diane')
        s3 = Student(3, 'Jen')
        s4 = Student(4, 'Dan')
        s_list = [s1, s2, s3, s4]
        c = Course('Class')
        c.enroll_students(s_list)
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        a1 = Answer('a1')
        a1_2 = Answer('a2')
        a2 = Answer(True)
        a2_2 = Answer(False)
        s1.set_answer(q1, a1)
        s1.set_answer(q2, a2)
        s2.set_answer(q1, a1)
        s2.set_answer(q2, a2)
        s3.set_answer(q1, a1_2)
        s3.set_answer(q2, a2_2)
        s4.set_answer(q1, a1_2)
        s4.set_answer(q2, a2_2)
        survey.set_criterion(LonelyMemberCriterion(), q1)
        survey.set_criterion(LonelyMemberCriterion(), q2)
        survey.set_weight(1, q1)
        survey.set_weight(1, q2)
        g = GreedyGrouper(2)
        grouping = g.make_grouping(c, survey)
        groups = grouping.get_groups()
        expected = [Group([s1, s2]), Group([s3, s4])]
        assert groups == expected

    def test_make_grouping_rig1(self) -> None:
        s1 = Student(1, 'David')
        s2 = Student(2, 'Diane')
        s3 = Student(3, 'Jen')
        s4 = Student(4, 'Dan')
        s5 = Student(5, 'Mario')
        s_list = [s1, s2, s3, s4, s5]
        c = Course('Class')
        c.enroll_students(s_list)
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        a1 = Answer('a1')
        a1_2 = Answer('a2')
        a2 = Answer(True)
        a2_2 = Answer(False)
        s1.set_answer(q1, a1)
        s1.set_answer(q2, a2)
        s2.set_answer(q1, a1)
        s2.set_answer(q2, a2)
        s3.set_answer(q1, a1_2)
        s3.set_answer(q2, a2_2)
        s4.set_answer(q1, a1_2)
        s4.set_answer(q2, a2_2)
        s5.set_answer(q1, a1)
        s5.set_answer(q2, a2)
        survey.set_criterion(LonelyMemberCriterion(), q1)
        survey.set_criterion(LonelyMemberCriterion(), q2)
        survey.set_weight(1, q1)
        survey.set_weight(1, q2)
        g = GreedyGrouper(2)
        grouping = g.make_grouping(c, survey)
        groups = grouping.get_groups()
        expected = [Group([s1, s2]), Group([s3, s4]), Group([s5])]
        assert groups == expected

    def test_gg_make_grouping_rig2(self) -> None:
        s1 = Student(1, 'David')
        s2 = Student(2, 'Diane')
        s3 = Student(3, 'Jen')
        s4 = Student(4, 'Dan')
        s5 = Student(5, 'Mario')
        s_list = [s1, s2, s3, s4, s5]
        c = Course('Class')
        c.enroll_students(s_list)
        q1 = MultipleChoiceQuestion(1, 'random', ['a1', 'a2', 'a3'])
        q2 = YesNoQuestion(2, 'random')
        survey = Survey([q1, q2])
        a1 = Answer('a1')
        a1_2 = Answer('a2')
        a2 = Answer(True)
        a2_2 = Answer(False)
        s1.set_answer(q1, a1)
        s1.set_answer(q2, a2)
        s2.set_answer(q1, a1)
        s2.set_answer(q2, a2)
        s3.set_answer(q1, a1_2)
        s3.set_answer(q2, a2_2)
        s4.set_answer(q1, a1_2)
        s4.set_answer(q2, a2_2)
        s5.set_answer(q1, a1)
        s5.set_answer(q2, a2)
        survey.set_criterion(LonelyMemberCriterion(), q1)
        survey.set_criterion(LonelyMemberCriterion(), q2)
        survey.set_weight(1, q1)
        survey.set_weight(1, q2)
        g = GreedyGrouper(2)
        grouping = g.make_grouping(c, survey)
        groups = grouping.get_groups()
        expected = [Group([s1, s2]), Group([s3, s4]), Group([s5])]
        assert groups == expected


if __name__ == '__main__':
    pytest.main(['tests.py'])

    # style checker
    # import python_ta
    # python_ta.check_all(config={'extra-imports': ['typing',
    #                                               'survey',
    #                                               'course',
    #                                               'criterion',
    #                                               'grouper']})
