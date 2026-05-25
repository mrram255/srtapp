from rest_framework import serializers
from .models import ForumThread, ForumReply


class ForumReplySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_role = serializers.CharField(source='author.role', read_only=True)

    class Meta:
        model = ForumReply
        fields = [
            'id', 'thread', 'author', 'author_name', 'author_role',
            'body', 'parent_reply', 'is_flagged', 'is_accepted',
            'like_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'like_count', 'created_at', 'updated_at']


class ForumThreadSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_role = serializers.CharField(source='author.role', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    tags_list = serializers.SerializerMethodField()

    class Meta:
        model = ForumThread
        fields = [
            'id', 'college', 'title', 'body',
            'author', 'author_name', 'author_role',
            'subject', 'subject_name', 'department', 'semester',
            'tags', 'tags_list', 'is_pinned', 'is_closed', 'is_flagged',
            'view_count', 'reply_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'college', 'author', 'view_count', 'reply_count', 'created_at', 'updated_at']

    def get_tags_list(self, obj):
        return [t.strip() for t in obj.tags.split(',') if t.strip()] if obj.tags else []
