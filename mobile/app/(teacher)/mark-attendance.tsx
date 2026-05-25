import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { Colors } from "@/constants/Colors";
import { BorderRadius, Spacing } from "@/constants/Spacing";
import api from "@/lib/api";
import type { ApiEnvelope } from "@/lib/types";

type MarkStatus = "PRESENT" | "ABSENT" | "LATE" | "EXCUSED";

const STATUSES: MarkStatus[] = ["PRESENT", "ABSENT", "LATE", "EXCUSED"];

export default function TeacherMarkAttendanceScreen() {
  const insets = useSafeAreaInsets();
  const [teacherId, setTeacherId] = useState("");
  const [studentId, setStudentId] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [status, setStatus] = useState<MarkStatus>("PRESENT");
  const [period, setPeriod] = useState("1");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    void (async () => {
      try {
        const res = await api.get<ApiEnvelope<{ teacher_id: string }>>("/teachers/dashboard/");
        setTeacherId(res.data?.data?.teacher_id ?? "");
      } catch {
        /* teacher id optional until submit */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleSubmit = async () => {
    if (!studentId.trim() || !subjectId.trim()) {
      Alert.alert("Required", "Enter student and subject UUIDs.");
      return;
    }
    if (!teacherId) {
      Alert.alert("Profile", "Teacher profile not loaded. Try again.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await api.post<ApiEnvelope<{ created_or_updated: number }>>("/attendance/", [
        {
          student: studentId.trim(),
          subject: subjectId.trim(),
          teacher: teacherId,
          date: new Date().toISOString().split("T")[0],
          period: Number(period) || 1,
          status,
        },
      ]);
      Alert.alert("Saved", res.data.message ?? `Marked ${res.data.data?.created_or_updated ?? 1} row(s).`);
      setStudentId("");
    } catch (e: unknown) {
      Alert.alert("Failed", e instanceof Error ? e.message : "Could not mark attendance.");
    } finally {
      setSubmitting(false);
    }
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
      keyboardShouldPersistTaps="handled"
    >
      <Text style={styles.title}>Mark attendance</Text>
      <Text style={styles.sub}>Record attendance for a class period</Text>

      <Text style={styles.label}>Student UUID</Text>
      <TextInput
        style={styles.input}
        placeholder="Student ID"
        placeholderTextColor={Colors.light.textMuted}
        autoCapitalize="none"
        value={studentId}
        onChangeText={setStudentId}
      />

      <Text style={styles.label}>Subject UUID</Text>
      <TextInput
        style={styles.input}
        placeholder="Subject ID"
        placeholderTextColor={Colors.light.textMuted}
        autoCapitalize="none"
        value={subjectId}
        onChangeText={setSubjectId}
      />

      <Text style={styles.label}>Period</Text>
      <TextInput
        style={styles.input}
        keyboardType="number-pad"
        value={period}
        onChangeText={setPeriod}
      />

      <Text style={styles.label}>Status</Text>
      <View style={styles.statusRow}>
        {STATUSES.map((s) => (
          <TouchableOpacity
            key={s}
            style={[styles.chip, status === s && styles.chipActive]}
            onPress={() => setStatus(s)}
          >
            <Text style={[styles.chipText, status === s && styles.chipTextActive]}>{s}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity
        style={[styles.btn, submitting && styles.btnDisabled]}
        onPress={() => void handleSubmit()}
        disabled={submitting}
      >
        {submitting ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnLabel}>Save attendance</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: Colors.light.bg, paddingHorizontal: Spacing.xl },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: Colors.light.bg },
  title: { fontSize: 22, fontWeight: "700", color: Colors.light.text, marginBottom: Spacing.xs },
  sub: { fontSize: 14, color: Colors.light.textMuted, marginBottom: Spacing.lg },
  label: { fontSize: 13, fontWeight: "700", color: Colors.light.textSecond, marginBottom: Spacing.xs },
  input: {
    borderWidth: 1,
    borderColor: Colors.light.border,
    borderRadius: BorderRadius.lg,
    padding: Spacing.base,
    fontSize: 15,
    color: Colors.light.text,
    backgroundColor: Colors.light.surface,
    marginBottom: Spacing.base,
  },
  statusRow: { flexDirection: "row", flexWrap: "wrap", gap: Spacing.sm, marginBottom: Spacing.lg },
  chip: {
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
    borderRadius: BorderRadius.md,
    backgroundColor: Colors.light.surfaceMid,
  },
  chipActive: { backgroundColor: Colors.light.primary },
  chipText: { fontSize: 12, fontWeight: "600", color: Colors.light.textMuted },
  chipTextActive: { color: Colors.light.surface },
  btn: {
    backgroundColor: Colors.light.accent,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.lg,
    alignItems: "center",
  },
  btnDisabled: { opacity: 0.7 },
  btnLabel: { color: "#fff", fontWeight: "700", fontSize: 16 },
});
