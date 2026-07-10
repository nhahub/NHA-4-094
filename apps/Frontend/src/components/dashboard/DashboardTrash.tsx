"use client";

import React, { useState, useEffect } from "react";
import { MoreHorizontal, RotateCcw, Trash2, Pencil } from "lucide-react";
import { toast } from "sonner";
import type { PageItem } from "@/app/dashboard/DashboardContent";

type TrashItem = {
  id: string;
  title: string;
  content: string;
  parentId: string | null;
  icon?: string;
};

type DashboardTrashProps = {
  pages: PageItem[];
  isMockUser?: boolean;
  onPagesChanged?: () => void;
};

// ─── Helper: map DB row (snake_case) → TrashItem (camelCase) ─────────────────
function dbRowToTrashItem(row: any): TrashItem {
  return {
    id: row.id,
    title: row.title ?? "Untitled",
    content: row.content ?? "",
    parentId: row.parent_id ?? null,
    icon: row.icon ?? undefined,
  };
}

const DashboardTrash = ({ pages, isMockUser, onPagesChanged }: DashboardTrashProps) => {
  const [trashedPages, setTrashedPages] = useState<TrashItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);

  // ─── Fetch trashed pages on mount ──────────────────────────────────────────
  useEffect(() => {
    if (isMockUser) {
      setTrashedPages([]);
      setIsLoading(false);
      return;
    }

    const fetchTrashed = async () => {
      try {
        const res = await fetch("/api/pages/trash");
        if (!res.ok) throw new Error("Failed to fetch trashed pages");
        const data = await res.json();
        setTrashedPages(data.map(dbRowToTrashItem));
      } catch (err) {
        console.error("Error fetching trashed pages:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrashed();
  }, [isMockUser]);

  // ─── Restore a page ───────────────────────────────────────────────────────
  const handleRestore = async (id: string) => {
    setOpenMenuId(null);
    try {
      const res = await fetch("/api/pages/trash", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      if (!res.ok) throw new Error("Failed to restore page");
      setTrashedPages((prev) => prev.filter((p) => p.id !== id));
      toast.success("Page restored");
      onPagesChanged?.();
    } catch (err) {
      console.error("Error restoring page:", err);
      toast.error("Failed to restore page");
    }
  };

  // ─── Permanently delete a page ─────────────────────────────────────────────
  const handlePermanentDelete = async (id: string) => {
    setOpenMenuId(null);
    try {
      const res = await fetch(`/api/pages/trash?id=${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to permanently delete page");
      setTrashedPages((prev) => prev.filter((p) => p.id !== id));
      toast.success("Page permanently deleted");
    } catch (err) {
      console.error("Error permanently deleting page:", err);
      toast.error("Failed to delete page");
    }
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setOpenMenuId(null);
    if (openMenuId) {
      document.addEventListener("click", handleClickOutside);
      return () => document.removeEventListener("click", handleClickOutside);
    }
  }, [openMenuId]);

  return (
    <main className="flex-1 h-[calc(100vh-40px)] overflow-y-auto text-white my-[20px] border border-[#666565]/50 rounded-lg px-[45px] py-[35px] mx-[20px] relative">
      <div className="absolute top-[25px] left-[45px] right-[45px] flex items-center justify-between z-10">
        <span className="text-[14px] text-[#9ca3af] font-light">../ trash</span>
        <span className="text-[#9ca3af]">...</span>
      </div>

      <section className="mx-auto mt-20 w-full max-w-[900px]">
        <h4 className="mb-5 text-[32px] font-semibold">Trash</h4>
        <div className="flex flex-col">
          {isLoading ? (
            <div className="flex items-center justify-center py-16 text-[#9ca3af]">
              <span className="text-[15px]">Loading...</span>
            </div>
          ) : trashedPages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-[#9ca3af]">
              <Trash2 className="h-10 w-10 mb-3 opacity-40" />
              <span className="text-[15px]">Trash is empty</span>
            </div>
          ) : (
            trashedPages.map((item) => (
              <div key={item.id} className="flex items-center gap-4 border-b border-white/10 py-4">
                <div className="flex items-center justify-center w-8 h-8 shrink-0">
                  {item.icon ? (
                    <span className="text-[18px]">{item.icon}</span>
                  ) : (
                    <Pencil className="w-4 h-4 text-[#8b5cf6] fill-[#8b5cf6]" />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <h4 className="truncate text-[20px] font-semibold text-white">{item.title || "Untitled"}</h4>
                  <h4 className="mt-1 truncate text-[15px] text-[#9ca3af]">
                    {item.content
                      ? item.content.replace(/<[^>]+>/g, "").slice(0, 80) || "No content"
                      : "No content"}
                  </h4>
                </div>
                <div className="relative">
                  <button
                    type="button"
                    className="rounded-full p-2 text-[#d1d5db] transition-colors hover:bg-white/10 hover:text-white"
                    aria-label={`Open actions for ${item.title}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      setOpenMenuId(openMenuId === item.id ? null : item.id);
                    }}
                  >
                    <MoreHorizontal className="h-5 w-5" />
                  </button>

                  {openMenuId === item.id && (
                    <div className="absolute top-[100%] right-0 mt-1 p-1.5 bg-[#0f0f13]/95 backdrop-blur-2xl border border-white/10 rounded-xl shadow-[0_15px_40px_rgba(0,0,0,0.8)] z-50 w-[200px] flex flex-col gap-0.5">
                      <button
                        className="flex items-center gap-3 text-left px-3 py-2 text-[14px] text-[#d1d5db] hover:bg-white/10 hover:text-white rounded-md transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRestore(item.id);
                        }}
                      >
                        <RotateCcw className="w-4 h-4" />
                        Restore
                      </button>
                      <div className="h-[1px] bg-[#666565]/50 my-1 mx-1" />
                      <button
                        className="flex items-center gap-3 text-left px-3 py-2 text-[14px] text-red-400 hover:bg-red-400/10 hover:text-red-300 rounded-md transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          handlePermanentDelete(item.id);
                        }}
                      >
                        <Trash2 className="w-4 h-4" />
                        Delete permanently
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </main>
  );
};

export default DashboardTrash;
