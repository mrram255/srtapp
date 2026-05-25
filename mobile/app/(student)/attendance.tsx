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

type AttendanceSummary = {
  id: string;
  subject_name: string;
  percentage: number;
  present_count: number;
  absent_count: number;
  total_classes: number;
};

type MonthlyStats = {
  total: number;
  present: number;
  absent: number;
  late: number;
  excused: number;
  percentage: number;
  is_low: boolean;
};

function unwrapList<T>(payload: ApiEnvelope<T[] | { items?: T[] }> | undefined): T[] {
  const raw = payload?.data;
  if (Array.isArray(raw)) return raw;
  if (raw && typeof raw === "object" && Array.isArray((raw as { items?: T[] }).items)) {
    return (raw as { items: T[] }).items;
  }
  return [];
}

export default function StudentAttendanceScreen() {
  const insets = useSafeAreaInsets();
  const [summaries, setSummaries] = useState<AttendanceSummary[]>([]);
  const [stats, setStats] = useState<MonthlyStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      setError("");
      const meRes = await api.get<ApiEnvelope<{ id: string }>>("/students/me/");
      const studentId = meRes.data?.data?.id;
      if (!studentId) throw new Error("Student profile not found.");

      const [summaryRes, statsRes] = await Promise.all([
        api.get<ApiEnvelope<AttendanceSummary[]>>("/attendance/summary/"),
        api.get<ApiEnvelope<MonthlyStats>>("/attendance/monthly-stats/", {
          params: { student: studentId },
        }),
      ]);

      setSummaries(unwrapList(summaryRes.data));
      setStats(statsRes.data?.data ?? null);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load attendance.");
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
      <Text style={styles.title}>Attendance</Text>
      <Text style={styles.sub}>Subject-wise summary and this month&apos;s stats</Text>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      {stats ? (
        <View style={[styles.statsCard, stats.is_low && styles.statsCardLow]}>
          <Text style={styles.statsLabel}>This month</Text>
          <Text style={styles.statsValue}>{stats.percentage}%</Text>
          <Text style={styles.statsMeta}>
            {stats.present} present · {stats.absent} absent · {stats.total} total
          </Text>
          {stats.is_low ? <Text style={styles.lowBadge}>Below 75% threshold</Text> : null}
        </View>
      ) : null}

      {summaries.length === 0 ? (
        <Text style={styles.empty}>No attendance records yet.</Text>
      ) : (
        summaries.map((row) => (
          <View key={row.id} style={styles.row}>
            <View style={styles.rowHead}>
              <Text style={styles.subject}>{row.subject_name}</Text>
              <Text style={[styles.pct, row.percentage < 75 && styles.pctLow]}>{row.percentage}%</Text>
            </View>
            <Text style={styles.rowMeta}>
              {row.present_count}/{row.total_classes} classes · {row.absent_count} absent
            </Text>
          </View>
        ))
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
  statsCard: {
    backgroundColor: Colors.light.surface,
    borderRadius: 16,
    padding: Spacing.lg,
    marginBottom: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  statsCardLow: { borderColor: Colors.light.warning, backgroundColor: `${Colors.light.warning}10` },
  statsLabel: { fontSize: 13, color: Colors.light.textMuted, fontWeight: "600" },
  statsValue: { fontSize: 32, fontWeight: "800", color: Colors.light.text, marginTop: Spacing.xs },
  statsMeta: { fontSize: 13, color: Colors.light.textMuted, marginTop: Spacing.xs },
  lowBadge: { marginTop: Spacing.sm, fontSize: 12, fontWeight: "700", color: Colors.light.warning },
  empty: { fontSize: 15, color: Colors.light.textMuted },
  row: {
    backgroundColor: Colors.light.surface,
    borderRadius: 12,
    padding: Spacing.base,
    marginBottom: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  rowHead: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  subject: { fontSize: 15, fontWeight: "600", color: Colors.light.text, flex: 1 },
  pct: { fontSize: 16, fontWeight: "800", color: Colors.light.success },
  pctLow: { color: Colors.light.warning },
  rowMeta: { fontSize: 12, color: Colors.light.textMuted, marginTop: Spacing.xs },
});
