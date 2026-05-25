import { Ionicons } from "@expo/vector-icons";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
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

export default function ResetPasswordScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const params = useLocalSearchParams<{ email?: string }>();

  const [email, setEmail] = useState(typeof params.email === "string" ? params.email : "");
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedEmail.includes("@") || otp.trim().length < 6) {
      Alert.alert("Required", "Enter your email and the 6-digit OTP.");
      return;
    }
    if (newPassword.length < 12) {
      Alert.alert("Weak password", "Password must be at least 12 characters.");
      return;
    }
    if (newPassword !== confirmPassword) {
      Alert.alert("Mismatch", "Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await api.post<ApiEnvelope<unknown>>("/auth/password/reset/", {
        email: trimmedEmail,
        otp: otp.trim(),
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      Alert.alert("Success", res.data.message ?? "Password reset successful.", [
        { text: "Sign in", onPress: () => router.replace("/(auth)/login") },
      ]);
    } catch (error: unknown) {
      Alert.alert("Reset failed", error instanceof Error ? error.message : "Something went wrong.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <ScrollView
        contentContainerStyle={[styles.container, { paddingTop: insets.top + Spacing.base }]}
        keyboardShouldPersistTaps="handled"
      >
        <TouchableOpacity style={styles.backRow} onPress={() => router.back()} accessibilityRole="button">
          <Ionicons name="arrow-back" size={22} color={Colors.light.text} />
          <Text style={styles.backLabel}>Back</Text>
        </TouchableOpacity>

        <Text style={styles.title}>Reset password</Text>
        <Text style={styles.body}>Enter the OTP from your email and choose a new password.</Text>

        <Text style={styles.fieldLabel}>Email</Text>
        <View style={styles.inputWrap}>
          <Ionicons name="mail-outline" size={20} color={Colors.light.textMuted} />
          <TextInput
            style={styles.input}
            keyboardType="email-address"
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
          />
        </View>

        <Text style={styles.fieldLabel}>OTP code</Text>
        <View style={styles.inputWrap}>
          <Ionicons name="key-outline" size={20} color={Colors.light.textMuted} />
          <TextInput
            style={styles.input}
            keyboardType="number-pad"
            maxLength={6}
            value={otp}
            onChangeText={setOtp}
          />
        </View>

        <Text style={styles.fieldLabel}>New password</Text>
        <View style={styles.inputWrap}>
          <Ionicons name="lock-closed-outline" size={20} color={Colors.light.textMuted} />
          <TextInput
            style={styles.input}
            secureTextEntry={!showPassword}
            value={newPassword}
            onChangeText={setNewPassword}
          />
          <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
            <Ionicons
              name={showPassword ? "eye-off-outline" : "eye-outline"}
              size={20}
              color={Colors.light.textMuted}
            />
          </TouchableOpacity>
        </View>

        <Text style={styles.fieldLabel}>Confirm password</Text>
        <View style={styles.inputWrap}>
          <Ionicons name="lock-closed-outline" size={20} color={Colors.light.textMuted} />
          <TextInput
            style={styles.input}
            secureTextEntry
            value={confirmPassword}
            onChangeText={setConfirmPassword}
          />
        </View>

        <TouchableOpacity
          style={[styles.primary, isSubmitting && styles.primaryDisabled]}
          onPress={() => void handleSubmit()}
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.primaryLabel}>Reset password</Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: Colors.light.bg },
  container: {
    flexGrow: 1,
    paddingHorizontal: Spacing.xl,
    paddingBottom: Spacing["2xl"],
  },
  backRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.sm,
    marginBottom: Spacing.xl,
  },
  backLabel: { fontSize: 16, color: Colors.light.text, fontWeight: "500" },
  title: { fontSize: 26, fontWeight: "bold", color: Colors.light.text, marginBottom: Spacing.sm },
  body: {
    fontSize: 15,
    lineHeight: 22,
    color: Colors.light.textMuted,
    marginBottom: Spacing.xl,
  },
  fieldLabel: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.light.textSecond,
    marginBottom: Spacing.xs,
  },
  inputWrap: {
    flexDirection: "row",
    alignItems: "center",
    borderWidth: 1,
    borderColor: Colors.light.border,
    borderRadius: BorderRadius.lg,
    paddingHorizontal: Spacing.base,
    paddingVertical: Platform.OS === "ios" ? 14 : 10,
    marginBottom: Spacing.base,
    backgroundColor: Colors.light.surface,
    gap: Spacing.sm,
  },
  input: { flex: 1, fontSize: 16, color: Colors.light.text },
  primary: {
    marginTop: Spacing.base,
    backgroundColor: Colors.light.accent,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.lg,
    alignItems: "center",
  },
  primaryDisabled: { opacity: 0.72 },
  primaryLabel: { color: "#FFFFFF", fontWeight: "700", fontSize: 16 },
});
