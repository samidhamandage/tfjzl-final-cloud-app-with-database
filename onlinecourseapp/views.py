from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment, Question, Choice, Submission


@login_required
def course_exam(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    questions = Question.objects.filter(course=course)

    context = {
        'course': course,
        'questions': questions,
    }

    return render(request, 'onlinecourseapp/exam_bootstrap.html', context)


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course
        )

        submission = Submission.objects.create(enrollment=enrollment)

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

    total_score = 0
    possible_score = 0
    question_results = []

    for question in questions:
        possible_score += question.grade

        selected_ids = list(
            submission.choices.filter(
                question=question
            ).values_list('id', flat=True)
        )

        is_correct = question.is_get_score(selected_ids)

        grade = question.grade if is_correct else 0
        total_score += grade

        question_results.append({
            'question': question,
            'selected_ids': selected_ids,
            'grade': grade,
            'possible': question.grade,
            'is_correct': is_correct,
        })

    grade = (
        round((total_score / possible_score) * 100, 2)
        if possible_score > 0 else 0
    )

    context = {
        'course': course,
        'submission': submission,
        'questions': questions,
        'question_results': question_results,
        'total_score': total_score,
        'possible_score': possible_score,
        'score': total_score,
        'total_grade': possible_score,
        'grade': grade,
        'grade_percentage': grade,
    }

    return render(
        request,
        'onlinecourseapp/exam_result_bootstrap.html',
        context
    )