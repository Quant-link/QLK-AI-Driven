import { PageLayout } from "@/components/layout/PageLayout";
import { RouteTable } from "@/components/routes/RouteTable";

export function Routes() {
  return (
    <PageLayout
      title="Optimal Routes"
      description="Smart routing analysis for optimal swap paths and gas efficiency"
    >
      <RouteTable />
    </PageLayout>
  );
}
