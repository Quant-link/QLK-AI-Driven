import React, { useState, useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import {
  BarChart3,
  TrendingUp,
  Route,
  Settings,
  Activity,
  Zap,
  Bell,
  User,
  Menu,
  X
} from 'lucide-react';
import logoSvg from '@/assets/logo.svg';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface SystemStatus {
  isActive: boolean;
  successRate: number;
  activeArbitrages: number;
}

const navigation: NavigationItem[] = [
  { name: 'Dashboard', href: '/', icon: BarChart3 },
  { name: 'Market Data', href: '/market-data', icon: TrendingUp },
  { name: 'Routes', href: '/routes', icon: Route },
  { name: 'Strategies', href: '/strategies', icon: Settings },
];

const systemStatus: SystemStatus = {
  isActive: true,
  successRate: 94.7,
  activeArbitrages: 3,
};

export function Navbar(): JSX.Element {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);

  const toggleMobileMenu = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsMobileMenuOpen(prev => !prev);
  }, []);

  const closeMobileMenu = useCallback((e?: React.MouseEvent) => {
    if (e) e.preventDefault();
    setIsMobileMenuOpen(false);
  }, []);

  const renderNavigationItem = useCallback((item: NavigationItem, isMobile: boolean = false) => {
    const Icon = item.icon;
    const isActive = location.pathname === item.href;
    
    return (
      <Link
        key={item.name}
        to={item.href}
        onClick={isMobile ? closeMobileMenu : undefined}
        className={cn(
          'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
          isMobile 
            ? 'text-base' 
            : 'xl:px-4 xl:space-x-2',
          isActive
            ? 'bg-primary text-primary-foreground shadow-sm'
            : 'text-muted-foreground hover:text-foreground hover:bg-accent'
        )}
      >
        <Icon className="h-4 w-4 xl:h-5 xl:w-5 flex-shrink-0" />
        <span className={cn(isMobile ? 'block' : 'hidden xl:inline')}>
          {item.name}
        </span>
      </Link>
    );
  }, [location.pathname, closeMobileMenu]);

  const renderSystemStatus = useCallback(() => (
    <div className="flex items-center space-x-4 2xl:space-x-6">
      <div className="flex items-center space-x-2 text-xs xl:text-sm">
        <div className={cn(
          "h-2 w-2 rounded-full",
          systemStatus.isActive ? "bg-green-500 animate-pulse" : "bg-red-500"
        )} />
        <span className="text-muted-foreground hidden 2xl:inline">
          {systemStatus.isActive ? 'System Active' : 'System Inactive'}
        </span>
        <Badge variant="secondary" className="text-xs">
          <span className="hidden 2xl:inline">{systemStatus.successRate}% Success</span>
          <span className="2xl:hidden">{systemStatus.successRate}%</span>
        </Badge>
      </div>
      
      <div className="flex items-center space-x-2 text-xs xl:text-sm text-muted-foreground">
        <Zap className="h-4 w-4 text-yellow-500" />
        <span className="hidden 2xl:inline">{systemStatus.activeArbitrages} Active Arbitrages</span>
        <span className="2xl:hidden">{systemStatus.activeArbitrages} Active</span>
      </div>
    </div>
  ), []);

  const renderMobileStats = useCallback(() => (
    <div className="border-t px-3 py-3 space-y-2">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center space-x-2">
          <div className={cn(
            "h-2 w-2 rounded-full",
            systemStatus.isActive ? "bg-green-500 animate-pulse" : "bg-red-500"
          )} />
          <span className="text-muted-foreground">System Active</span>
        </div>
        <Badge variant="secondary" className="text-xs">{systemStatus.successRate}%</Badge>
      </div>
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center space-x-2">
          <Zap className="h-4 w-4 text-yellow-500" />
          <span className="text-muted-foreground">Active Arbitrages</span>
        </div>
        <Badge variant="outline">{systemStatus.activeArbitrages}</Badge>
      </div>
    </div>
  ), []);

  return (
    <nav className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
        <div className="flex justify-between items-center h-14 sm:h-16">
          {/* Logo Section */}
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <img
                src={logoSvg}
                alt="QuantLink Logo"
                className="h-8 sm:h-10 w-auto"
              />
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden lg:block ml-6 xl:ml-10">
              <div className="flex items-baseline space-x-1 xl:space-x-2">
                {navigation.map(item => renderNavigationItem(item))}
              </div>
            </div>
          </div>
          
          {/* Right Section */}
          <div className="flex items-center space-x-2 sm:space-x-3 lg:space-x-4">
            {/* System Status - Desktop Only */}
            <div className="hidden xl:flex">
              {renderSystemStatus()}
            </div>

            {/* Notifications */}
            <Button variant="ghost" size="sm" className="relative h-8 w-8 sm:h-9 sm:w-9 hover:bg-primary/10 hover:text-primary">
              <Bell className="h-4 w-4" />
              <Badge className="absolute -top-1 -right-1 h-4 w-4 sm:h-5 sm:w-5 rounded-full p-0 text-xs">
                2
              </Badge>
            </Button>

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="sm"
              className="lg:hidden h-8 w-8 hover:bg-primary/10 hover:text-primary"
              onClick={toggleMobileMenu}
              aria-label="Toggle mobile menu"
            >
              {isMobileMenuOpen ? (
                <X className="h-4 w-4" />
              ) : (
                <Menu className="h-4 w-4" />
              )}
            </Button>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-7 w-7 sm:h-8 sm:w-8 rounded-full hover:bg-primary/10">
                  <Avatar className="h-7 w-7 sm:h-8 sm:w-8">
                    <AvatarFallback className="bg-gradient-to-br from-primary to-primary/80 text-white text-xs">
                      AI
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">AI Trader</p>
                    <p className="text-xs leading-none text-muted-foreground">
                      ai@tradingbot.com
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        
        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="lg:hidden border-t bg-background/95 backdrop-blur">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigation.map(item => renderNavigationItem(item, true))}
            </div>
            {renderMobileStats()}
          </div>
        )}
      </div>
    </nav>
  );
}