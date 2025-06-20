import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  HomeIcon,
  CreditCardIcon,
  ArrowsRightLeftIcon,
  ClockIcon,
  TagIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  WalletIcon,
  CurrencyDollarIcon,
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  CreditCardIcon as CreditCardIconSolid,
  ArrowsRightLeftIcon as ArrowsRightLeftIconSolid,
  ClockIcon as ClockIconSolid,
  TagIcon as TagIconSolid,
  ChartBarIcon as ChartBarIconSolid,
  Cog6ToothIcon as Cog6ToothIconSolid,
  CurrencyDollarIcon as CurrencyDollarIconSolid,
} from '@heroicons/react/24/solid';

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  iconSolid: React.ElementType;
}

const navigation: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: HomeIcon, iconSolid: HomeIconSolid },
  { name: 'Accounts', href: '/accounts', icon: CreditCardIcon, iconSolid: CreditCardIconSolid },
  { name: 'Transactions', href: '/transactions', icon: ArrowsRightLeftIcon, iconSolid: ArrowsRightLeftIconSolid },
  { name: 'Transfer', href: '/transfer', icon: CurrencyDollarIcon, iconSolid: CurrencyDollarIconSolid },
  { name: 'Recurring', href: '/recurring-transactions', icon: ClockIcon, iconSolid: ClockIconSolid },
  { name: 'Categories', href: '/categories', icon: TagIcon, iconSolid: TagIconSolid },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon, iconSolid: ChartBarIconSolid },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon, iconSolid: Cog6ToothIconSolid },
];

const Sidebar: React.FC = () => {
  const location = useLocation();

  return (
    <motion.div
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col w-72 bg-dark-900/40 backdrop-blur-xl border-r border-dark-700/50"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 p-6 border-b border-dark-700/50">
        <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent rounded-xl flex items-center justify-center">
          <WalletIcon className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">Wallet</h1>
          <p className="text-sm text-dark-400">Personal Finance</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          const Icon = isActive ? item.iconSolid : item.icon;

          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `relative flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                  isActive
                    ? 'bg-primary-600/20 text-primary-400 border border-primary-500/30'
                    : 'text-dark-300 hover:text-white hover:bg-dark-800/50'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute inset-0 bg-gradient-to-r from-primary-600/10 to-accent/10 rounded-xl border border-primary-500/20"
                      transition={{ type: "spring", duration: 0.6 }}
                    />
                  )}
                  <Icon className="w-5 h-5 relative z-10" />
                  <span className="font-medium relative z-10">{item.name}</span>
                  {isActive && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-2 h-2 bg-primary-500 rounded-full ml-auto relative z-10"
                    />
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>
    </motion.div>
  );
};

export default Sidebar; 