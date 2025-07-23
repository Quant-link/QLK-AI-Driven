import { AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export function SlippageWarning() {
  return (
    <Badge className="bg-red-100 text-red-800 border-red-200">
      <AlertTriangle className="h-3 w-3 mr-1" />
      High
    </Badge>
  );
}