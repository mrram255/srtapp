import { Ionicons } from "@expo/vector-icons";
import { Redirect, Tabs } from "expo-router";

import { Colors } from "@/constants/Colors";
import { useAuthStore } from "@/store/auth-store";

function normalizeRole(role: string | undefined) {
  return role?.trim().toUpperCase() ?? "";
}

export default function StudentLayout() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const user = useAuthStore((s) => s.user);

  if (isLoading) return null;

  if (!isAuthenticated) {
    return <Redirect href="/welcome" />;
  }

  if (normalizeRole(user?.role) !== "STUDENT") {
    return <Redirect href="/" />;
  }

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: Colors.light.tabBar,
          borderTopColor: Colors.light.border,
          height: 60,
          paddingBottom: 8,
        },
        tabBarActiveTintColor: Colors.light.tabBarActive,
        tabBarInactiveTintColor: Colors.light.tabBarInactive,
      }}
    >
      <Tabs.Screen
        name="dashboard"
        options={{
          title: "Home",
          tabBarIcon: ({ color, size }) => <Ionicons name="home" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="attendance"
        options={{
          title: "Attendance",
          tabBarIcon: ({ color, size }) => <Ionicons name="calendar" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="assignments"
        options={{
          title: "Assignments",
          tabBarIcon: ({ color, size }) => <Ionicons name="document-text" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="results"
        options={{
          title: "Results",
          tabBarIcon: ({ color, size }) => <Ionicons name="trophy" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Profile",
          tabBarIcon: ({ color, size }) => <Ionicons name="person" size={size} color={color} />,
        }}
      />
    </Tabs>
  );
}
