import { LinearGradient } from "expo-linear-gradient";
import { useRouter } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { Image, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { Colors } from "@/constants/Colors";
import { Spacing } from "@/constants/Spacing";

/** First screen — college branding → navigate to login. Layout avoids `margin: auto` quirks on Android. */
export default function WelcomeScreen() {
  const router = useRouter();

  return (
    <LinearGradient colors={[Colors.light.primary, Colors.light.secondary]} style={styles.flex}>
      <StatusBar style="light" />
      <SafeAreaView style={styles.safe} edges={["top", "bottom"]}>
        <View style={styles.inner}>
          <View style={styles.topBlock}>
            <View style={styles.logoBadge}>
              <Image source={require("../assets/icon.png")} style={styles.logoImg} resizeMode="contain" />
            </View>
            <Text style={styles.collegeTitle}>SRT College, Dhamri</Text>
            <Text style={styles.tagline}>Your College, In Your Pocket</Text>

            <View style={styles.dots}>
              {[0, 1, 2].map((i) => (
                <View key={i} style={styles.dot} />
              ))}
            </View>
          </View>

          <View style={styles.bottomBlock}>
            <TouchableOpacity
              accessibilityRole="button"
              accessibilityLabel="Go to login page"
              style={styles.primaryBtn}
              onPress={() => router.push("/(auth)/login")}
              activeOpacity={0.92}
            >
              <Text style={styles.primaryBtnText}>Go to login page</Text>
            </TouchableOpacity>

            <Text style={styles.footer}>Powered by Kiji Technology</Text>
          </View>
        </View>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  safe: { flex: 1 },
  inner: {
    flex: 1,
    justifyContent: "space-between",
    paddingHorizontal: Spacing.xl,
    paddingBottom: Spacing.md,
    paddingTop: Spacing.md,
  },
  topBlock: {
    alignItems: "center",
    paddingTop: Spacing.xl,
  },
  logoBadge: {
    width: 112,
    height: 112,
    borderRadius: 28,
    backgroundColor: `${Colors.light.surface}33`,
    borderWidth: 1,
    borderColor: `${Colors.light.surface}55`,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: Spacing["2xl"],
  },
  logoImg: {
    width: 84,
    height: 84,
    borderRadius: 16,
  },
  collegeTitle: {
    fontSize: 26,
    fontWeight: "800",
    color: Colors.light.surface,
    textAlign: "center",
    letterSpacing: 0.2,
    marginBottom: Spacing.sm,
  },
  tagline: {
    fontSize: 16,
    color: Colors.light.surface,
    opacity: 0.88,
    textAlign: "center",
    paddingHorizontal: Spacing.lg,
  },
  dots: {
    flexDirection: "row",
    gap: 8,
    marginTop: Spacing["3xl"],
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: Colors.light.surface,
    opacity: 0.45,
  },
  bottomBlock: {
    width: "100%",
    gap: Spacing.lg,
  },
  primaryBtn: {
    width: "100%",
    backgroundColor: Colors.light.accent,
    paddingVertical: Spacing.base,
    paddingHorizontal: Spacing.xl,
    borderRadius: 14,
    alignSelf: "stretch",
  },
  primaryBtnText: {
    color: "#FFFFFF",
    fontSize: 17,
    fontWeight: "700",
    textAlign: "center",
  },
  footer: {
    textAlign: "center",
    color: Colors.light.surface,
    fontSize: 12,
    opacity: 0.75,
    paddingHorizontal: Spacing.base,
    paddingBottom: Spacing.sm,
  },
});
