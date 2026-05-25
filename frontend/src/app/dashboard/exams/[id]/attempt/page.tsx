"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { examsApi, type MCQQuestion } from "@/lib/api/exams";

export default function ExamAttemptPage() {
  const params = useParams();
  const router = useRouter();
  const examId = String(params.id ?? "");

  const [attemptId, setAttemptId] = useState("");
  const [examName, setExamName] = useState("");
  const [questions, setQuestions] = useState<MCQQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!examId) return;
    examsApi
      .startExam(examId)
      .then((res) => {
        const data = res.data ?? res;
        setAttemptId(data.attempt_id);
        setExamName(data.exam_name ?? "Exam");
        setQuestions(data.questions ?? []);
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : "Could not start exam.");
      })
      .finally(() => setLoading(false));
  }, [examId]);

  const submit = async () => {
    if (!attemptId) return;
    setSubmitting(true);
    setError("");
    try {
      const payload = questions.map((q) => ({
        question: q.id,
        selected_option: answers[q.id] ?? null,
      }));
      await examsApi.submitExam(attemptId, payload);
      router.push("/dashboard/exams");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Submit failed.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-purple-200 border-t-purple-600" />
      </div>
    );
  }

  if (error && questions.length === 0) {
    return (
      <div className="m-6 rounded-xl border border-red-200 bg-red-50 p-5 text-red-700">
        {error}
        <button onClick={() => router.push("/dashboard/exams")} className="mt-3 block text-sm underline">
          Back to exams
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{examName}</h1>
        <p className="text-sm text-gray-500">{questions.length} questions — select one option each</p>
      </div>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <div className="space-y-4">
        {questions.map((q, idx) => (
          <div key={q.id} className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
            <p className="font-medium text-gray-900">
              Q{idx + 1}. {q.question_text}
            </p>
            <div className="mt-3 space-y-2">
              {(["A", "B", "C", "D"] as const).map((opt) => {
                const key = `option_${opt.toLowerCase()}` as keyof MCQQuestion;
                const label = q[key];
                if (!label) return null;
                return (
                  <label key={opt} className="flex cursor-pointer items-center gap-2 rounded-lg border border-gray-100 p-3 hover:bg-gray-50">
                    <input
                      type="radio"
                      name={q.id}
                      value={opt}
                      checked={answers[q.id] === opt}
                      onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: opt }))}
                    />
                    <span className="text-sm text-gray-700">
                      <strong>{opt}.</strong> {String(label)}
                    </span>
                  </label>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={submit}
        disabled={submitting}
        className="w-full rounded-xl bg-purple-600 py-3 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-60"
      >
        {submitting ? "Submitting..." : "Submit exam"}
      </button>
    </div>
  );
}
