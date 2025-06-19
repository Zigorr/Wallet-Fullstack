import React from 'react';
import { motion } from 'framer-motion';
import {
  MagnifyingGlassIcon,
  BellIcon,
  UserIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { Menu, Transition } from '@headlessui/react';
import { Fragment } from 'react';

const Header: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-dark-900/30 backdrop-blur-sm border-b border-dark-700/50 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Search Bar */}
        <div className="flex-1 max-w-xl">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
            <input
              type="text"
              placeholder="Search transactions, accounts..."
              className="w-full pl-10 pr-4 py-2 bg-dark-800/50 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200"
            />
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative p-2 bg-dark-800/50 hover:bg-dark-700/50 rounded-xl transition-colors duration-200"
          >
            <BellIcon className="w-5 h-5 text-dark-300" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-primary-500 rounded-full"></span>
          </motion.button>

          {/* User Menu */}
          <Menu as="div" className="relative">
            <Menu.Button className="flex items-center gap-3 p-2 hover:bg-dark-800/50 rounded-xl transition-colors duration-200">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent rounded-lg flex items-center justify-center">
                <UserIcon className="w-4 h-4 text-white" />
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-white">{user?.username}</p>
                <p className="text-xs text-dark-400">{user?.email}</p>
              </div>
              <ChevronDownIcon className="w-4 h-4 text-dark-400" />
            </Menu.Button>

            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items className="absolute right-0 mt-2 w-48 bg-dark-800 border border-dark-700 rounded-xl shadow-lg focus:outline-none">
                <div className="p-2">
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        className={`${
                          active ? 'bg-dark-700' : ''
                        } flex w-full items-center rounded-lg px-3 py-2 text-sm text-white transition-colors duration-200`}
                      >
                        Profile Settings
                      </button>
                    )}
                  </Menu.Item>
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        className={`${
                          active ? 'bg-dark-700' : ''
                        } flex w-full items-center rounded-lg px-3 py-2 text-sm text-white transition-colors duration-200`}
                      >
                        Preferences
                      </button>
                    )}
                  </Menu.Item>
                  <div className="my-1 border-t border-dark-700"></div>
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        onClick={logout}
                        className={`${
                          active ? 'bg-danger/10 text-danger' : 'text-white'
                        } flex w-full items-center rounded-lg px-3 py-2 text-sm transition-colors duration-200`}
                      >
                        Sign Out
                      </button>
                    )}
                  </Menu.Item>
                </div>
              </Menu.Items>
            </Transition>
          </Menu>
        </div>
      </div>
    </header>
  );
};

export default Header; 