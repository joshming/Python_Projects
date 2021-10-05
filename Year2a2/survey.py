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

This file contains classes that describe a survey as well as classes that
described different types of questions that can be asked in a given survey.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Union, Dict, List
from criterion import HomogeneousCriterion, InvalidAnswerError
if TYPE_CHECKING:
    from criterion import Criterion
    from grouper import Grouping
    from course import Student


class Question:
    """ An abstract class representing a question used in a survey

    === Public Attributes ===
    id: the id of this question
    text: the text of this question

    === Private Attributes ===
    _answers: the answers provided for this question with the student id at
                index 0 and their respective answer as index 1.

    === Representation Invariants ===
    text is not the empty string
    """

    id: int
    text: str
    _answers: List[List[int, Answer]]

    def __init__(self, id_: int, text: str) -> None:
        """ Initialize a question with the text <text> """
        self.id = id_
        self.text = text
        self._answers = []

    def __str__(self) -> str:
        """
        Return a string representation of this question that contains both
        the text of this question and a description of all possible answers
        to this question.

        You can choose the precise format of this string.
        """
        raise NotImplementedError

    def validate_answer(self, answer: Answer) -> bool:
        """
        Return True iff <answer> is a valid answer to this question.
        """
        raise NotImplementedError

    def get_similarity(self, answer1: Answer, answer2: Answer) -> float:
        """ Return a float between 0.0 and 1.0 indicating how similar two
        answers are.

        === Precondition ===
        <answer1> and <answer2> are both valid answers to this question
        """
        raise NotImplementedError

    def get_answers_to_question(self) -> List[List[int, Answer]]:
        """"Return a list of answers for a specific question"""
        return self._answers


class MultipleChoiceQuestion(Question):
    """ A question whose answers can be one of several options. A child class
    off Question.

    === Public Attributes ===
    id: the id of this question
    text: the text of this question

    === Private Attributes ===
    _options: list of strings of the answers for the question

    === Representation Invariants ===
    text is not the empty string
    """

    id: int
    text: str
    _options: List[str]

    def __init__(self, id_: int, text: str, options: List[str]) -> None:
        """
        Initialize a question with the text <text> and id <id> and
        possible answers <options>.

        === Precondition ===
        No two elements in <options> are the same string
        <options> contains at least two elements
        """
        Question.__init__(self, id_, text)
        self._options = options

    def __str__(self) -> str:
        """
        Return a string representation of this question including the
        text of the question and a description of the possible answers.

        You can choose the precise format of this string.
        """
        # Set up format to be "<Question>, Possible Answers: "
        question = self.text + ', Possible Answers (Choose one): '

        # Go through all the options for answers
        for i in range(len(self._options)):
            # Add this option to the string question
            if i < (len(self._options) - 1):
                question += self._options[i] + '; '
            else:
                question += self._options[i]

        return question

    def validate_answer(self, answer: Answer) -> bool:
        """
        Return True iff <answer> is a valid answer to this question.

        An answer is valid if its content is one of the possible answers to this
        question.
        """
        # if it is not a string, return False
        if not isinstance(answer.content, str):
            return False
        # Check if the answer is in the options for the question
        elif answer.content in self._options:
            return True
        # Otherwise return False
        return False

    def get_similarity(self, answer1: Answer, answer2: Answer) -> float:
        """
        Return 1.0 iff <answer1>.content and <answer2>.content are equal and
        0.0 otherwise.

        === Precondition ===
        <answer1> and <answer2> are both valid answers to this question.
        """
        if answer1.content == answer2.content:
            return 1.0
        else:
            return 0.0


