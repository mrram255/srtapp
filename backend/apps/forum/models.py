from django.db import models
from apps.core.models import CollegeScopedModel


class ForumThread(CollegeScopedModel):
    title = models.CharField(max_length=300)
    body = models.TextField()
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='forum_threads')
    subject = models.ForeignKey('academics.Subject', on_delete=models.SET_NULL, null=True, blank=True, related_name='threads')
    department = models.ForeignKey('colleges.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='threads')
    semester = models.PositiveIntegerField(null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'forum_threads'
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title


class ForumReply(CollegeScopedModel):
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='forum_replies')
    body = models.TextField()
    parent_reply = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_replies')
    is_flagged = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    like_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'forum_replies'
        ordering = ['created_at']


class ForumLike(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    reply = models.ForeignKey(ForumReply, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'forum_likes'
        unique_together = [['user', 'reply']]
