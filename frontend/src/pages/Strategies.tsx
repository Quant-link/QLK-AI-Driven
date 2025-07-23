import { PageLayout } from "@/components/layout/PageLayout";
import { DCAStatusCard } from "@/components/strategies/DCAStatusCard";
import { StrategyLogTable } from "@/components/strategies/StrategyLogTable";

export function Strategies() {
  return (
    <PageLayout
      title="Trading Strategies"
      description="Monitor TWAP, DCA, and arbitrage strategy performance and execution logs"
    >
      <DCAStatusCard />

      <StrategyLogTable />
    </PageLayout>
  );
}
