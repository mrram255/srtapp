"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth-store";
import { assignmentsApi, type Assignment, type AssignmentSubmission } from "@/lib/api/assignments";

export default function AssignmentsPage() {
  const user = useAuthStore((s) => s.user);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [submissions, setSubmissions] = useState<AssignmentSubmission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"assignments" | "submissions">("assignments");
  const [showCreate, setShowCreate] = useState(false);
  const [showSubmit, setShowSubmit] = useState<string | null>(null);
  const [showGrade, setShowGrade] = useState<string | null>(null);
  const [formTitle, setFormTitle] = useState("");
  const [formDesc, setFormDesc] = useState("");
  const [submitText, setSubmitText] = useState("");
  const [gradeMarks, setGradeMarks] = useState("");
  const [gradeFeedback, setGradeFeedback] = useState("");
  const [actionMsg, setActionMsg] = useState("");

  const isTeacher = ["TEACHER", "HOD", "ADMIN", "SUPER_ADMIN"].includes(user?.role ?? "");

  const reload = async () => {
    const [aRes, sRes] = await Promise.all([assignmentsApi.list(), assignmentsApi.submissions()]);
    setAssignments(aRes.data?.items ?? aRes.data ?? []);
    setSubmissions(sRes.data?.items ?? sRes.data ?? []);
  };

  useEffect(() => {
    if (!user?.id) return;
    const fetchData = async () => {
      try {
        setLoading(true);
        await reload();
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load assignments.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user?.id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600" />
          <p className="text-sm text-gray-400">Loading assignments...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="m-6 p-5 bg-red-50 border border-red-200 rounded-xl text-red-700 flex items-center gap-3">
        <span className="text-xl">⚠️</span>
        <span>{error}</span>
      </div>
    );
  }

  const handleCreate = async () => {
    try {
      await assignmentsApi.create({ title: formTitle, description: formDesc, status: "PUBLISHED" });
      setShowCreate(false);
      setFormTitle("");
      setFormDesc("");
      await reload();
      setActionMsg("Assignment created.");
    } catch (e: unknown) {
      setActionMsg(e instanceof Error ? e.message : "Create failed.");
    }
  };

  const handleSubmit = async (assignmentId: string) => {
    try {
      await assignmentsApi.submit({ assignment: assignmentId, submission_text: submitText });
      setShowSubmit(null);
      setSubmitText("");
      await reload();
      setActionMsg("Submission saved.");
    } catch (e: unknown) {
      setActionMsg(e instanceof Error ? e.message : "Submit failed.");
    }
  };

  const handleGrade = async (submissionId: string) => {
    try {
      await assignmentsApi.grade(submissionId, {
        marks_obtained: Number(gradeMarks),
        feedback: gradeFeedback,
      });
      setShowGrade(null);
      setGradeMarks("");
      setGradeFeedback("");
      await reload();
      setActionMsg("Graded successfully.");
    } catch (e: unknown) {
      setActionMsg(e instanceof Error ? e.message : "Grade failed.");
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Assignments</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {isTeacher ? "Manage your assignments" : "Your assignments & submissions"}
          </p>
        </div>
        <div className="flex gap-2">
          {isTeacher ? (
            <button
              onClick={() => setShowCreate(true)}
              className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white"
            >
              + New assignment
            </button>
          ) : null}
        </div>
        <div className="flex gap-2 text-sm font-medium">
          <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full">
            {assignments.length} Assignments
          </span>
          {!isTeacher && (
            <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full">
              {submissions.length} Submitted
            </span>
          )}
        </div>
      </div>

      {actionMsg ? <p className="text-sm text-green-700">{actionMsg}</p> : null}

      {showCreate ? (
        <div className="rounded-xl border border-gray-200 bg-white p-4 space-y-3">
          <input value={formTitle} onChange={(e) => setFormTitle(e.target.value)} placeholder="Title" className="w-full rounded-lg border px-3 py-2 text-sm" />
          <textarea value={formDesc} onChange={(e) => setFormDesc(e.target.value)} placeholder="Description" rows={3} className="w-full rounded-lg border px-3 py-2 text-sm" />
          <div className="flex gap-2">
            <button onClick={handleCreate} className="rounded-lg bg-accent px-4 py-2 text-sm text-white">Save</button>
            <button onClick={() => setShowCreate(false)} className="rounded-lg border px-4 py-2 text-sm">Cancel</button>
          </div>
        </div>
      ) : null}

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit">
        {(["assignments", "submissions"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab === "assignments" ? "📋 Assignments" : "📤 Submissions"}
          </button>
        ))}
      </div>

      {activeTab === "assignments" && (
        <div className="space-y-3">
          {assignments.length === 0 ? (
            <EmptyState icon="📝" title="No assignments yet" subtitle="Assignments will appear here once published" />
          ) : (
            assignments.map((a) => (
              <div key={a.id}>
                <AssignmentCard assignment={a} />
                {!isTeacher && a.status === "PUBLISHED" ? (
                  <button onClick={() => setShowSubmit(a.id)} className="mt-2 text-sm text-accent hover:underline">
                    Submit work
                  </button>
                ) : null}
                {showSubmit === a.id ? (
                  <div className="mt-2 rounded-lg border p-3 space-y-2">
                    <textarea value={submitText} onChange={(e) => setSubmitText(e.target.value)} rows={3} className="w-full rounded border px-2 py-1 text-sm" placeholder="Your answer..." />
                    <button onClick={() => handleSubmit(a.id)} className="rounded bg-accent px-3 py-1 text-sm text-white">Send</button>
                  </div>
                ) : null}
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === "submissions" && (
        <div className="space-y-3">
          {submissions.length === 0 ? (
            <EmptyState icon="📤" title="No submissions yet" subtitle="Submitted assignments will appear here" />
          ) : (
            submissions.map((s) => (
              <div key={s.id}>
                <SubmissionCard submission={s} />
                {isTeacher && s.status === "SUBMITTED" ? (
                  <>
                    <button onClick={() => setShowGrade(s.id)} className="mt-2 text-sm text-accent hover:underline">
                      Grade
                    </button>
                    {showGrade === s.id ? (
                      <div className="mt-2 rounded-lg border p-3 space-y-2">
                        <input value={gradeMarks} onChange={(e) => setGradeMarks(e.target.value)} placeholder="Marks" className="w-full rounded border px-2 py-1 text-sm" />
                        <textarea value={gradeFeedback} onChange={(e) => setGradeFeedback(e.target.value)} placeholder="Feedback" rows={2} className="w-full rounded border px-2 py-1 text-sm" />
                        <button onClick={() => handleGrade(s.id)} className="rounded bg-accent px-3 py-1 text-sm text-white">Save grade</button>
                      </div>
                    ) : null}
                  </>
                ) : null}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

function AssignmentCard({ assignment }: { assignment: Assignment }) {
  const isOverdue = new Date(assignment.due_date) < new Date();
  const statusColors: Record<string, string> = {
    DRAFT: "bg-gray-100 text-gray-600",
    PUBLISHED: "bg-green-100 text-green-700",
    CLOSED: "bg-red-100 text-red-700",
  };
  return (
    <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-gray-900">{assignment.title}</h3>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${statusColors[assignment.status] ?? "bg-gray-100 text-gray-600"}`}>
              {assignment.status}
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-1 line-clamp-2">{assignment.description}</p>
          <div className="flex flex-wrap gap-3 mt-3 text-xs text-gray-500">
            <span>📚 {assignment.subject_name}</span>
            <span>👨‍🏫 {assignment.teacher_name}</span>
            <span>🎯 Max: {assignment.max_marks} marks</span>
            <span className={isOverdue ? "text-red-500 font-medium" : ""}>
              📅 Due: {new Date(assignment.due_date).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}
              {isOverdue && " (Overdue)"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function SubmissionCard({ submission }: { submission: AssignmentSubmission }) {
  const statusColors: Record<string, string> = {
    PENDING: "bg-yellow-100 text-yellow-700",
    SUBMITTED: "bg-blue-100 text-blue-700",
    LATE: "bg-orange-100 text-orange-700",
    GRADED: "bg-green-100 text-green-700",
    RESUBMIT: "bg-red-100 text-red-700",
  };
  return (
    <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-gray-900">{submission.assignment_title}</h3>
          <p className="text-xs text-gray-400 mt-0.5">
            Submitted: {submission.submitted_at
              ? new Date(submission.submitted_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })
              : "—"}
          </p>
        </div>
        <span className={`text-xs font-semibold px-3 py-1 rounded-full ${statusColors[submission.status] ?? "bg-gray-100 text-gray-600"}`}>
          {submission.status}
        </span>
      </div>
      {submission.status === "GRADED" && (
        <div className="mt-3 p-3 bg-green-50 border border-green-100 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm text-green-700 font-medium">
              Marks: {submission.marks_obtained} / —
            </span>
          </div>
          {submission.feedback && (
            <p className="text-xs text-gray-600 mt-1">💬 {submission.feedback}</p>
          )}
        </div>
      )}
    </div>
  );
}

function EmptyState({ icon, title, subtitle }: { icon: string; title: string; subtitle: string }) {
  return (
    <div className="text-center py-16 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
      <p className="text-4xl mb-3">{icon}</p>
      <p className="text-gray-500 font-medium">{title}</p>
      <p className="text-gray-400 text-sm mt-1">{subtitle}</p>
    </div>
  );
}