class NumericQuestion(Question):
    """ A question whose answer can be an integer between some
    minimum and maximum value (inclusive).

    === Public Attributes ===
    id: the id of this question
    text: the text of this question

    === Private Attributes ===
    _min: the minimum value that can be entered
    _max: the maximum value that can be entered

    === Representation Invariants ===
    text is not the empty string
    _min is inclusive
    _max is inclusive
    """

    id: int
    text: str
    _min: int
    _max: int

    def __init__(self, id_: int, text: str, min_: int, max_: int) -> None:
        """
        Initialize a question with id <id_> and text <text> whose possible
        answers can be any integer between <min_> and <max_> (inclusive)

        === Precondition ===
        min_ < max_
        """
        Question.__init__(self, id_, text)
        self._min = min_
        self._max = max_

    def __str__(self) -> str:
        """
        Return a string representation of this question including the
        text of the question and a description of the possible answers.

        You can choose the precise format of this string.
        """
        return f'{self.text}, Possible Answers: The answer must be between ' \
               f'{self._min} and {self._max}'

    def validate_answer(self, answer: Answer) -> bool:
        """
        Return True iff the content of <answer> is an integer between the
        minimum and maximum (inclusive) possible answers to this question.
        """
        if not isinstance(answer.content, int):
            return False
        else:
            if self._min <= answer.content <= self._max:
                return True
        return False

    def get_similarity(self, answer1: Answer, answer2: Answer) -> float:
        """
        Return the similarity between <answer1> and <answer2> over the range
        of possible answers to this question.

        Similarity calculated by:

        1. first find the absolute difference between <answer1>.content and
           <answer2>.content.
        2. divide the value from step 1 by the difference between the maximimum
           and minimum possible answers.
        3. subtract the value from step 2 from 1.0

        Hint: this is the same calculation from the worksheet in lecture!

        For example:
        - Maximum similarity is 1.0 and occurs when <answer1> == <answer2>
        - Minimum similarity is 0.0 and occurs when <answer1> is the minimum
            possible answer and <answer2> is the maximum possible answer
            (or vice versa).

        === Precondition ===
        <answer1> and <answer2> are both valid answers to this question
        """
        # stores the equation presented from steps 1 to 3
        similarity = 1.0 - (abs(answer1.content - answer2.content) /
                            (self._max - self._min))
        return similarity


class YesNoQuestion(Question):
    """ A question whose answer is either yes (represented by True) or
    no (represented by False).

    === Public Attributes ===
    id: the id of this question
    text: the text of this question

    === Representation Invariants ===
    text is not the empty string
    """
    id: int
    text: str

    def __str__(self) -> str:
        """
        Return a string representation of this question including the
        text of the question and a description of the possible answers.

        You can choose the precise format of this string.
        """
        return f'{self.text}, Possible Answers: True; False'

    def validate_answer(self, answer: Answer) -> bool:
        """
        Return True iff <answer>'s content is a boolean.
        """
        return isinstance(answer.content, bool)

    def get_similarity(self, answer1: Answer, answer2: Answer) -> float:
        """
        Return 1.0 iff <answer1>.content is equal to <answer2>.content and
        return 0.0 otherwise.

        === Precondition ===
        <answer1> and <answer2> are both valid answers to this question
        """
        return answer1.content == answer2.content


class CheckboxQuestion(MultipleChoiceQuestion):
    """ A question whose answers can be one or more of several options

    === Public Attributes ===
    id: the id of this question
    text: the text of this question

    === Private Attributes ===
    _options: list of the strings of possible answers to the question

    === Representation Invariants ===
    text is not the empty string
    """

    id: int
    text: str
    _options: List[str]

    def __str__(self) -> str:
        """
        Return a string representation of this question including the
        text of the question and a description of the possible answers.

        You can choose the precise format of this string.
        """
        # Set up format to be "<Question>, Possible Answers: "
        question = self.text + ', Possible Answers (Choose all that apply): '

        # Go through all the options for answers
        for i in range(len(self._options)):
            # Add this option to the string question
            if i < (len(self._options) - 1):
                question += self._options[i] + '; '
            else:
                question += self._options[i]

        return question

    def validate_answer(self, answer: Answer) -> bool:
        """
        Return True iff <answer> is a valid answer to this question.

        An answer is valid iff its content is a non-empty list containing
        unique possible answers to this question.
        """
        if not isinstance(answer.content, str) and not isinstance(answer.content
                                                                  , list):
            return False
        # Check if it is a singular answer from the list
        if isinstance(answer.content, str):
            # Check if that answer is in the list, if so return True
            if answer.content in self._options:
                return True
            else:
                return False
        elif not answer.content:
            return False
        else:
            # Otherwise, loop through all the answers that are provided
            for a in answer.content:
                if answer.content.count(a) > 1:
                    return False
                # If any are not in the options, return False
                if a not in self._options:
                    return False
        # Otherwise return True
        return True

    def get_similarity(self, answer1: Answer, answer2: Answer) -> float:
        """
        Return the similarity between <answer1> and <answer2>.

        Similarity is defined as the ratio between the number of strings that
        are common to both <answer1>.content and <answer2>.content over the
        total number of unique strings that appear in both <answer1>.content and
        <answer2>.content

        For example, if <answer1>.content == ['a', 'b', 'c'] and
        <answer1>.content == ['c', 'b', 'd'], the strings that are common to
        both are ['c', 'b'] and the unique strings that appear in both are
        ['a', 'b', 'c', 'd'].

        === Precondition ===
        <answer1> and <answer2> are both valid answers to this question
        """
        similar = 0.0
        a1_length = len(answer1.content)
        a2_length = len(answer2.content)

        # Check
        if a1_length < a2_length:
            different = a2_length
            # Go through the first set of answers
            for answer in answer1.content:
                # Check if the answer is in the other set of answers
                if answer in answer2.content:
                    # If it is, add to similar
                    similar += 1
                else:
                    # Otherwise, add to different
                    different += 1
        else:
            different = a1_length
            for answer in answer2.content:
                # Check if the answer is in the other set of answers
                if answer in answer1.content:
                    # If it is, add to similar
                    similar += 1
                else:
                    # Otherwise, add to different
                    different += 1
        # Return the quotient of the two if there are different strings
        if different != 1.0:
            return similar / different

        return 1.0


