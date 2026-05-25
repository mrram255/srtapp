"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth-store";
import { examsApi, type ExamSchedule, type ExamResult } from "@/lib/api/exams";
import Link from "next/link";

const EXAM_TYPE_LABEL: Record<string, string> = {
  INTERNAL_1: "Internal 1",
  INTERNAL_2: "Internal 2",
  INTERNAL_3: "Internal 3",
  SEMESTER: "Semester",
  PRACTICAL: "Practical",
  VIVA: "Viva",
  QUIZ: "Quiz",
};

const EXAM_TYPE_COLOR: Record<string, string> = {
  INTERNAL_1: "bg-blue-100 text-blue-700",
  INTERNAL_2: "bg-indigo-100 text-indigo-700",
  INTERNAL_3: "bg-purple-100 text-purple-700",
  SEMESTER: "bg-red-100 text-red-700",
  PRACTICAL: "bg-green-100 text-green-700",
  VIVA: "bg-yellow-100 text-yellow-700",
  QUIZ: "bg-orange-100 text-orange-700",
};

export default function ExamsPage() {
  const user = useAuthStore((s) => s.user);
  const [exams, setExams] = useState<ExamSchedule[]>([]);
  const [results, setResults] = useState<ExamResult[]>([]);
  const [tab, setTab] = useState<"upcoming" | "results">("upcoming");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user?.id) return;
    const fetchData = async () => {
      try {
        setLoading(true);
        const [examsRes, resultsRes] = await Promise.all([
          examsApi.list(),
          examsApi.results(),
        ]);
        setExams(examsRes.data ?? []);
        setResults(resultsRes.data ?? []);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load exams.");
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
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-200 border-t-purple-600" />
          <p className="text-sm text-gray-400">Loading exams...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="m-6 p-5 bg-red-50 border border-red-200 rounded-xl text-red-700">
        ⚠️ {error}
      </div>
    );
  }

  const today = new Date().toISOString().split("T")[0];
  const upcoming = exams.filter((e) => e.exam_date >= today);
  const past = exams.filter((e) => e.exam_date < today);

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Examinations</h1>
          <p className="text-sm text-gray-500 mt-0.5">Schedule, results & rankings</p>
        </div>
        <div className="flex gap-3">
          <div className="bg-purple-50 border border-purple-100 rounded-xl px-4 py-2 text-center">
            <p className="text-xs text-purple-500">Upcoming</p>
            <p className="text-xl font-bold text-purple-700">{upcoming.length}</p>
          </div>
          <div className="bg-green-50 border border-green-100 rounded-xl px-4 py-2 text-center">
            <p className="text-xs text-green-500">Results</p>
            <p className="text-xl font-bold text-green-700">{results.length}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex bg-gray-100 rounded-xl p-1 gap-1 w-fit">
        {(["upcoming", "results"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition-all capitalize ${
              tab === t
                ? "bg-white text-purple-600 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Upcoming Exams */}
      {tab === "upcoming" && (
        <div className="space-y-3">
          {upcoming.length === 0 ? (
            <EmptyState icon="📝" title="No upcoming exams" subtitle="You're all caught up!" />
          ) : (
            upcoming.map((exam) => <ExamCard key={exam.id} exam={exam} showStart={user?.role === "STUDENT"} />)
          )}
          {past.length > 0 && (
            <>
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide pt-2">Past Exams</h3>
              {past.map((exam) => (
                <ExamCard key={exam.id} exam={exam} isPast showStart={false} />
              ))}
            </>
          )}
        </div>
      )}

      {/* Results */}
      {tab === "results" && (
        <div className="space-y-3">
          {results.length === 0 ? (
            <EmptyState icon="📊" title="No results yet" subtitle="Results will appear after exam evaluation" />
          ) : (
            results.map((result) => <ResultCard key={result.id} result={result} />)
          )}
        </div>
      )}
    </div>
  );
}

function ExamCard({
  exam,
  isPast = false,
  showStart = false,
}: {
  exam: ExamSchedule;
  isPast?: boolean;
  showStart?: boolean;
}) {
  const daysLeft = Math.ceil(
    (new Date(exam.exam_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <div className={`bg-white border rounded-xl p-4 shadow-sm ${isPast ? "opacity-60" : ""}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${EXAM_TYPE_COLOR[exam.exam_type] ?? "bg-gray-100 text-gray-600"}`}>
              {EXAM_TYPE_LABEL[exam.exam_type] ?? exam.exam_type}
            </span>
            {!isPast && daysLeft <= 3 && daysLeft >= 0 && (
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-red-100 text-red-600">
                {daysLeft === 0 ? "Today!" : `${daysLeft}d left`}
              </span>
            )}
          </div>
          <h3 className="font-semibold text-gray-900">{exam.name}</h3>
          <p className="text-sm text-gray-500">{exam.subject_name}</p>
        </div>
        {showStart && exam.question_count > 0 && !isPast && (
          <Link
            href={`/dashboard/exams/${exam.id}/attempt`}
            className="px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors"
          >
            Start Exam
          </Link>
        )}
      </div>
      <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-gray-400">Date</p>
          <p className="font-semibold text-gray-700">{new Date(exam.exam_date).toLocaleDateString("en-IN")}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-gray-400">Time</p>
          <p className="font-semibold text-gray-700">{exam.start_time.slice(0, 5)} — {exam.end_time.slice(0, 5)}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-gray-400">Marks</p>
          <p className="font-semibold text-gray-700">{exam.max_marks} ({exam.passing_marks} pass)</p>
        </div>
      </div>
      {exam.room_number && (
        <p className="mt-2 text-xs text-gray-400">🏫 Room: {exam.room_number}</p>
      )}
      {exam.question_count > 0 && (
        <p className="mt-1 text-xs text-purple-500">📋 {exam.question_count} MCQ questions</p>
      )}
    </div>
  );
}

function ResultCard({ result }: { result: ExamResult }) {
  const isPassed = result.status === "PASS";
  return (
    <div className={`bg-white border rounded-xl p-4 shadow-sm border-l-4 ${isPassed ? "border-l-green-500" : "border-l-red-500"}`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-gray-900">{result.exam_name}</h3>
          <p className="text-sm text-gray-500 mt-0.5">
            Marks: {result.marks_obtained} • {result.percentage}%
          </p>
        </div>
        <div className="text-right">
          <span className={`text-sm font-bold px-3 py-1 rounded-full ${isPassed ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
            {result.status}
          </span>
          {result.rank && (
            <p className="text-xs text-gray-400 mt-1">Rank #{result.rank}</p>
          )}
        </div>
      </div>
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
