import { PageLayout } from "@/components/layout/PageLayout";
import { SwapInterface } from "@/components/swap/SwapInterface";

export function Swap() {
  return (
    <PageLayout
      title="Token Swap"
      description="Swap tokens using the best available rates from multiple DEXs"
    >
      <SwapInterface />
    </PageLayout>
  );
}
