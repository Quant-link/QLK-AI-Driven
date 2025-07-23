import { PageLayout } from "@/components/layout/PageLayout";
import { TokenListTable } from "@/components/market-data/TokenListTable";
import { TokenChart } from "@/components/market-data/TokenChart";

export function MarketData() {
  return (
    <PageLayout
      title="Market Data"
      description="Comprehensive token analytics, price movements, and liquidity data"
    >
      <TokenChart tokenSymbol="ETH" />
      <TokenListTable />
    </PageLayout>
  );
}
