"use client";
import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth-store";
import api from "@/lib/api/client";
import { MessageSquare, ThumbsUp, Plus, X } from "lucide-react";

interface ForumThread {
  id: string; title: string; body: string;
  author_name: string; subject_name: string;
  reply_count: number; created_at: string;
}
interface ForumReply {
  id: string; body: string; author_name: string;
  like_count: number; created_at: string;
}

export default function ForumPage() {
  const user = useAuthStore((s) => s.user);
  const [threads, setThreads] = useState<ForumThread[]>([]);
  const [selected, setSelected] = useState<ForumThread | null>(null);
  const [replies, setReplies] = useState<ForumReply[]>([]);
  const [loading, setLoading] = useState(true);
  const [replyText, setReplyText] = useState("");
  const [newThread, setNewThread] = useState({ title: "", body: "" });
  const [showNew, setShowNew] = useState(false);
  const [error, setError] = useState("");

  const canCreate = ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"].includes(user?.role ?? "");

  const loadThreads = async () => {
    try {
      setLoading(true);
      const res = await api.get("/forum/").then((r) => r.data);
      setThreads(res.data ?? []);
    } catch { setError("Failed to load forum."); }
    finally { setLoading(false); }
  };

  const loadReplies = async (threadId: string) => {
    const res = await api.get(`/forum/${threadId}/`).then((r) => r.data);
    setReplies(res.data?.replies ?? []);
  };

  const openThread = async (thread: ForumThread) => {
    setSelected(thread);
    await loadReplies(thread.id);
  };

  const submitReply = async () => {
    if (!replyText.trim() || !selected) return;
    await api.post(`/forum/${selected.id}/replies/`, { body: replyText });
    setReplyText("");
    await loadReplies(selected.id);
  };

  const createThread = async () => {
    if (!newThread.title.trim() || !newThread.body.trim()) return;
    await api.post("/forum/", newThread);
    setNewThread({ title: "", body: "" });
    setShowNew(false);
    await loadThreads();
  };

  const likeReply = async (replyId: string) => {
    await api.post(`/forum/replies/${replyId}/like/`);
    if (selected) await loadReplies(selected.id);
  };

  useEffect(() => { if (user?.id) loadThreads(); }, [user?.id]);

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600" />
    </div>
  );

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Discussion Forum</h1>
          <p className="text-sm text-gray-500 mt-0.5">Ask questions, share knowledge</p>
        </div>
        {canCreate && (
          <button onClick={() => setShowNew(true)}
            className="flex items-center gap-2 px-4 py-2 bg-accent text-white rounded-xl text-sm font-medium hover:bg-accent/90">
            <Plus className="h-4 w-4" /> New Thread
          </button>
        )}
      </div>

      {error && <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">⚠️ {error}</div>}

      {showNew && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-lg bg-white rounded-2xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">New Discussion Thread</h2>
              <button onClick={() => setShowNew(false)}><X className="h-5 w-5 text-gray-400" /></button>
            </div>
            <div className="space-y-4">
              <input value={newThread.title}
                onChange={(e) => setNewThread((p) => ({ ...p, title: e.target.value }))}
                placeholder="Thread title..."
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent" />
              <textarea value={newThread.body}
                onChange={(e) => setNewThread((p) => ({ ...p, body: e.target.value }))}
                placeholder="Describe your question..." rows={4}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent resize-none" />
            </div>
            <div className="flex gap-3 mt-5">
              <button onClick={() => setShowNew(false)}
                className="flex-1 px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancel</button>
              <button onClick={createThread}
                className="flex-1 px-4 py-2 bg-accent text-white rounded-lg text-sm font-medium hover:bg-accent/90">Post Thread</button>
            </div>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-3">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">All Threads ({threads.length})</p>
          {threads.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
              <p className="text-4xl mb-2">💬</p>
              <p className="text-gray-500 text-sm">No discussions yet. Start one!</p>
            </div>
          ) : threads.map((thread) => (
            <button key={thread.id} onClick={() => openThread(thread)}
              className={"w-full text-left p-4 rounded-xl border transition-all hover:shadow-sm " + (selected?.id === thread.id ? "border-accent bg-accent/5" : "border-gray-100 bg-white")}>
              <p className="font-medium text-gray-900 text-sm line-clamp-1">{thread.title}</p>
              <p className="text-xs text-gray-500 mt-1 line-clamp-2">{thread.body}</p>
              <div className="flex items-center gap-3 mt-2">
                <span className="text-xs text-gray-400">{thread.author_name}</span>
                <span className="text-xs text-gray-400 flex items-center gap-1">
                  <MessageSquare className="h-3 w-3" />{thread.reply_count}
                </span>
                <span className="text-xs text-gray-400">{new Date(thread.created_at).toLocaleDateString("en-IN")}</span>
              </div>
            </button>
          ))}
        </div>

        <div>
          {!selected ? (
            <div className="flex items-center justify-center h-64 bg-white rounded-2xl border border-gray-100">
              <div className="text-center text-gray-400">
                <MessageSquare className="h-10 w-10 mx-auto mb-2 opacity-30" />
                <p className="text-sm">Select a thread to view</p>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-2xl border border-gray-100 p-5 space-y-4">
              <div>
                <h2 className="font-semibold text-gray-900">{selected.title}</h2>
                <p className="text-sm text-gray-600 mt-1">{selected.body}</p>
                <p className="text-xs text-gray-400 mt-2">by {selected.author_name}</p>
              </div>
              <hr className="border-gray-100" />
              <div className="space-y-3 max-h-64 overflow-y-auto">
                <p className="text-xs font-semibold text-gray-500 uppercase">Replies ({replies.length})</p>
                {replies.length === 0 ? (
                  <p className="text-sm text-gray-400 text-center py-4">No replies yet. Be the first!</p>
                ) : replies.map((reply) => (
                  <div key={reply.id} className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-700">{reply.body}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-gray-400">{reply.author_name}</span>
                      <button onClick={() => likeReply(reply.id)}
                        className="flex items-center gap-1 text-xs text-gray-400 hover:text-accent">
                        <ThumbsUp className="h-3 w-3" /> {reply.like_count}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              {canCreate && (
                <div className="flex gap-2 pt-2 border-t border-gray-100">
                  <input value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    placeholder="Write a reply..."
                    onKeyDown={(e) => { if (e.key === "Enter") submitReply(); }}
                    className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent" />
                  <button onClick={submitReply}
                    className="px-4 py-2 bg-accent text-white rounded-lg text-sm font-medium hover:bg-accent/90">Send</button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
