from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Course, Enrollment, Question, Choice, Submission


# Display the exam page
@login_required
def course_exam(request, course_id):

    course = get_object_or_404(Course, id=course_id)
    questions = Question.objects.filter(course=course)

    context = {
        'course': course,
        'questions': questions,
    }

    return render(
        request,
        'onlinecourseapp/exam_bootstrap.html',
        context
    )


# Submit the exam
@login_required
def submit(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':

        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course
        )

        submission = Submission.objects.create(
            enrollment=enrollment
        )

        selected_ids = request.POST.getlist('choices')

        for choice_id in selected_ids:
            choice = get_object_or_404(
                Choice,
                id=choice_id,
                question__course=course
            )
            submission.choices.add(choice)

        return redirect(
            'show_exam_result',
            course_id=course.id,
            submission_id=submission.id
        )

    return redirect('course_exam', course_id=course.id)


# Display exam results
@login_required
def show_exam_result(request, course_id, submission_id):

    course = get_object_or_404(Course, id=course_id)

    submission = get_object_or_404(
        Submission,
        id=submission_id,
        enrollment__user=request.user,
        enrollment__course=course
    )

    questions = Question.objects.filter(course=course)

    total_grade = sum(
        question.grade for question in questions
    )

    score = 0

    for question in questions:

        selected_ids = submission.choices.filter(
            question=question
        ).values_list('id', flat=True)

        if question.is_get_score(selected_ids):
            score += question.grade

    grade_percentage = (
        round((score / total_grade) * 100, 2)
        if total_grade > 0 else 0
    )

    context = {
        'course': course,
        'submission': submission,
        'questions': questions,
        'score': score,
        'total_grade': total_grade,
        'grade_percentage': grade_percentage,
    }

    return render(
        request,
        'onlinecourseapp/exam_result_bootstrap.html',
        context
    )