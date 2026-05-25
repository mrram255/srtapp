import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { Linking, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { Colors } from "@/constants/Colors";
import { BorderRadius, Spacing } from "@/constants/Spacing";

const SUPPORT =
  typeof process.env.EXPO_PUBLIC_REGISTRATION_EMAIL === "string"
    ? process.env.EXPO_PUBLIC_REGISTRATION_EMAIL.trim()
    : "registration@srtcollege.ac.in";

export default function SignupScreen() {
  const router = useRouter();

  const openMail = () => {
    const url = `mailto:${encodeURIComponent(SUPPORT)}?subject=${encodeURIComponent(
      "SRT College mobile app — new student / staff account",
    )}&body=${encodeURIComponent("Name:\nPhone:\nRole (Student/Staff):\n")}`;
    void Linking.openURL(url);
  };

  return (
    <SafeAreaView style={styles.safe} edges={["top", "bottom"]}>
      <View style={styles.topBar}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn} accessibilityRole="button">
          <Ionicons name="arrow-back" size={22} color={Colors.light.text} />
        </TouchableOpacity>
        <Text style={styles.topTitle}>New account</Text>
      </View>

      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <Text style={styles.heading}>Welcome to SRT College, Dhamri</Text>
        <Text style={styles.body}>
          Campus accounts are created by the college registration office. Students and staff receive login
          credentials once their record is active in the MIS.
        </Text>
        <Text style={styles.body}>
          If you do not have portal access yet, contact registration with your enrolment / staff details — a
          self-service sign-up API may be enabled later.
        </Text>

        <TouchableOpacity style={styles.mailBtn} onPress={openMail} activeOpacity={0.9}>
          <Ionicons name="mail-outline" size={20} color="#fff" />
          <Text style={styles.mailBtnLabel}>Email registration office</Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={() => router.replace("/(auth)/login")}>
          <Text style={styles.loginLink}>
            Already have an account? <Text style={styles.loginLinkBold}>Sign in</Text>
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.light.bg },
  topBar: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.sm,
    paddingHorizontal: Spacing.md,
    paddingBottom: Spacing.sm,
  },
  backBtn: { padding: Spacing.sm },
  topTitle: { fontSize: 18, fontWeight: "700", color: Colors.light.text },
  scroll: { padding: Spacing.xl, paddingTop: Spacing.sm },
  heading: {
    fontSize: 22,
    fontWeight: "800",
    color: Colors.light.primary,
    marginBottom: Spacing.base,
  },
  body: {
    fontSize: 15,
    lineHeight: 22,
    color: Colors.light.textSecond,
    marginBottom: Spacing.base,
  },
  mailBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: Spacing.sm,
    backgroundColor: Colors.light.accent,
    paddingVertical: Spacing.base,
    borderRadius: BorderRadius.lg,
    marginTop: Spacing.md,
  },
  mailBtnLabel: { color: "#fff", fontSize: 16, fontWeight: "700" },
  loginLink: {
    textAlign: "center",
    marginTop: Spacing["2xl"],
    fontSize: 15,
    color: Colors.light.textSecond,
  },
  loginLinkBold: { color: Colors.light.accent, fontWeight: "700" },
});
