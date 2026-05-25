from rest_framework import serializers
from .models import ExamSchedule, ExamResult, MCQQuestion, ExamAttempt, StudentAnswer, AdmitCard


class ExamScheduleSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = ExamSchedule
        fields = [
            'id', 'college', 'name', 'exam_type', 'subject', 'subject_name',
            'department', 'department_name', 'semester', 'section',
            'exam_date', 'start_time', 'end_time', 'duration_minutes',
            'room_number', 'max_marks', 'passing_marks', 'instructions',
            'is_active', 'question_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']

    def get_question_count(self, obj):
        return obj.questions.filter(is_deleted=False).count()


class MCQQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQQuestion
        fields = [
            'id', 'exam', 'question_text', 'option_a', 'option_b',
            'option_c', 'option_d', 'marks', 'negative_marks', 'order',
        ]
        read_only_fields = ['id']


class MCQQuestionWithAnswerSerializer(serializers.ModelSerializer):
    """Used after exam submission — shows correct answer."""
    class Meta:
        model = MCQQuestion
        fields = [
            'id', 'question_text', 'option_a', 'option_b',
            'option_c', 'option_d', 'correct_option', 'marks',
            'negative_marks', 'explanation', 'order',
        ]


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ['id', 'question', 'selected_option', 'is_correct', 'marks_awarded']
        read_only_fields = ['id', 'is_correct', 'marks_awarded']


class ExamAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttempt
        fields = [
            'id', 'exam', 'student', 'started_at', 'submitted_at',
            'status', 'tab_switch_count', 'question_order',
        ]
        read_only_fields = ['id', 'started_at', 'submitted_at', 'question_order']


class ExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    rank = serializers.SerializerMethodField()

    class Meta:
        model = ExamResult
        fields = [
            'id', 'exam', 'exam_name', 'student', 'student_name',
            'student_enrollment', 'marks_obtained', 'grade', 'percentage',
            'status', 'remarks', 'evaluated_by', 'evaluated_at', 'rank',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'percentage', 'created_at', 'updated_at']

    def get_rank(self, obj):
        if not obj.percentage:
            return None
        rank = ExamResult.objects.filter(
            exam=obj.exam,
            is_deleted=False,
            percentage__gt=obj.percentage,
        ).count() + 1
        return rank


class AdmitCardSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    exam_date = serializers.DateField(source='exam.exam_date', read_only=True)
    exam_time = serializers.TimeField(source='exam.start_time', read_only=True)
    room_number = serializers.CharField(source='exam.room_number', read_only=True)

    class Meta:
        model = AdmitCard
        fields = [
            'id', 'exam', 'exam_name', 'exam_date', 'exam_time',
            'room_number', 'student', 'student_name', 'student_enrollment',
            'roll_number', 'seat_number', 'is_issued', 'issued_at',
        ]
        read_only_fields = ['id', 'issued_at']


class ScorecardSerializer(serializers.Serializer):
    """Instant scorecard after exam submission."""
    exam_name = serializers.CharField()
    subject_name = serializers.CharField()
    total_questions = serializers.IntegerField()
    attempted = serializers.IntegerField()
    correct = serializers.IntegerField()
    incorrect = serializers.IntegerField()
    skipped = serializers.IntegerField()
    marks_obtained = serializers.DecimalField(max_digits=6, decimal_places=2)
    max_marks = serializers.IntegerField()
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    status = serializers.CharField()
    rank = serializers.IntegerField(allow_null=True)
    total_students = serializers.IntegerField()
    answers = StudentAnswerSerializer(many=True)
