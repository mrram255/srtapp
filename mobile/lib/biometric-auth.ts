import AsyncStorage from "@react-native-async-storage/async-storage";
import * as LocalAuthentication from "expo-local-authentication";
import * as SecureStore from "expo-secure-store";

import {
  BIO_EMAIL_KEY,
  BIO_ENABLED_KEY,
  BIO_PASSWORD_KEY,
} from "@/lib/secure-keys";

const PROMPT_ONCE_KEY = "srtapp_biometric_offer_shown";

export async function isBiometricLoginAvailable(): Promise<boolean> {
  try {
    if (!(await LocalAuthentication.hasHardwareAsync())) return false;
    if (!(await LocalAuthentication.isEnrolledAsync())) return false;
    const enabled = await SecureStore.getItemAsync(BIO_ENABLED_KEY);
    if (enabled !== "true") return false;
    const email = await SecureStore.getItemAsync(BIO_EMAIL_KEY);
    const password = await SecureStore.getItemAsync(BIO_PASSWORD_KEY);
    return !!(email && password);
  } catch {
    return false;
  }
}

/** Run before reading stored credentials — device auth prompt. */
export async function authenticateWithBiometrics(): Promise<boolean> {
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: "Sign in to SRT College",
    cancelLabel: "Cancel",
    disableDeviceFallback: false,
    fallbackLabel: "Use password",
  });
  return result.success === true;
}

export async function saveBiometricCredentials(email: string, password: string): Promise<void> {
  await SecureStore.setItemAsync(BIO_EMAIL_KEY, email.trim());
  await SecureStore.setItemAsync(BIO_PASSWORD_KEY, password);
  await SecureStore.setItemAsync(BIO_ENABLED_KEY, "true");
}

export async function clearBiometricCredentials(): Promise<void> {
  await SecureStore.deleteItemAsync(BIO_EMAIL_KEY).catch(() => undefined);
  await SecureStore.deleteItemAsync(BIO_PASSWORD_KEY).catch(() => undefined);
  await SecureStore.deleteItemAsync(BIO_ENABLED_KEY).catch(() => undefined);
}

/**
 * Reads email/password after biometric success. Call only after biometric prompt passes.
 */
export async function loadBiometricCredentialBundle(): Promise<{
  email: string;
  password: string;
} | null> {
  try {
    const email = await SecureStore.getItemAsync(BIO_EMAIL_KEY);
    const password = await SecureStore.getItemAsync(BIO_PASSWORD_KEY);
    if (!email || !password) return null;
    return { email, password };
  } catch {
    return null;
  }
}

/** True if hardware biometric exists – used to decide whether we offer signup setup. */
export async function hardwareBiometricsUsable(): Promise<boolean> {
  try {
    if (!(await LocalAuthentication.hasHardwareAsync())) return false;
    return LocalAuthentication.isEnrolledAsync();
  } catch {
    return false;
  }
}

/** User chose “Later” → still mark so we do not nag every login. */
export async function markBiometricOfferHandled(): Promise<void> {
  await AsyncStorage.setItem(PROMPT_ONCE_KEY, "1");
}

/** Show “Enable Face ID / fingerprint?” prompt at most once (until fresh install). */
export async function shouldOfferBiometricSetup(): Promise<boolean> {
  const done = await AsyncStorage.getItem(PROMPT_ONCE_KEY);
  return done !== "1";
}

/** Device auth → return stored creds. `null` if disabled, cancelled, or missing. */
export async function biometricQuickLoginChallenge(): Promise<{
  email: string;
  password: string;
} | null> {
  const enabled = await SecureStore.getItemAsync(BIO_ENABLED_KEY);
  if (enabled !== "true") return null;

  const ok = await authenticateWithBiometrics();
  if (!ok) return null;

  return loadBiometricCredentialBundle();
}
