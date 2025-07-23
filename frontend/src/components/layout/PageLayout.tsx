import { ReactNode } from 'react';
import { Separator } from '@/components/ui/separator';

interface PageLayoutProps {
  children: ReactNode;
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function PageLayout({ children, title, description, actions }: PageLayoutProps) {
  return (
    <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-6 xl:px-8 py-4 sm:py-6 lg:py-8">
      <div className="mb-6 sm:mb-8">
        <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
          <div className="space-y-1 sm:space-y-2">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-foreground">{title}</h1>
            {description && (
              <p className="text-sm sm:text-base text-muted-foreground max-w-2xl leading-relaxed">{description}</p>
            )}
          </div>
          {actions && (
            <div className="flex items-center space-x-2 flex-shrink-0">
              {actions}
            </div>
          )}
        </div>
        <Separator className="mt-4 sm:mt-6" />
      </div>
      <div className="space-y-4 sm:space-y-6 lg:space-y-8">
        {children}
      </div>
    </div>
  );
}