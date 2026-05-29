from rest_framework import serializers

from .models import FeePayment, FeeStructure, StudentFeeAccount


class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = [
            'id',
            'college',
            'name',
            'description',
            'department',
            'branch',
            'semester',
            'academic_year',
            'tuition_fee',
            'exam_fee',
            'library_fee',
            'lab_fee',
            'sports_fee',
            'hostel_fee',
            'transport_fee',
            'other_fee',
            'total_fee',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'total_fee', 'created_at', 'updated_at']


class FeePaymentSerializer(serializers.ModelSerializer):
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)

    class Meta:
        model = FeePayment
        fields = [
            'id',
            'college',
            'student',
            'student_enrollment',
            'fee_structure',
            'amount_due',
            'amount_paid',
            'amount_remaining',
            'discount',
            'fine',
            'due_date',
            'paid_date',
            'status',
            'payment_method',
            'transaction_id',
            'receipt_number',
            'remarks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'amount_remaining', 'status', 'created_at', 'updated_at']


class FeePaymentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = [
            'student',
            'fee_structure',
            'amount_due',
            'amount_paid',
            'discount',
            'fine',
            'due_date',
            'paid_date',
            'payment_method',
            'transaction_id',
            'receipt_number',
            'remarks',
        ]

    def validate(self, attrs):
        student = attrs['student']
        fee_structure = attrs['fee_structure']
        if student.college_id != fee_structure.college_id:
            raise serializers.ValidationError('Student and fee structure must belong to the same college.')
        attrs['college'] = student.college
        return attrs


class StudentFeeAccountSerializer(serializers.ModelSerializer):
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)

    class Meta:
        model = StudentFeeAccount
        fields = [
            'id',
            'college',
            'student',
            'student_enrollment',
            'fee_structure',
            'total_due',
            'total_paid',
            'total_discount',
            'balance',
            'status',
            'due_date',
            'created_at',
        ]
        read_only_fields = fields
