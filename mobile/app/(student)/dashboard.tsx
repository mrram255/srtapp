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

type DashboardData = {
  attendance_percentage?: number;
  pending_assignments?: number;
  upcoming_exams?: number;
  fee_status?: string;
  recent_notifications?: { title: string; created_at?: string }[];
};

type TimetableEntry = {
  id: string;
  subject_name: string;
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
  const startMin = toMin(start);
  const endMin = toMin(end);
  if (nowMin >= endMin) return "completed";
  if (nowMin >= startMin) return "ongoing";
  return "upcoming";
}

interface QuickActionProps {
  icon: IonIconName;
  label: string;
  color: string;
  onPress: () => void;
}

function QuickAction({ icon, label, color, onPress }: QuickActionProps) {
  return (
    <TouchableOpacity style={styles.quickAction} onPress={onPress}>
      <View style={[styles.quickActionIcon, { backgroundColor: `${color}20` }]}>
        <Ionicons name={icon} size={24} color={color} />
      </View>
      <Text style={styles.quickActionLabel}>{label}</Text>
    </TouchableOpacity>
  );
}

export default function StudentDashboard() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const [data, setData] = useState<DashboardData | null>(null);
  const [schedule, setSchedule] = useState<TimetableEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    const [dashRes, todayRes] = await Promise.all([
      api.get<ApiEnvelope<DashboardData>>("/students/dashboard/"),
      api.get<ApiEnvelope<TimetableEntry[]>>("/academics/timetable/today/").catch(() => ({ data: { data: [] } })),
    ]);
    setData(dashRes.data?.data ?? {});
    const raw = todayRes.data?.data;
    setSchedule(Array.isArray(raw) ? raw : []);
  }, []);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      try {
        await load();
      } catch {
        setData({});
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

  if (loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color={Colors.light.accent} />
      </View>
    );
  }

  const attendance = data?.attendance_percentage ?? 0;
  const pending = data?.pending_assignments ?? 0;
  const exams = data?.upcoming_exams ?? 0;
  const notifications = data?.recent_notifications ?? [];

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => void onRefresh()} />}
    >
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hello, {user?.first_name}!</Text>
          <Text style={styles.subGreeting}>Have a great day ahead</Text>
        </View>
        <TouchableOpacity style={styles.notificationBtn}>
          <Ionicons name="notifications-outline" size={24} color={Colors.light.text} />
          {notifications.length > 0 ? <View style={styles.badge} /> : null}
        </TouchableOpacity>
      </View>

      <View style={styles.statsContainer}>
        <View style={[styles.statCard, { backgroundColor: `${Colors.light.success}15` }]}>
          <Ionicons name="checkmark-circle" size={28} color={Colors.light.success} />
          <Text style={styles.statValue}>{attendance}%</Text>
          <Text style={styles.statLabel}>Attendance</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: `${Colors.light.accent}15` }]}>
          <Ionicons name="document-text" size={28} color={Colors.light.accent} />
          <Text style={styles.statValue}>{pending}</Text>
          <Text style={styles.statLabel}>Pending Work</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: `${Colors.light.warning}15` }]}>
          <Ionicons name="calendar" size={28} color={Colors.light.warning} />
          <Text style={styles.statValue}>{exams}</Text>
          <Text style={styles.statLabel}>Upcoming Exams</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Quick Actions</Text>
      <View style={styles.quickActionsGrid}>
        <QuickAction
          icon="calendar"
          label="Attendance"
          color={Colors.light.success}
          onPress={() => router.push("/(student)/attendance")}
        />
        <QuickAction
          icon="document-text"
          label="Assignments"
          color={Colors.light.accent}
          onPress={() => router.push("/(student)/assignments")}
        />
        <QuickAction
          icon="trophy"
          label="Results"
          color={Colors.light.primary}
          onPress={() => router.push("/(student)/results")}
        />
        <QuickAction icon="person" label="Profile" color={Colors.light.gold} onPress={() => router.push("/(student)/profile")} />
      </View>

      <Text style={styles.sectionTitle}>Today&apos;s Schedule</Text>
      <View style={styles.scheduleContainer}>
        {schedule.length === 0 ? (
          <Text style={styles.empty}>No classes scheduled today.</Text>
        ) : (
          schedule.map((item, index) => {
            const status = slotStatus(item.start_time, item.end_time);
            return (
              <View key={item.id} style={styles.scheduleItem}>
                <View style={styles.scheduleTime}>
                  <Text style={styles.scheduleTimeText}>{item.start_time?.slice(0, 5)}</Text>
                  <View style={[styles.scheduleLine, index < schedule.length - 1 && styles.scheduleLineActive]} />
                </View>
                <View
                  style={[styles.scheduleContent, status === "ongoing" && styles.scheduleContentActive]}
                >
                  <Text style={styles.scheduleSubject}>{item.subject_name}</Text>
                  <Text style={styles.scheduleRoom}>{item.room_number || "—"}</Text>
                  {status === "ongoing" ? (
                    <View style={styles.ongoingBadge}>
                      <Text style={styles.ongoingText}>Now</Text>
                    </View>
                  ) : null}
                </View>
              </View>
            );
          })
        )}
      </View>

      {notifications.length > 0 ? (
        <>
          <Text style={styles.sectionTitle}>Recent Updates</Text>
          <View style={styles.notificationsContainer}>
            {notifications.slice(0, 5).map((notif, index) => (
              <View key={`${notif.title}-${index}`} style={styles.notificationItem}>
                <View style={[styles.notificationDot, { backgroundColor: Colors.light.info }]} />
                <View style={styles.notificationContent}>
                  <Text style={styles.notificationTitle}>{notif.title}</Text>
                </View>
              </View>
            ))}
          </View>
        </>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.light.bg },
  loading: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: Colors.light.bg },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: Spacing.xl,
    paddingTop: Spacing["2xl"] + 20,
    paddingBottom: Spacing.lg,
    backgroundColor: Colors.light.surface,
  },
  greeting: { fontSize: 24, fontWeight: "bold", color: Colors.light.text },
  subGreeting: { fontSize: 14, color: Colors.light.textMuted, marginTop: Spacing.xs },
  notificationBtn: { padding: Spacing.sm, position: "relative" },
  badge: {
    position: "absolute",
    top: Spacing.sm,
    right: Spacing.sm,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: Colors.light.accent,
  },
  statsContainer: { flexDirection: "row", padding: Spacing.xl, gap: Spacing.base },
  statCard: { flex: 1, borderRadius: 16, padding: Spacing.base, alignItems: "center" },
  statValue: { fontSize: 20, fontWeight: "bold", color: Colors.light.text, marginTop: Spacing.sm },
  statLabel: { fontSize: 12, color: Colors.light.textMuted, marginTop: Spacing.xs },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: Colors.light.text,
    marginHorizontal: Spacing.xl,
    marginTop: Spacing.lg,
    marginBottom: Spacing.base,
  },
  quickActionsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    paddingHorizontal: Spacing.xl,
    gap: Spacing.base,
  },
  quickAction: { width: "22%", alignItems: "center", marginBottom: Spacing.base },
  quickActionIcon: {
    width: 56,
    height: 56,
    borderRadius: 16,
    justifyContent: "center",
    alignItems: "center",
  },
  quickActionLabel: { fontSize: 12, color: Colors.light.text, marginTop: Spacing.xs, textAlign: "center" },
  scheduleContainer: { paddingHorizontal: Spacing.xl },
  empty: { fontSize: 14, color: Colors.light.textMuted, marginBottom: Spacing.base },
  scheduleItem: { flexDirection: "row", marginBottom: Spacing.base },
  scheduleTime: { alignItems: "center", width: 50 },
  scheduleTimeText: { fontSize: 12, fontWeight: "600", color: Colors.light.textMuted },
  scheduleLine: { width: 2, flex: 1, backgroundColor: Colors.light.border, marginTop: Spacing.xs },
  scheduleLineActive: { backgroundColor: Colors.light.accent },
  scheduleContent: {
    flex: 1,
    backgroundColor: Colors.light.surface,
    borderRadius: 12,
    padding: Spacing.base,
    marginLeft: Spacing.base,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  scheduleContentActive: { borderColor: Colors.light.accent, backgroundColor: `${Colors.light.accent}08` },
  scheduleSubject: { fontSize: 14, fontWeight: "600", color: Colors.light.text },
  scheduleRoom: { fontSize: 12, color: Colors.light.textMuted, marginTop: Spacing.xs },
  ongoingBadge: {
    position: "absolute",
    top: Spacing.base,
    right: Spacing.base,
    backgroundColor: Colors.light.accent,
    borderRadius: 8,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
  },
  ongoingText: { color: "#FFFFFF", fontSize: 10, fontWeight: "bold" },
  notificationsContainer: { paddingHorizontal: Spacing.xl, paddingBottom: Spacing["2xl"] },
  notificationItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.light.surface,
    borderRadius: 12,
    padding: Spacing.base,
    marginBottom: Spacing.sm,
  },
  notificationDot: { width: 8, height: 8, borderRadius: 4, marginRight: Spacing.base },
  notificationContent: { flex: 1 },
  notificationTitle: { fontSize: 14, fontWeight: "500", color: Colors.light.text },
});
