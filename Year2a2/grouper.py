"""CSC148 Assignment 1

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Misha Schwartz, Mario Badr, Christine Murad, Diane Horton, Sophia Huynh
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) 2020 Misha Schwartz, Mario Badr, Christine Murad, Diane Horton,
Sophia Huynh and Jaisie Sin

=== Module Description ===

This file contains classes that define different algorithms for grouping
students according to chosen criteria and the group members' answers to survey
questions. This file also contain a classe that describes a group of students as
well as a grouping (a group of groups).
"""
from __future__ import annotations
import random
from typing import TYPE_CHECKING, List, Any
from course import sort_students, Course, Student

if TYPE_CHECKING:
    from survey import Survey


def slice_list(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Return a list containing slices of <lst> in order. Each slice is a
    list of size <n> containing the next <n> elements in <lst>.

    The last slice may contain fewer than <n> elements in order to make sure
    that the returned list contains all elements in <lst>.

    === Precondition ===
    n <= len(lst)

    >>> slice_list([3, 4, 6, 2, 3], 2) == [[3, 4], [6, 2], [3]]
    True
    >>> slice_list(['a', 1, 6.0, False], 3) == [['a', 1, 6.0], [False]]
    True
    """
    slices = []
    if n == 0 and not lst:
        return []
    elif n == 0 and lst:
        return lst
    # number of ppl in last group
    else:
        remainder = len(lst) % n

    # adding first few slices
    for i in range(0, len(lst) - remainder, n):
        slices.append(lst[i:i + n])

    # adding last group
    if remainder != 0:
        slices.append(lst[i + n:])

    return slices


def windows(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Return a list containing windows of <lst> in order. Each window is a list
    of size <n> containing the elements with index i through index i+<n> in the
    original list where i is the index of window in the returned list.

    === Precondition ===
    n <= len(lst)

    >>> windows([3, 4, 6, 2, 3], 2) == [[3, 4], [4, 6], [6, 2], [2, 3]]
    True
    >>> windows(['a', 1, 6.0, False], 3) == [['a', 1, 6.0], [1, 6.0, False]]
    True
    """
    windows_lst = []
    # can't go past len(lst) - n since no more items to make window of size n
    for i in range(len(lst) - n + 1):
        windows_lst.append(lst[i:i + n])

    return windows_lst


class Grouper:
    """
    An abstract class representing a grouper used to create a grouping of
    students according to their answers to a survey.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def __init__(self, group_size: int) -> None:
        """
        Initialize a grouper that creates groups of size <group_size>

        === Precondition ===
        group_size > 1
        """
        self.group_size = group_size

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """ Return a grouping for all students in <course> using the questions
        in <survey> to create the grouping.
        """
        raise NotImplementedError


class AlphaGrouper(Grouper):
    """
    A grouper that groups students in a given course according to the
    alphabetical order of their names.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        The first group should contain the students in <course> whose names come
        first when sorted alphabetically, the second group should contain the
        next students in that order, etc.

        All groups in this grouping should have exactly self.group_size members
        except for the last group which may have fewer than self.group_size
        members if that is required to make sure all students in <course> are
        members of a group.

        Hint: the sort_students function might be useful
        """
        # sorted list of students ordered by name
        # course.get_students is a tuple so need to parse to list to sort
        students = sort_students(list(course.get_students()), 'name')

        # slicing students into groups of size self.group_size
        students = slice_list(students, self.group_size)

        # making Grouping to hold groups of students
        grouping = Grouping()
        for student_group in students:
            # adding a group to grouping
            grouping.add_group(Group(student_group))

        return grouping


class RandomGrouper(Grouper):
    """
    A grouper used to create a grouping of students by randomly assigning them
    to groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Students should be assigned to groups randomly.

        All groups in this grouping should have exactly self.group_size members
        except for one group which may have fewer than self.group_size
        members if that is required to make sure all students in <course> are
        members of a group.
        """
        # list of all students sorted by id num.
        # need to convert tuple to list to shuffle
        students = list(course.get_students())
        # randomizing student list
        random.shuffle(students)

        # slicing students into groups of size self.group_size
        students = slice_list(students, self.group_size)

        # creating a Grouping with student slices
        grouping = Grouping()
        for student_group in students:
            # adding a group to grouping
            grouping.add_group(Group(student_group))

        return grouping


class GreedyGrouper(Grouper):
    """
    A grouper used to create a grouping of students according to their
    answers to a survey. This grouper uses a greedy algorithm to create
    groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Starting with a tuple of all students in <course> obtained by calling
        the <course>.get_students() method, create groups of students using the
        following algorithm:

        1. select the first student in the tuple that hasn't already been put
           into a group and put this student in a new group.
        2. select the student in the tuple that hasn't already been put into a
           group that, if added to the new group, would increase the group's
           score the most (or reduce it the least), add that student to the new
           group.
        3. repeat step 2 until there are N students in the new group where N is
           equal to self.group_size.
        4. repeat steps 1-3 until all students have been placed in a group.

        In step 2 above, use the <survey>.score_students method to determine
        the score of each group of students.

        The final group created may have fewer than N members if that is
        required to make sure all students in <course> are members of a group.
        """
        # list of all students sorted by id num.
        students = list(course.get_students())

        grouping = Grouping()

        # loop through until last ppl without groups are left in students
        # there should be (# of students) // (group_size) groups of
        # size self.group_size (notice int div rounds down)
        num_groups = 0
        target = len(students) // self.group_size
        while len(students) > 0 and num_groups < target:
            # start with first student in students
            group = [students[0]]
            # removing first student from student_list
            students.pop(0)

            # helper function for steps 2-3
            # getting group_size members in group list
            self._get_group_members(survey, group, students)

            # now we know that group has enough members now
            # and can be added to grouping
            grouping.add_group(Group(group))

            # number of groups increases by 1
            num_groups += 1

        # dealing with last remaining members
        # (if there are any)
        # for 0 <= x < self.group_size
        # there should be x number of students left in students now
        # put them all in a group and add it to grouping
        if len(students) != 0:
            grouping.add_group(Group(students))

        return grouping

    def _get_group_members(self, survey: Survey,
                           group: list,
                           students: List[Student]) -> None:
        """ helper function for make_groups in GreedyGrouper
        steps 2-3

        2. select the student in the tuple that hasn't already been put into a
           group that, if added to the new group, would increase the group's
           score the most (or reduce it the least), add that student to the new
           group.
        3. repeat step 2 until there are N students in the new group where N is
           equal to self.group_size.

        this also mutates the original student and group lists in make_groups
        """
        while len(group) < self.group_size:
            # start by assuming adding next student produces the best score
            best_score = survey.score_students(group + [students[0]])
            # student that produces best score
            add_student = students[0]

            for student in students:
                curr_score = survey.score_students(group + [student])
                if curr_score > best_score:
                    best_score = curr_score
                    add_student = student

            # now add_student is the student that produces
            # the best score when added
            # so add that student to group
            group.append(add_student)
            # then remove them from the students list
            students.remove(add_student)


class WindowGrouper(Grouper):
    """
    A grouper used to create a grouping of students according to their
    answers to a survey. This grouper uses a window search algorithm to create
    groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Starting with a tuple of all students in <course> obtained by calling
        the <course>.get_students() method, create groups of students using the
        following algorithm:

        1. Get the windows of the list of students who have not already been
           put in a group.
        2. For each window in order, calculate the current window's score as
           well as the score of the next window in the list. If the current
           window's score is greater than or equal to the next window's score,
           make a group out of the students in current window and start again at
           step 1. If the current window is the last window, compare it to the
           first window instead.

        In step 2 above, use the <survey>.score_students to determine the score
        of each window (list of students).

        In step 1 and 2 above, use the windows function to get the windows of
        the list of students.

        If there are any remaining students who have not been put in a group
        after repeating steps 1 and 2 above, put the remaining students into a
        new group.
        """
        # list of all students sorted by id num.
        students = list(course.get_students())

        # if no students in course then return empty grouping
        if len(students) == 0:
            return Grouping()

        grouping = Grouping()

        # loop through until last ppl without group are left in windows
        # there should be (# of students) // (group_size) groups of
        # size self.group_size (notice int div rounds down)
        num_groups = 0
        target = len(students) // self.group_size
        while num_groups < target:

            # calling helper method
            self._find_best_window(survey, students, grouping)

            # number of groups increases by 1
            num_groups += 1

        # dealing with last remaining members
        # (if there are any)
        # for 0 <= x < self.group_size
        # there should be x number of students left in students now
        # put them all in a group and add it to grouping
        if len(students) != 0:
            grouping.add_group(Group(students))

        return grouping

    # helper method
    def _find_best_window(self, survey: Survey, students: List[Student],
                          grouping: Grouping) -> None:
        """helper method for make_grouping in WindowGrouper
        this loops through each window of size self.group_size
        as described in step 2 of make_grouping

        2. For each window in order, calculate the current window's score as
           well as the score of the next window in the list. If the current
           window's score is greater than or equal to the next window's score,
           make a group out of the students in current window and start again at
           step 1. If the current window is the last window, compare it to the
           first window instead.

        also mutates students list in make_grouping to be updated
        without the students that have been added to a group
        """
        # getting new list of windows of size self.group_size
        student_windows = windows(students, self.group_size)

        found_group = False
        i = 0
        # loop stops when a group is added or
        # if i reaches then end of the student_windows list
        while not found_group and i < len(student_windows) - 1:
            # if window[i] has a higher score than next window then
            # the group made from it is added to the grouping
            if (survey.score_students(student_windows[i]) >=
                    survey.score_students(student_windows[i + 1])):
                grouping.add_group(Group(student_windows[i]))
                # removing students in the window from students list
                # since they are now in a group
                for student in student_windows[i]:
                    students.remove(student)
                # we found a group to add
                found_group = True
            i += 1

        # if we reached the end of the student_windows without adding group
        # the last window should be the greatest score
        # this also works if there is only one window
        if not found_group:
            last = len(student_windows) - 1
            grouping.add_group(Group(student_windows[last]))
            # removing students in the window from students list
            # since they are now in a group
            for student in student_windows[last]:
                students.remove(student)


class Group:
    """
    A group of one or more students

    === Private Attributes ===
    _members: a list of unique students in this group

    === Representation Invariants ===
    No two students in _members have the same id
    """

    _members: List[Student]

    def __init__(self, members: List[Student]) -> None:
        """ Initialize a group with members <members> """
        self._members = members

    def __len__(self) -> int:
        """ Return the number of members in this group """
        return len(self._members)

    def __contains__(self, member: Student) -> bool:
        """
        Return True iff this group contains a member with the same id
        as <member>.
        """
        for course_member in self._members:
            if course_member.id == member.id:
                return True
        return False

    def __str__(self) -> str:
        """
        Return a string containing the names of all members in this group
        on a single line.

        You can choose the precise format of this string.
        """
        members_str = ''
        for member in self._members:
            if members_str == '':
                # no comma before first member's name
                members_str += member.name
            else:
                members_str += ', ' + member.name
        return members_str

    def get_members(self) -> List[Student]:
        """ Return a list of members in this group. This list should be a
        shallow copy of the self._members attribute.
        """
        lst = []
        for member in self._members:
            lst.append(member)
        return lst

    # helper function for tests
    def __eq__(self, other: Group) -> bool:
        """"two groupings are equal if they contain the same groups"""
        # groups must be same size
        if len(self) != len(other):
            return False
        for student in self._members:
            # there is a student in self that isn't in the other group
            # then groups are not equal
            if student not in other:
                return False
        # every student in self is also in other
        return True


class Grouping:
    """
    A collection of groups

    === Private Attributes ===
    _groups: a list of Groups

    === Representation Invariants ===
    No group in _groups contains zero members
    No student appears in more than one group in _groups
    """

    _groups: List[Group]

    def __init__(self) -> None:
        """ Initialize a Grouping that contains zero groups """
        self._groups = []

    def __len__(self) -> int:
        """ Return the number of groups in this grouping """
        return len(self._groups)

    def __str__(self) -> str:
        """
        Return a multi-line string that includes the names of all of the members
        of all of the groups in <self>. Each line should contain the names
        of members for a single group.

        You can choose the precise format of this string.
        """
        groups_str = ''
        for group in self._groups:
            if groups_str == '':
                # no /n before first group
                groups_str += str(group)
            else:
                groups_str += '\n' + str(group)
        return groups_str

    def add_group(self, group: Group) -> bool:
        """
        Add <group> to this grouping and return True.

        Iff adding <group> to this grouping would violate a representation
        invariant don't add it and return False instead.
        """
        # if group is empty don't add it
        if len(group) == 0:
            return False

        # string of all the students in all groups in grouping
        students = str(self)
        for student in group.get_members():
            # if a student is already in another group in groupings
            if student.name in students:
                return False
        # now we know representation invariants aren't violated
        # so add the group to grouping
        self._groups.append(group)
        return True

    def get_groups(self) -> List[Group]:
        """ Return a list of all groups in this grouping.
        This list should be a shallow copy of the self._groups
        attribute.
        """
        lst = []
        for group in self._groups:
            lst.append(group)
        return lst

    # helper function for tests
    def __eq__(self, other: Grouping) -> bool:
        """"two groupings are equal if they contain the same groups"""
        # groups must be same size
        if len(self) != len(other):
            return False
        # list of groups in other
        other_groups = other.get_groups()
        for group1 in self._groups:
            # looking for a group1 in other
            found = False
            for group2 in other_groups:
                # if the same group is found in other found is now True
                # there are no duplicate groups from rep invariant
                if group1 == group2:
                    found = True
            # if any group1 in self is not in other grouping is NOT equal
            if not found:
                return False
        # every group in self is also in other
        return True


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={'extra-imports': ['typing',
                                                  'random',
                                                  'survey',
                                                  'course']})
