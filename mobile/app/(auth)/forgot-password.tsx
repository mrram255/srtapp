import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
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

export default function ForgotPasswordScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    const trimmed = email.trim().toLowerCase();
    if (!trimmed.includes("@")) {
      Alert.alert("Invalid email", "Enter a valid email address.");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await api.post<ApiEnvelope<unknown>>("/auth/password/forgot/", { email: trimmed });
      Alert.alert("Check your email", res.data.message ?? "If this email exists, OTP has been sent.", [
        { text: "Enter OTP", onPress: () => router.push({ pathname: "/(auth)/reset-password", params: { email: trimmed } }) },
        { text: "OK" },
      ]);
    } catch (error: unknown) {
      Alert.alert("Request failed", error instanceof Error ? error.message : "Something went wrong.");
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

        <Text style={styles.title}>Forgot password</Text>
        <Text style={styles.body}>
          Enter your college email. We will send a one-time code to reset your password.
        </Text>

        <Text style={styles.fieldLabel}>Email address</Text>
        <View style={styles.inputWrap}>
          <Ionicons name="mail-outline" size={20} color={Colors.light.textMuted} />
          <TextInput
            style={styles.input}
            placeholder="you@college.edu"
            placeholderTextColor={Colors.light.textMuted}
            keyboardType="email-address"
            autoCapitalize="none"
            autoCorrect={false}
            value={email}
            onChangeText={setEmail}
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
            <Text style={styles.primaryLabel}>Send reset code</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.linkRow}
          onPress={() => router.push("/(auth)/reset-password")}
        >
          <Text style={styles.linkText}>
            Have a code? <Text style={styles.linkBold}>Reset password</Text>
          </Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.secondary} onPress={() => router.replace("/(auth)/login")}>
          <Text style={styles.secondaryLabel}>Return to sign in</Text>
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
  title: {
    fontSize: 26,
    fontWeight: "bold",
    color: Colors.light.text,
    marginBottom: Spacing.sm,
  },
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
    marginBottom: Spacing.lg,
    backgroundColor: Colors.light.surface,
    gap: Spacing.sm,
  },
  input: { flex: 1, fontSize: 16, color: Colors.light.text },
  primary: {
    backgroundColor: Colors.light.accent,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.lg,
    alignItems: "center",
  },
  primaryDisabled: { opacity: 0.72 },
  primaryLabel: { color: "#FFFFFF", fontWeight: "700", fontSize: 16 },
  linkRow: { marginTop: Spacing.lg, alignItems: "center" },
  linkText: { fontSize: 14, color: Colors.light.textMuted },
  linkBold: { fontWeight: "700", color: Colors.light.accent },
  secondary: { marginTop: Spacing.base, alignSelf: "center", padding: Spacing.sm },
  secondaryLabel: { color: Colors.light.textMuted, fontSize: 14, fontWeight: "600" },
});
