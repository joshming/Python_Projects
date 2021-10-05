"""CSC148 Assignment 1

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Misha Schwartz, Mario Badr, Christine Murad, Diane Horton,
Sophia Huynh and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) 2020 Misha Schwartz, Mario Badr, Christine Murad, Diane Horton,
Sophia Huynh and Jaisie Sin

=== Module Description ===

This file contains classes that describe different types of criteria used to
evaluate a group of answers to a survey question.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from survey import Question, Answer


class InvalidAnswerError(Exception):
    """
    Error that should be raised when an answer is invalid for a given question.
    """


class Criterion:
    """
    An abstract class representing a criterion used to evaluate the quality of
    a group based on the group members' answers for a given question.
    """

    def score_answers(self, question: Question, answers: List[Answer]) -> float:
        """
        Return score between 0.0 and 1.0 indicating the quality of the group of
        <answers> to the question <question>.

        Raise InvalidAnswerError if any answer in <answers> is not a valid
        answer to <question>.

        Each implementation of this abstract class will measure quality
        differently.
        """
        raise NotImplementedError


class HomogeneousCriterion(Criterion):
    """
    A criterion used to evaluate the quality of a group based on the group
    members' answers for a given question.

    This criterion gives a higher score to answers that are more similar.
    """

    def score_answers(self, question: Question, answers: List[Answer]) -> float:
        """
        Return a score between 0.0 and 1.0 indicating how similar the answers in
        <answers> are.

        This score is calculated by finding the similarity of every
        combination of two answers in <answers> and taking the average of all
        of these similarity scores.

        If there is only one answer in <answers> and it is valid return 1.0
        since a single answer is always identical to itself.

        Raise InvalidAnswerError if any answer in <answers> is not a valid
        answer to <question>.

        === Precondition ===
        len(answers) > 0
        """
        # if there is only a single answer return 1.0
        if len(answers) == 1 and answers[0].is_valid(question):
            return 1.0

        total = 0.0
        for i in range(len(answers)-1):
            for j in range(i+1, len(answers)):
                # if a answer is invalid an error is raised
                if not answers[i].is_valid(question) \
                        or not answers[j].is_valid(question):
                    raise InvalidAnswerError
                # adding similarity between two answers
                total += question.get_similarity(answers[i], answers[j])
        # total combinations = (n-1) + ... + 3 + 2 + 1
        # = (n)(n+1)//2 - n = (n**2 + n)//2
        n = len(answers)
        score = total/((n**2 + n)/2 - n)  # check Math?
        return score


class HeterogeneousCriterion(HomogeneousCriterion):
    """ A criterion used to evaluate the quality of a group based on the group
    members' answers for a given question.

    This criterion gives a higher score to answers that are more different.
    """

    def score_answers(self, question: Question, answers: List[Answer]) -> float:
        """
        Return a score between 0.0 and 1.0 indicating how similar the answers in
        <answers> are.

        This score is calculated by finding the similarity of every
        combination of two answers in <answers>, finding the average of all
        of these similarity scores, and then subtracting this average from 1.0

        If there is only one answer in <answers> and it is valid, return 0.0
        since a single answer is never identical to itself.

        Raise InvalidAnswerError if any answer in <answers> is not a valid
        answer to <question>.

        === Precondition ===
        len(answers) > 0
        """
        return 1 - HomogeneousCriterion.score_answers(self, question, answers)


class LonelyMemberCriterion(Criterion):
    """ A criterion used to measure the quality of a group of students
    according to the group members' answers to a question. This criterion
    assumes that a group is of high quality if no member of the group gives
    a unique answer to a question.
    """

    def score_answers(self, question: Question, answers: List[Answer]) -> float:
        """
        Return score between 0.0 and 1.0 indicating the quality of the group of
        <answers> to the question <question>.

        The score returned will be zero iff there are any unique answers in
        <answers> and will be 1.0 otherwise.

        An answer is not unique if there is at least one other answer in
        <answers> with identical content.

        Raise InvalidAnswerError if any answer in <answers> is not a valid
        answer to <question>.

        === Precondition ===
        len(answers) > 0
        """
        for i in range(len(answers)):
            # start by assuming answers[i] is unique
            isunique = True

            for j in range(len(answers)):
                # if a answer is invalid an error is raised
                if not answers[i].is_valid(question) \
                        or not answers[j].is_valid(question):
                    raise InvalidAnswerError

                # if there is another answer that is the same as answers[i]
                # (having a score of 1.00)
                if question.get_similarity(answers[i], answers[j]) == 1.0\
                        and i != j:
                    # we know the answer is not unique
                    isunique = False

            # none of the other answers in answers match answers[i]
            if isunique:
                return 0.00

        # now we know all answers are not unique
        return 1.00


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={'extra-imports': ['typing',
                                                  'survey']})
