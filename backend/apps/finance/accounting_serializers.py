from rest_framework import serializers

from .models import Budget, ChartOfAccount, JournalEntry, JournalLine, Payslip, PayrollRun, PaymentOrder, SalaryStructure, Vendor


class ChartOfAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartOfAccount
        fields = ['id', 'college', 'code', 'name', 'account_type', 'parent', 'is_active', 'created_at']
        read_only_fields = ['id', 'college', 'created_at']


class JournalLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalLine
        fields = ['id', 'account', 'debit', 'credit', 'narration']


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalLineSerializer(many=True, read_only=True)

    class Meta:
        model = JournalEntry
        fields = [
            'id', 'college', 'entry_date', 'description', 'reference', 'status',
            'posted_by', 'lines', 'created_at',
        ]
        read_only_fields = ['id', 'college', 'posted_by', 'created_at']


class JournalEntryWriteSerializer(serializers.Serializer):
    entry_date = serializers.DateField()
    description = serializers.CharField(max_length=255)
    reference = serializers.CharField(max_length=50, required=False, allow_blank=True)
    lines = serializers.ListField(child=serializers.DictField(), min_length=2)


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'college', 'name', 'contact_person', 'email', 'phone', 'gstin', 'is_active', 'created_at']
        read_only_fields = ['id', 'college', 'created_at']


class BudgetSerializer(serializers.ModelSerializer):
    account_code = serializers.CharField(source='account.code', read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id', 'college', 'account', 'account_code', 'fiscal_year',
            'amount_allocated', 'amount_spent', 'created_at',
        ]
        read_only_fields = ['id', 'college', 'created_at']


class SalaryStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryStructure
        fields = [
            'id', 'college', 'staff', 'designation', 'basic_salary', 'hra',
            'allowances', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'college', 'created_at']


class PayrollRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollRun
        fields = [
            'id', 'college', 'month', 'year', 'status', 'total_gross',
            'total_net', 'processed_by', 'created_at',
        ]
        read_only_fields = ['id', 'college', 'processed_by', 'total_gross', 'total_net', 'created_at']


class PayslipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payslip
        fields = [
            'id', 'college', 'payroll_run', 'staff', 'gross_salary',
            'deductions', 'tds', 'net_salary', 'pdf_url', 'created_at',
        ]
        read_only_fields = fields


class PaymentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentOrder
        fields = [
            'id', 'college', 'student', 'fee_payment', 'amount', 'currency',
            'razorpay_order_id', 'status', 'receipt_url', 'created_at',
        ]
        read_only_fields = ['id', 'college', 'razorpay_order_id', 'status', 'created_at']
