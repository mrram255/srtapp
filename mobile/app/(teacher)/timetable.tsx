import { Ionicons } from "@expo/vector-icons";
import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { Colors } from "@/constants/Colors";
import { Spacing } from "@/constants/Spacing";
import api from "@/lib/api";
import type { ApiEnvelope } from "@/lib/types";

type TimetableEntry = {
  id: string;
  subject_name: string;
  section: string;
  start_time: string;
  end_time: string;
  room_number: string;
};

function slotStatus(start: string, end: string): "completed" | "ongoing" | "upcoming" {
  const now = new Date();
  const toMin = (t: string) => {
    const [h, m] = t.split(":").map(Number);
    return h * 60 + m;
  };
  const nowMin = now.getHours() * 60 + now.getMinutes();
  if (nowMin >= toMin(end)) return "completed";
  if (nowMin >= toMin(start)) return "ongoing";
  return "upcoming";
}

export default function TeacherTimetableScreen() {
  const insets = useSafeAreaInsets();
  const [entries, setEntries] = useState<TimetableEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      setError("");
      const res = await api.get<ApiEnvelope<TimetableEntry[]>>("/academics/timetable/today/");
      const raw = res.data?.data;
      setEntries(Array.isArray(raw) ? raw : []);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load timetable.");
    }
  }, []);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      await load();
      setLoading(false);
    })();
  }, [load]);

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <View style={[styles.center, { paddingTop: insets.top }]}>
        <ActivityIndicator size="large" color={Colors.light.accent} />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.screen}
      contentContainerStyle={{ paddingTop: insets.top + Spacing["2xl"], paddingBottom: Spacing["2xl"] }}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => void onRefresh()} />}
    >
      <Text style={styles.title}>Schedule</Text>
      <Text style={styles.sub}>Today&apos;s teaching periods</Text>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      {entries.length === 0 ? (
        <Text style={styles.empty}>No classes scheduled today.</Text>
      ) : (
        entries.map((cls) => {
          const status = slotStatus(cls.start_time, cls.end_time);
          return (
            <View key={cls.id} style={[styles.row, status === "ongoing" && styles.rowActive]}>
              <View style={styles.timeCol}>
                <Text style={styles.time}>{cls.start_time?.slice(0, 5)}</Text>
                <Text style={styles.timeEnd}>{cls.end_time?.slice(0, 5)}</Text>
              </View>
              <View style={styles.body}>
                <Text style={styles.subject}>{cls.subject_name}</Text>
                <Text style={styles.meta}>
                  {cls.section} · {cls.room_number || "—"}
                </Text>
              </View>
              {status === "ongoing" ? (
                <View style={styles.nowBadge}>
                  <Text style={styles.nowText}>Now</Text>
                </View>
              ) : status === "completed" ? (
                <Ionicons name="checkmark-circle" size={20} color={Colors.light.success} />
              ) : null}
            </View>
          );
        })
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: Colors.light.bg, paddingHorizontal: Spacing.xl },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: Colors.light.bg },
  title: { fontSize: 22, fontWeight: "700", color: Colors.light.text, marginBottom: Spacing.xs },
  sub: { fontSize: 14, color: Colors.light.textMuted, marginBottom: Spacing.lg },
  error: { color: Colors.light.error, marginBottom: Spacing.base },
  empty: { fontSize: 15, color: Colors.light.textMuted },
  row: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.light.surface,
    borderRadius: 12,
    padding: Spacing.base,
    marginBottom: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  rowActive: { borderColor: Colors.light.accent, backgroundColor: `${Colors.light.accent}08` },
  timeCol: { width: 56 },
  time: { fontSize: 13, fontWeight: "700", color: Colors.light.text },
  timeEnd: { fontSize: 11, color: Colors.light.textMuted, marginTop: 2 },
  body: { flex: 1, marginLeft: Spacing.sm },
  subject: { fontSize: 15, fontWeight: "600", color: Colors.light.text },
  meta: { fontSize: 12, color: Colors.light.textMuted, marginTop: 2 },
  nowBadge: {
    backgroundColor: Colors.light.accent,
    borderRadius: 8,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
  },
  nowText: { color: "#fff", fontSize: 10, fontWeight: "bold" },
});
