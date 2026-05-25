import { Redirect } from "expo-router";

/** Legacy `/login` path — onboarding starts at branded welcome. */
export default function LegacyLoginRedirect() {
  return <Redirect href="/welcome" />;
}
