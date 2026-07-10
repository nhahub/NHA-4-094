"use client";

import React, { useEffect, useState } from "react";
import { Moon, Sun, User, X } from "lucide-react";

type DashboardSettingsProps = {
  isOpen: boolean;
  onClose: () => void;
  displayName: string;
  email?: string;
};

const DashboardSettings = ({ isOpen, onClose, displayName, email }: DashboardSettingsProps) => {
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="absolute inset-0 z-[80] flex items-start justify-center px-6 pt-[7vh] backdrop-blur-xs">
      <div className="w-full max-w-[760px] rounded-2xl border border-[#666565]/50 bg-[#111116]/95 p-7 text-white relative shadow-2xl">
        <div className="grid grid-cols-[200px_1fr] gap-6">
          <div className="border-r border-white/10 pr-6">
            <div className="mb-6 flex items-center justify-between">
              <h1 className="text-[22px] font-semibold text-white">Settings</h1>
              <X className="h-5 w-5 text-[#9ca3af] cursor-pointer hover:text-white transition-colors" onClick={onClose} />
            </div>
            
            <button
              type="button"
              className="mb-3 flex w-full items-center gap-3 rounded-md border border-[#8b5cf6]/80 bg-[#8b5cf6]/10 px-3 py-2 text-left text-[14px] text-white transition-colors"
            >
              <User className="h-5 w-5" />
              General
            </button>
          </div>

          <div className="pl-4">
            <h4 className="mb-4 text-[22px] font-semibold text-white">General</h4>
            
            <label className="mb-4 block">
              <span className="mb-2 block text-[14px] text-white">Name</span>
              <input
                readOnly
                value={displayName}
                className="w-full rounded-md border border-white/10 bg-white/[0.03] px-4 py-3 text-[14px] text-white outline-none"
              />
            </label>
            
            <label className="mb-5 block">
              <span className="mb-2 block text-[14px] text-white">Email</span>
              <input
                readOnly
                value={email || "developer@example.com"}
                className="w-full rounded-md border border-white/10 bg-white/[0.03] px-4 py-3 text-[14px] text-white outline-none"
              />
            </label>

            <div className="mt-8 flex justify-end gap-4">
              <button
                type="button"
                onClick={onClose}
                className="rounded-md border border-white/10 px-8 py-3 text-[14px] text-[#d1d5db] hover:text-white cursor-pointer transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={onClose}
                className="rounded-md bg-gradient-to-r from-[#6d28d9] to-[#d946ef] px-8 py-3 text-[14px] font-semibold text-white cursor-pointer hover:opacity-90 transition-opacity"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardSettings;
