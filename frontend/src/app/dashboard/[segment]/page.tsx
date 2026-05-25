import { DashboardBySegment } from "@/components/dashboard/dashboard-by-segment";

type PageProps = {
  params: Promise<{ segment: string }>;
};

export default async function DashboardSegmentPage({ params }: PageProps) {
  const { segment } = await params;

  return <DashboardBySegment segment={segment} />;
}