class Answer:
    """ An answer to a question used in a survey

    === Public Attributes ===
    content: an answer to a single question

    === Private Attributes ===
    id: an answer's id number
    """
    content: Union[str, bool, int, List[str]]
    _id: int

    def __init__(self,
                 content: Union[str, bool, int, List[Union[str]]]) -> None:
        """Initialize an answer with content <content>"""
        self.content = content
        self._id = 0

    def _make_id(self, question: Question) -> None:
        """Set an answer to its corresponding question <question>"""
        self._id = question.id

    def is_valid(self, question: Question) -> bool:
        """Return True iff self.content is a valid answer to <question>"""
        if question.validate_answer(self):
            return True
        else:
            raise InvalidAnswerError


class Survey:
    """
    A survey containing questions as well as criteria and weights used to
    evaluate the quality of a group based on their answers to the survey
    questions.

    === Private Attributes ===
    _questions: a dictionary mapping each question's id to the question itself
    _criteria: a dictionary mapping a question's id to its associated criterion
    _weights: a dictionary mapping a question's id to a weight; an integer
              representing the importance of this criteria.
    _default_criterion: a criterion to use to evaluate a question if the
              question does not have an associated criterion in _criteria
    _default_weight: a weight to use to evaluate a question if the
              question does not have an associated weight in _weights
    _Answers: a dictionary with the question's id as a key, and a list of lists
              the student's id number and answer for that question.

    === Representation Invariants ===
    No two questions on this survey have the same id
    Each key in _questions equals the id attribute of its value
    Each key in _criteria occurs as a key in _questions
    Each key in _weights occurs as a key in _questions
    Each value in _weights is greater than 0
    _default_weight > 0
    """

    _questions: Dict[int, Question]
    _criteria: Dict[int, Criterion]
    _weights: Dict[int, int]
    _default_criterion: Criterion
    _default_weight: int

    def __init__(self, questions: List[Question]) -> None:
        """
        Initialize a new survey that contains every question in <questions>.
        This new survey should use a HomogeneousCriterion as a default criterion
        and should use 1 as a default weight.
        """
        self._questions = {}
        for question in questions:
            if question.id not in self._questions:
                self._questions[question.id] = question
            else:
                self._questions[question.id] = question
        self._criteria = {}
        self._weights = {}
        self._default_criterion = HomogeneousCriterion()
        self._default_weight = 1

    def __len__(self) -> int:
        """ Return the number of questions in this survey """
        return len(self._questions)

    def __contains__(self, question: Question) -> bool:
        """
        Return True iff there is a question in this survey with the same
        id as <question>.
        """
        return question.id in self._questions

    def __str__(self) -> str:
        """
        Return a string containing the string representation of all
        questions in this survey

        You can choose the precise format of this string.
        """
        count = 1
        questions = ''
        for q_id in self._questions:
            questions += str(count) + '. ' + str(self._questions[q_id]) + '; '
            count += 1
        questions = questions.strip()
        return questions

    def get_questions(self) -> List[Question]:
        """ Return a list of all questions in this survey """
        question_list = []

        for q_id in self._questions:
            question_list.append(self._questions[q_id])

        return question_list

    def _get_criterion(self, question: Question) -> Criterion:
        """
        Return the criterion associated with <question> in this survey.

        Iff <question>.id does not appear in self._criteria, return the default
        criterion for this survey instead.

        === Precondition ===
        <question>.id occurs in this survey
        """
        if question.id not in self._criteria:
            return self._default_criterion
        else:
            return self._criteria[question.id]

    def _get_weight(self, question: Question) -> int:
        """
        Return the weight associated with <question> in this survey.

        Iff <question>.id does not appear in self._weights, return the default
        weight for this survey instead.

        === Precondition ===
        <question>.id occurs in this survey
        """
        if question.id in self._weights:
            return self._weights[question.id]
        else:
            return self._default_weight

    def set_weight(self, weight: int, question: Question) -> bool:
        """
        Set the weight associated with <question> to <weight> and return True.

        If <question>.id does not occur in this survey, do not set the <weight>
        and return False instead.
        """
        if question.id in self._questions:
            self._weights[question.id] = weight
            return True
        else:
            return False

    def set_criterion(self, criterion: Criterion, question: Question) -> bool:
        """
        Set the criterion associated with <question> to <criterion> and return
        True.

        If <question>.id does not occur in this survey, do not set the <weight>
        and return False instead.
        """
        if question.id not in self._questions:
            return False
        else:
            self._criteria[question.id] = criterion
            return True

    def score_students(self, students: List[Student]) -> float:
        """
        Return a quality score for <students> calculated based on their answers
        to the questions in this survey, and the associated criterion and weight
        for each question .

        This score is determined using the following algorithm:

        1. For each question in <self>, find its associated criterion, weight,
           and <students> answers to this question. Use the score_answers method
           for this criterion to calculate a quality score. Multiply this
           quality score by the associated weight.
        2. Find the average of all quality scores from step 1.

        If an InvalidAnswerError would be raised by calling this method, or if
        there are no questions in <self>, this method should return zero.

        === Precondition ===
        All students in <students> have an answer to all questions in this
            survey
        """
        score = 0.0
        questions = self.get_questions()
        num_of_scores = len(questions)
        if not questions:  # Make sure it is not an empty list of questions
            return 0.0

        # Go through all the questions in this survey
        for question in questions:
            # set up the criterion and weight. Retrieve the answers to the
            # questions
            criterion = self._get_criterion(question)
            weight = self._get_weight(question)
            # Loop through the student list
            s_answer = []
            for student in students:
                # See if the student has a valid answer
                try:
                    student.has_answer(question)
                # If not, return 0
                except InvalidAnswerError:
                    return 0.0

                temp = student.get_answer(question)
                s_answer.append(temp)
            score += (criterion.score_answers(question, s_answer) * weight)
        return score / num_of_scores

    def score_grouping(self, grouping: Grouping) -> float:
        """ Return a score for <grouping> calculated based on the answers of
        each student in each group in <grouping> to the questions in <self>.

        If there are no groups in <grouping> this score is 0.0. Otherwise, this
        score is determined using the following algorithm:

        1. For each group in <grouping>, get the score for the members of this
           group calculated based on their answers to the questions in this
           survey.
        2. Return the average of all the scores calculated in step 1.

        === Precondition ===
        All students in the groups in <grouping> have an answer to all questions
            in this survey
        """
        scores = []
        total = 0.0
        l_group = grouping.get_groups()

        if not l_group:
            return 0.0

        # Go through the list of groups
        for group in l_group:
            # Get a list of the students in the group
            l_students = group.get_members()
            # For the list of students, get its score, and append it to the
            # list of scores
            score = self.score_students(l_students)
            scores.append(score)

        # Total up all the scores
        for s in scores:
            total += s
        # Return the average of the scores
        return total / len(scores)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={'extra-imports': ['typing',
                                                  'criterion',
                                                  'course',
                                                  'grouper']})
