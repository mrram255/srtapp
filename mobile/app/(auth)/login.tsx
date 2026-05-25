import { Ionicons } from "@expo/vector-icons";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { LinearGradient } from "expo-linear-gradient";
import { Redirect, useRouter } from "expo-router";
import { useCallback, useEffect, useState } from "react";
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
import { SafeAreaView } from "react-native-safe-area-context";

import { Colors } from "@/constants/Colors";
import { BorderRadius, Spacing } from "@/constants/Spacing";
import {
  biometricQuickLoginChallenge,
  hardwareBiometricsUsable,
  isBiometricLoginAvailable,
  markBiometricOfferHandled,
  saveBiometricCredentials,
  shouldOfferBiometricSetup,
} from "@/lib/biometric-auth";
import { djangoOriginFromApiV1Base } from "@/lib/django-origin";
import api from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";

type RoleTab = "student" | "teacher" | "admin";

const ROLE_PROMPT_KEY = "srtapp_mobile_last_role_tab";

export default function LoginScreen() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);

  const [role, setRole] = useState<RoleTab>("student");
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [bioReady, setBioReady] = useState(false);

  useEffect(() => {
    void (async () => {
      try {
        const saved = await AsyncStorage.getItem(ROLE_PROMPT_KEY);
        if (saved === "student" || saved === "teacher" || saved === "admin") setRole(saved);
      } catch {
        /* ignore */
      }
    })();
  }, []);

  useEffect(() => {
    void isBiometricLoginAvailable().then(setBioReady);
  }, []);

  useEffect(() => {
    void AsyncStorage.setItem(ROLE_PROMPT_KEY, role);
  }, [role]);

  if (!isLoading && isAuthenticated) {
    return <Redirect href="/" />;
  }

  const normalizedEmailForApi = (): string | null => {
    const trimmed = identifier.trim();
    if (!trimmed) {
      Alert.alert("Required", "Enter your college email.");
      return null;
    }
    if (!trimmed.includes("@")) {
      if (role === "student") {
        Alert.alert(
          "Registered email needed",
          "Portal sign-in uses the official college email linked to your MIS record. Ask registration if unsure.",
          [{ text: "OK" }],
        );
      } else {
        Alert.alert("Invalid email", "Enter a valid email address (must include @).", [{ text: "OK" }]);
      }
      return null;
    }
    return trimmed.toLowerCase();
  };

  const offerBiometricsAfterLogin = async (email: string, pwd: string) => {
    if (!(await hardwareBiometricsUsable())) return;
    if (!(await shouldOfferBiometricSetup())) return;

    Alert.alert("Faster login", "Use Face ID or fingerprint next time?", [
      {
        text: "Not now",
        style: "cancel",
        onPress: () => void markBiometricOfferHandled(),
      },
      {
        text: "Enable",
        onPress: () =>
          void (async () => {
            await saveBiometricCredentials(email, pwd);
            await markBiometricOfferHandled();
            setBioReady(true);
          })(),
      },
    ]);
  };

  const handleLogin = async () => {
    const email = normalizedEmailForApi();
    if (!email || !password.trim()) {
      if (email && !password.trim()) {
        Alert.alert("Error", "Please enter your password");
      }
      return;
    }

    setIsSubmitting(true);
    try {
      await login(email.trim(), password);
      router.replace("/");
      void offerBiometricsAfterLogin(email.trim(), password);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Invalid credentials";
      const hint =
        typeof __DEV__ !== "undefined" && __DEV__
          ? `\n\nBundled: ${process.env.EXPO_PUBLIC_API_URL ?? "(unset)"}\nIf wrong: unset EXPO_PUBLIC_API_URL; rm -rf .expo; restart Metro (-c).\nTap “Test Django /health/” below.`
          : "";
      Alert.alert("Login Failed", message + hint);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBiometric = useCallback(async () => {
    setIsSubmitting(true);
    try {
      const bundle = await biometricQuickLoginChallenge();
      if (!bundle?.email || !bundle.password) {
        setBioReady(await isBiometricLoginAvailable());
        return;
      }
      await login(bundle.email, bundle.password);
      router.replace("/");
    } catch (error: unknown) {
      Alert.alert(
        "Biometric login failed",
        error instanceof Error ? error.message : "Try password sign-in.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }, [login, router]);

  const tabs: { key: RoleTab; label: string }[] = [
    { key: "student", label: "Student" },
    { key: "teacher", label: "Teacher" },
    { key: "admin", label: "Admin" },
  ];

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <ScrollView keyboardShouldPersistTaps="handled" bounces={false} contentContainerStyle={styles.flexGrow}>
        <LinearGradient colors={[Colors.light.primary, Colors.light.secondary]} style={styles.hero}>
          <SafeAreaView edges={["top"]} style={styles.heroInner}>
            <TouchableOpacity style={styles.backWelcome} onPress={() => router.replace("/welcome")}>
              <Ionicons name="chevron-back" size={22} color={Colors.light.surface} />
              <Text style={styles.backWelcomeTxt}>Welcome</Text>
            </TouchableOpacity>
            <View style={styles.heroLogo}>
              <Ionicons name="school" size={40} color={Colors.light.gold} />
            </View>
            <Text style={styles.heroTitle}>SRT College, Dhamri</Text>
          </SafeAreaView>
        </LinearGradient>

        <View style={styles.card}>
          <TouchableOpacity style={styles.signupRow} onPress={() => router.push("/(auth)/signup")}>
            <Text style={styles.signupRowTxt}>
              New here? <Text style={styles.signupRowBold}>Sign up first</Text>
            </Text>
            <Ionicons name="chevron-forward" size={18} color={Colors.light.accent} />
          </TouchableOpacity>

          <Text style={styles.welcomeEmoji}>Welcome Back!</Text>
          <Text style={styles.welcomeHint}>Sign in to continue</Text>

          <View style={styles.roleRow}>
            {tabs.map(({ key, label }) => (
              <TouchableOpacity
                key={key}
                accessibilityRole="button"
                accessibilityState={{ selected: role === key }}
                style={[styles.roleChip, role === key && styles.roleChipActive]}
                onPress={() => setRole(key)}
              >
                <Text style={[styles.roleChipTxt, role === key && styles.roleChipTxtActive]}>{label}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.fieldLabel}>
            {role === "student" ? "Roll / college email" : "College email"}
          </Text>
          <View style={styles.inputWrap}>
            <Ionicons
              name={role === "student" ? "card-outline" : "mail-outline"}
              size={20}
              color={Colors.light.textMuted}
            />
            <TextInput
              style={styles.input}
              placeholder={role === "student" ? "e.g. 2021CS045 or you@student.srt.ac.in" : "staff@example.com"}
              placeholderTextColor={Colors.light.textMuted}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              value={identifier}
              onChangeText={setIdentifier}
            />
          </View>
          {role === "student" ? (
            <Text style={styles.fieldHint}>
              Server login uses your registered email. Add @ only if you have a full email; otherwise ask
              registration for the portal ID format.
            </Text>
          ) : null}

          <Text style={styles.fieldLabel}>Password</Text>
          <View style={styles.inputWrap}>
            <Ionicons name="lock-closed-outline" size={20} color={Colors.light.gold} />
            <TextInput
              style={styles.input}
              placeholder="••••••••"
              placeholderTextColor={Colors.light.textMuted}
              secureTextEntry={!showPassword}
              value={password}
              onChangeText={setPassword}
            />
            <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
              <Ionicons
                name={showPassword ? "eye-off-outline" : "eye-outline"}
                size={20}
                color={Colors.light.textMuted}
              />
            </TouchableOpacity>
          </View>

          <TouchableOpacity
            style={styles.forgot}
            onPress={() => router.push("/(auth)/forgot-password")}
          >
            <Text style={styles.forgotTxt}>Forgot Password?</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.signInBtn, isSubmitting && styles.signInDisabled]}
            onPress={() => void handleLogin()}
            disabled={isSubmitting}
            activeOpacity={0.94}
          >
            {isSubmitting ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <>
                <Text style={styles.signInTxt}>Sign In</Text>
                <Ionicons name="arrow-forward" size={20} color="#fff" />
              </>
            )}
          </TouchableOpacity>

          {bioReady ? (
            <TouchableOpacity
              style={styles.bioOutline}
              onPress={() => void handleBiometric()}
              disabled={isSubmitting}
            >
              <Ionicons name="finger-print-outline" size={22} color={Colors.light.accent} />
              <Text style={styles.bioOutlineTxt}>Sign in with biometrics</Text>
            </TouchableOpacity>
          ) : null}

          <View style={styles.dividerRow}>
            <View style={styles.divLine} />
            <Text style={styles.divTxt}>OR</Text>
            <View style={styles.divLine} />
          </View>
          <Text style={styles.orHint}>School email credentials from registration office.</Text>

          <Text style={styles.footerMuted}>Powered by Kiji Technology</Text>
        </View>

        {typeof __DEV__ !== "undefined" && __DEV__ ? (
          <View style={styles.devBox}>
            <Text style={styles.devText}>API base (bundled): {process.env.EXPO_PUBLIC_API_URL ?? "unset"}</Text>
            <TouchableOpacity
              style={styles.devButton}
              onPress={() =>
                void (async () => {
                  try {
                    const origin = djangoOriginFromApiV1Base(api.defaults.baseURL ?? "");
                    const res = await fetch(`${origin}/health/`, {
                      headers: { Accept: "application/json" },
                    });
                    const body = await res.text();
                    Alert.alert(`/health (${res.status})`, body.slice(0, 280));
                  } catch (e) {
                    Alert.alert("Cannot reach Django", e instanceof Error ? e.message : String(e));
                  }
                })()
              }
            >
              <Text style={styles.devButtonText}>Test Django /health/ (same as Chrome)</Text>
            </TouchableOpacity>
          </View>
        ) : null}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: Colors.light.bg },
  flexGrow: { flexGrow: 1 },
  hero: {
    paddingBottom: Spacing["3xl"],
    borderBottomLeftRadius: 28,
    borderBottomRightRadius: 28,
  },
  heroInner: {
    alignItems: "center",
    paddingHorizontal: Spacing.xl,
    paddingTop: Spacing.sm,
  },
  backWelcome: {
    alignSelf: "flex-start",
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    paddingVertical: Spacing.sm,
  },
  backWelcomeTxt: { color: Colors.light.surface, fontSize: 15, fontWeight: "600" },
  heroLogo: {
    width: 72,
    height: 72,
    borderRadius: 18,
    backgroundColor: `${Colors.light.surface}22`,
    justifyContent: "center",
    alignItems: "center",
    marginTop: Spacing.md,
    borderWidth: 1,
    borderColor: `${Colors.light.surface}44`,
  },
  heroTitle: {
    marginTop: Spacing.lg,
    fontSize: 22,
    fontWeight: "800",
    color: Colors.light.surface,
    textAlign: "center",
  },
  card: {
    marginHorizontal: Spacing.base,
    marginTop: -Spacing["2xl"],
    backgroundColor: Colors.light.surface,
    borderRadius: 24,
    padding: Spacing.xl,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 14,
    elevation: 6,
    borderWidth: 1,
    borderColor: Colors.light.border,
    marginBottom: Spacing.base,
  },
  signupRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: Spacing.sm,
    marginBottom: Spacing.base,
  },
  signupRowTxt: { fontSize: 14, color: Colors.light.textSecond },
  signupRowBold: { fontWeight: "700", color: Colors.light.accent },
  welcomeEmoji: {
    fontSize: 23,
    fontWeight: "800",
    color: Colors.light.text,
  },
  welcomeHint: {
    fontSize: 14,
    color: Colors.light.textMuted,
    marginBottom: Spacing.lg,
    marginTop: 4,
  },
  roleRow: {
    flexDirection: "row",
    gap: Spacing.sm,
    marginBottom: Spacing.lg,
  },
  roleChip: {
    flex: 1,
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.md,
    backgroundColor: Colors.light.surfaceMid,
    alignItems: "center",
  },
  roleChipActive: {
    backgroundColor: Colors.light.primary,
  },
  roleChipTxt: { fontSize: 13, fontWeight: "600", color: Colors.light.textMuted },
  roleChipTxtActive: { color: Colors.light.surface },
  fieldLabel: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.light.textSecond,
    marginBottom: Spacing.xs,
  },
  fieldHint: {
    fontSize: 12,
    color: Colors.light.textMuted,
    marginBottom: Spacing.base,
    lineHeight: 17,
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
    backgroundColor: Colors.light.bg,
    gap: Spacing.sm,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: Colors.light.text,
  },
  forgot: { alignSelf: "flex-end", marginBottom: Spacing.base },
  forgotTxt: { color: Colors.light.accent, fontSize: 14, fontWeight: "600" },
  signInBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: Spacing.sm,
    backgroundColor: Colors.light.accent,
    paddingVertical: Spacing.base,
    borderRadius: BorderRadius.lg,
  },
  signInDisabled: { opacity: 0.72 },
  signInTxt: { color: "#fff", fontSize: 17, fontWeight: "800" },
  bioOutline: {
    marginTop: Spacing.base,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: Spacing.sm,
    borderWidth: 1.5,
    borderColor: Colors.light.accent,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.lg,
    backgroundColor: `${Colors.light.accent}0d`,
  },
  bioOutlineTxt: { fontSize: 15, fontWeight: "700", color: Colors.light.accent },
  dividerRow: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: Spacing.lg,
    gap: Spacing.sm,
  },
  divLine: { flex: 1, height: 1, backgroundColor: Colors.light.border },
  divTxt: {
    fontSize: 11,
    fontWeight: "700",
    color: Colors.light.textMuted,
    letterSpacing: 1,
  },
  orHint: {
    fontSize: 12,
    color: Colors.light.textMuted,
    textAlign: "center",
    marginBottom: Spacing.sm,
  },
  footerMuted: {
    fontSize: 11,
    color: Colors.light.textMuted,
    textAlign: "center",
    marginTop: Spacing.md,
    opacity: 0.85,
  },
  devBox: {
    marginHorizontal: Spacing.xl,
    marginBottom: Spacing["2xl"],
    padding: Spacing.md,
    backgroundColor: "#f3f4f6",
    borderRadius: 8,
  },
  devText: { fontSize: 11, color: "#374151", marginBottom: Spacing.sm },
  devButton: {
    backgroundColor: "#e5e7eb",
    paddingVertical: Spacing.sm,
    borderRadius: 8,
    alignItems: "center",
  },
  devButtonText: { fontSize: 12, fontWeight: "600", color: Colors.light.primary },
});
