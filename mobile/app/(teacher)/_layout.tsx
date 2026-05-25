import { Ionicons } from "@expo/vector-icons";
import { Redirect, Tabs } from "expo-router";

import { Colors } from "@/constants/Colors";
import { useAuthStore } from "@/store/auth-store";

function normalizeRole(role: string | undefined) {
  return role?.trim().toUpperCase() ?? "";
}

export default function TeacherLayout() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const user = useAuthStore((s) => s.user);

  if (isLoading) return null;

  if (!isAuthenticated) {
    return <Redirect href="/welcome" />;
  }

  if (!["TEACHER", "HOD"].includes(normalizeRole(user?.role))) {
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
        name="mark-attendance"
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
        name="grades"
        options={{
          title: "Grades",
          tabBarIcon: ({ color, size }) => <Ionicons name="school" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="timetable"
        options={{
          title: "Schedule",
          tabBarIcon: ({ color, size }) => <Ionicons name="time" size={size} color={color} />,
        }}
      />
    </Tabs>
  );
}
