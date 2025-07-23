import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertCircle, CheckCircle, Info, XCircle, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NotificationProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  className?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function Notification({ 
  type, 
  title, 
  message, 
  className, 
  dismissible = false,
  onDismiss,
  action
}: NotificationProps) {
  const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertCircle,
    info: Info,
  };

  const styles = {
    success: 'border-green-200 bg-green-50 text-green-900 dark:border-green-800 dark:bg-green-950 dark:text-green-100',
    error: 'border-red-200 bg-red-50 text-red-900 dark:border-red-800 dark:bg-red-950 dark:text-red-100',
    warning: 'border-yellow-200 bg-yellow-50 text-yellow-900 dark:border-yellow-800 dark:bg-yellow-950 dark:text-yellow-100',
    info: 'border-blue-200 bg-blue-50 text-blue-900 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-100',
  };

  const badgeStyles = {
    success: 'bg-green-100 text-green-800 border-green-200',
    error: 'bg-red-100 text-red-800 border-red-200',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    info: 'bg-blue-100 text-blue-800 border-blue-200',
  };

  const Icon = icons[type];

  return (
    <Alert className={cn(styles[type], 'relative', className)}>
      <Icon className="h-4 w-4" />
      <div className="flex-1">
        {title && (
          <AlertTitle className="flex items-center space-x-2">
            <span>{title}</span>
            <Badge variant="outline" className={badgeStyles[type]}>
              {type.toUpperCase()}
            </Badge>
          </AlertTitle>
        )}
        <AlertDescription className="mt-1">
          {message}
        </AlertDescription>
        {action && (
          <div className="mt-3">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={action.onClick}
              className="h-8"
            >
              {action.label}
            </Button>
          </div>
        )}
      </div>
      {dismissible && onDismiss && (
        <Button
          variant="ghost"
          size="sm"
          className="absolute top-2 right-2 h-6 w-6 p-0"
          onClick={onDismiss}
        >
          <X className="h-3 w-3" />
        </Button>
      )}
    </Alert>
  );
}