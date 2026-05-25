"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth-store";
import { timetableApi, type TimetableEntry, type WeekTimetable } from "@/lib/api/timetable";

const DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"];

const DAY_SHORT: Record<string, string> = {
  MONDAY: "Mon",
  TUESDAY: "Tue",
  WEDNESDAY: "Wed",
  THURSDAY: "Thu",
  FRIDAY: "Fri",
  SATURDAY: "Sat",
};

const TODAY = new Date().toLocaleDateString("en-US", { weekday: "long" }).toUpperCase();

export default function TimetablePage() {
  const user = useAuthStore((s) => s.user);
  const [view, setView] = useState<"today" | "week">("today");
  const [todayClasses, setTodayClasses] = useState<TimetableEntry[]>([]);
  const [weekData, setWeekData] = useState<WeekTimetable>({});
  const [selectedDay, setSelectedDay] = useState(TODAY);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user?.id) return;
    const fetchData = async () => {
      try {
        setLoading(true);
        const [todayRes, weekRes] = await Promise.all([
          timetableApi.today(),
          timetableApi.week(),
        ]);
        setTodayClasses(todayRes.data ?? []);
        setWeekData(weekRes.data ?? {});
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load timetable.");
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
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-200 border-t-indigo-600" />
          <p className="text-sm text-gray-400">Loading timetable...</p>
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

  const displayClasses = view === "today"
    ? todayClasses
    : (weekData[selectedDay] ?? []);

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Timetable</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {view === "today" ? `Today — ${TODAY.charAt(0) + TODAY.slice(1).toLowerCase()}` : "Weekly Schedule"}
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex bg-gray-100 rounded-xl p-1 gap-1">
          {(["today", "week"] as const).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                view === v
                  ? "bg-white text-indigo-600 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {v === "today" ? "Today" : "Week"}
            </button>
          ))}
        </div>
      </div>

      {/* Day Selector for Week View */}
      {view === "week" && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {DAYS.map((day) => {
            const count = weekData[day]?.length ?? 0;
            const isToday = day === TODAY;
            const isSelected = day === selectedDay;
            return (
              <button
                key={day}
                onClick={() => setSelectedDay(day)}
                className={`flex-shrink-0 flex flex-col items-center px-4 py-3 rounded-xl border transition-all ${
                  isSelected
                    ? "bg-indigo-600 border-indigo-600 text-white"
                    : isToday
                    ? "bg-indigo-50 border-indigo-200 text-indigo-700"
                    : "bg-white border-gray-200 text-gray-600 hover:border-indigo-200"
                }`}
              >
                <span className="text-xs font-medium">{DAY_SHORT[day]}</span>
                <span className={`text-lg font-bold mt-0.5 ${isSelected ? "text-white" : ""}`}>
                  {count}
                </span>
                <span className={`text-xs mt-0.5 ${isSelected ? "text-indigo-200" : "text-gray-400"}`}>
                  classes
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* Classes List */}
      {displayClasses.length === 0 ? (
        <div className="text-center py-16 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
          <p className="text-4xl mb-3">📅</p>
          <p className="text-gray-500 font-medium">No classes scheduled</p>
          <p className="text-gray-400 text-sm mt-1">
            {view === "today" ? "Enjoy your free day!" : "No classes on this day"}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {displayClasses.map((entry, idx) => (
            <ClassCard key={entry.id} entry={entry} index={idx} />
          ))}
        </div>
      )}

      {/* Week Overview Stats */}
      {view === "week" && Object.keys(weekData).length > 0 && (
        <div className="bg-indigo-50 rounded-2xl p-4 border border-indigo-100">
          <p className="text-sm font-semibold text-indigo-700 mb-3">Weekly Overview</p>
          <div className="grid grid-cols-6 gap-2">
            {DAYS.map((day) => {
              const count = weekData[day]?.length ?? 0;
              const isToday = day === TODAY;
              return (
                <div key={day} className="text-center">
                  <p className="text-xs text-gray-500">{DAY_SHORT[day]}</p>
                  <div className="mt-1 bg-white rounded-lg py-2">
                    <p className={`text-lg font-bold ${isToday ? "text-indigo-600" : "text-gray-700"}`}>
                      {count}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function ClassCard({ entry, index }: { entry: TimetableEntry; index: number }) {
  const colors = [
    "border-l-blue-500 bg-blue-50",
    "border-l-purple-500 bg-purple-50",
    "border-l-green-500 bg-green-50",
    "border-l-orange-500 bg-orange-50",
    "border-l-pink-500 bg-pink-50",
    "border-l-teal-500 bg-teal-50",
  ];
  const color = colors[index % colors.length];

  return (
    <div className={`border-l-4 rounded-xl p-4 ${color} border border-gray-100 shadow-sm`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{entry.subject_name}</h3>
          <p className="text-sm text-gray-500 mt-0.5">{entry.teacher_name}</p>
        </div>
        <div className="text-right">
          <p className="text-sm font-bold text-gray-700">
            {entry.start_time.slice(0, 5)} — {entry.end_time.slice(0, 5)}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">Period {index + 1}</p>
        </div>
      </div>
      <div className="mt-3 flex gap-2 flex-wrap">
        <span className="px-2 py-1 bg-white rounded-lg text-xs text-gray-600 border border-gray-200">
          🏫 Room {entry.room_number}
        </span>
        <span className="px-2 py-1 bg-white rounded-lg text-xs text-gray-600 border border-gray-200">
          📚 Sem {entry.semester}
        </span>
        <span className="px-2 py-1 bg-white rounded-lg text-xs text-gray-600 border border-gray-200">
          👥 Section {entry.section}
        </span>
      </div>
    </div>
  );
}
