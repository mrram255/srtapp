import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import type { ComponentProps } from "react";
import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

import { Colors } from "@/constants/Colors";
import { Spacing } from "@/constants/Spacing";
import api from "@/lib/api";
import type { ApiEnvelope } from "@/lib/types";
import { useAuthStore } from "@/store/auth-store";

type IonIconName = ComponentProps<typeof Ionicons>["name"];

type TeacherStats = {
  my_assignments?: number;
  pending_grading?: number;
  classes_today?: number;
};

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

export default function TeacherDashboard() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const [stats, setStats] = useState<TeacherStats>({});
  const [schedule, setSchedule] = useState<TimetableEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    const [dashRes, todayRes] = await Promise.all([
      api.get<ApiEnvelope<TeacherStats>>("/analytics/dashboard/"),
      api.get<ApiEnvelope<TimetableEntry[]>>("/academics/timetable/today/").catch(() => ({ data: { data: [] } })),
    ]);
    setStats(dashRes.data?.data ?? {});
    const raw = todayRes.data?.data;
    setSchedule(Array.isArray(raw) ? raw : []);
  }, []);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      try {
        await load();
      } catch {
        setStats({});
        setSchedule([]);
      } finally {
        setLoading(false);
      }
    })();
  }, [load]);

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await load();
    } catch {
      /* keep prior data */
    } finally {
      setRefreshing(false);
    }
  };

  const actions: { icon: IonIconName; label: string; color: string; href: string }[] = [
    { icon: "calendar", label: "Mark Attendance", color: Colors.light.success, href: "/(teacher)/mark-attendance" },
    { icon: "document-text", label: "Assignments", color: Colors.light.accent, href: "/(teacher)/assignments" },
    { icon: "school", label: "Grades", color: Colors.light.gold, href: "/(teacher)/grades" },
    { icon: "time", label: "Schedule", color: Colors.light.primary, href: "/(teacher)/timetable" },
  ];

  if (loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color={Colors.light.accent} />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => void onRefresh()} />}
    >
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hello, {user?.first_name}!</Text>
          <Text style={styles.subGreeting}>Manage your classes efficiently</Text>
        </View>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats.my_assignments ?? 0}</Text>
          <Text style={styles.statLabel}>Assignments</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats.classes_today ?? schedule.length}</Text>
          <Text style={styles.statLabel}>Today&apos;s Classes</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats.pending_grading ?? 0}</Text>
          <Text style={styles.statLabel}>To Grade</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Quick Actions</Text>
      <View style={styles.actionsContainer}>
        {actions.map((action) => (
          <TouchableOpacity
            key={action.label}
            style={styles.actionButton}
            onPress={() => router.push(action.href as never)}
          >
            <View style={[styles.actionIcon, { backgroundColor: `${action.color}15` }]}>
              <Ionicons name={action.icon} size={24} color={action.color} />
            </View>
            <Text style={styles.actionLabel}>{action.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.sectionTitle}>Today&apos;s Classes</Text>
      <View style={styles.classesContainer}>
        {schedule.length === 0 ? (
          <Text style={styles.empty}>No classes scheduled today.</Text>
        ) : (
          schedule.map((cls) => {
            const status = slotStatus(cls.start_time, cls.end_time);
            return (
              <View key={cls.id} style={[styles.classItem, status === "ongoing" && styles.classItemActive]}>
                <View style={styles.classTime}>
                  <Text style={styles.classTimeText}>{cls.start_time?.slice(0, 5)}</Text>
                </View>
                <View style={styles.classContent}>
                  <Text style={styles.classSubject}>{cls.subject_name}</Text>
                  <Text style={styles.classDetails}>
                    {cls.section} · {cls.room_number || "—"}
                  </Text>
                </View>
                {status === "ongoing" ? (
                  <View style={styles.statusBadge}>
                    <Text style={styles.statusText}>Now</Text>
                  </View>
                ) : null}
                {status === "completed" ? (
                  <Ionicons name="checkmark-circle" size={20} color={Colors.light.success} />
                ) : null}
              </View>
            );
          })
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.light.bg },
  loading: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: Colors.light.bg },
  header: {
    paddingHorizontal: Spacing.xl,
    paddingTop: Spacing["2xl"] + 20,
    paddingBottom: Spacing.lg,
    backgroundColor: Colors.light.surface,
  },
  greeting: { fontSize: 24, fontWeight: "bold", color: Colors.light.text },
  subGreeting: { fontSize: 14, color: Colors.light.textMuted, marginTop: Spacing.xs },
  statsContainer: { flexDirection: "row", padding: Spacing.xl, gap: Spacing.base },
  statCard: {
    flex: 1,
    backgroundColor: Colors.light.surface,
    borderRadius: 16,
    padding: Spacing.base,
    alignItems: "center",
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  statValue: { fontSize: 24, fontWeight: "bold", color: Colors.light.accent },
  statLabel: { fontSize: 12, color: Colors.light.textMuted, marginTop: Spacing.xs, textAlign: "center" },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: Colors.light.text,
    marginHorizontal: Spacing.xl,
    marginTop: Spacing.lg,
    marginBottom: Spacing.base,
  },
  actionsContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    paddingHorizontal: Spacing.xl,
    gap: Spacing.base,
  },
  actionButton: {
    width: "47%",
    backgroundColor: Colors.light.surface,
    borderRadius: 16,
    padding: Spacing.base,
    alignItems: "center",
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  actionIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: "center",
    alignItems: "center",
  },
  actionLabel: {
    fontSize: 13,
    fontWeight: "500",
    color: Colors.light.text,
    marginTop: Spacing.sm,
    textAlign: "center",
  },
  classesContainer: { paddingHorizontal: Spacing.xl, paddingBottom: Spacing["2xl"] },
  empty: { fontSize: 14, color: Colors.light.textMuted },
  classItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.light.surface,
    borderRadius: 12,
    padding: Spacing.base,
    marginBottom: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  classItemActive: { borderColor: Colors.light.accent, backgroundColor: `${Colors.light.accent}08` },
  classTime: { width: 70 },
  classTimeText: { fontSize: 12, fontWeight: "600", color: Colors.light.textMuted },
  classContent: { flex: 1 },
  classSubject: { fontSize: 14, fontWeight: "600", color: Colors.light.text },
  classDetails: { fontSize: 12, color: Colors.light.textMuted, marginTop: 2 },
  statusBadge: {
    backgroundColor: Colors.light.accent,
    borderRadius: 8,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
  },
  statusText: { color: "#FFFFFF", fontSize: 10, fontWeight: "bold" },
});
