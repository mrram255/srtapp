from rest_framework import serializers

from apps.accounts.models import User

from .models import Message, MessageThread


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'college',
            'thread',
            'sender',
            'sender_email',
            'content',
            'attachment',
            'is_edited',
            'edited_at',
            'is_read',
            'read_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'sender', 'sender_email', 'created_at', 'updated_at']


class MessageWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['thread', 'content', 'attachment']

    def validate_thread(self, thread: MessageThread):
        user = self.context['request'].user
        if not thread.participants.filter(pk=user.pk).exists():
            raise serializers.ValidationError('You are not a participant in this thread.')
        return thread

    def create(self, validated_data):
        thread = validated_data['thread']
        request = self.context['request']
        return Message.objects.create(
            thread=thread,
            college=thread.college,
            sender=request.user,
            content=validated_data['content'],
            attachment=validated_data.get('attachment') or '',
        )


class MessageThreadSerializer(serializers.ModelSerializer):
    participant_ids = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = [
            'id',
            'college',
            'title',
            'thread_type',
            'participant_ids',
            'created_by',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_participant_ids(self, obj):
        return [str(uid) for uid in obj.participants.values_list('pk', flat=True)]


class MessageThreadWriteSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True)

    class Meta:
        model = MessageThread
        fields = ['title', 'thread_type', 'participant_ids']

    def validate_participant_ids(self, ids):
        user = self.context['request'].user
        ids = list(dict.fromkeys(ids))
        if user.pk not in ids:
            ids.append(user.pk)
        college_id = self.context['college'].id if self.context.get('college') else None
        qs = User.objects.filter(pk__in=ids, is_deleted=False, is_active=True)
        if college_id:
            qs = qs.filter(college_id=college_id)
        found = set(qs.values_list('pk', flat=True))
        missing = set(ids) - found
        if missing:
            raise serializers.ValidationError('Invalid or out-of-scope participant ids.')
        return ids

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        college = self.context['college']
        creator = self.context['request'].user
        thread = MessageThread.objects.create(
            **validated_data,
            college=college,
            created_by=creator,
        )
        users = list(User.objects.filter(pk__in=participant_ids))
        thread.participants.set(users)
        return thread
