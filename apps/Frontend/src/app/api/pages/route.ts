import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

// ─── GET: Fetch all pages for the authenticated user ─────────────────────────
export async function GET() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { data, error } = await supabase
    .from("pages")
    .select("*")
    .eq("user_id", user.id)
    .or("is_deleted.eq.false,is_deleted.is.null")
    .order("created_at", { ascending: true });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json(data);
}

// ─── POST: Create a new page ─────────────────────────────────────────────────
export async function POST(request: NextRequest) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json();

  const { data, error } = await supabase
    .from("pages")
    .insert({
      id: body.id,
      title: body.title ?? "Untitled",
      content: body.content ?? "",
      user_id: user.id,
      parent_id: body.parentId ?? null,
      icon: body.icon ?? null,
      is_open: body.isOpen ?? true,
    })
    .select()
    .single();

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json(data, { status: 201 });
}

// ─── PATCH: Update an existing page ──────────────────────────────────────────
export async function PATCH(request: NextRequest) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json();
  const { id, ...updates } = body;

  if (!id) {
    return NextResponse.json({ error: "Missing page id" }, { status: 400 });
  }

  // Map camelCase fields to snake_case DB columns
  const dbUpdates: Record<string, unknown> = {};
  if (updates.title !== undefined) dbUpdates.title = updates.title;
  if (updates.content !== undefined) dbUpdates.content = updates.content;
  if (updates.parentId !== undefined) dbUpdates.parent_id = updates.parentId;
  if (updates.icon !== undefined) dbUpdates.icon = updates.icon;
  if (updates.isOpen !== undefined) dbUpdates.is_open = updates.isOpen;
  dbUpdates.updated_at = new Date().toISOString();

  const { data, error } = await supabase
    .from("pages")
    .update(dbUpdates)
    .eq("id", id)
    .eq("user_id", user.id)
    .select()
    .single();

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json(data);
}

// ─── DELETE: Soft-delete a page (move to trash) ─────────────────────────────
export async function DELETE(request: NextRequest) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const id = searchParams.get("id");

  if (!id) {
    return NextResponse.json({ error: "Missing page id" }, { status: 400 });
  }

  const now = new Date().toISOString();

  // Soft-delete the page
  const { error } = await supabase
    .from("pages")
    .update({ is_deleted: true, updated_at: now })
    .eq("id", id)
    .eq("user_id", user.id);

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  // Also soft-delete all children of this page
  await supabase
    .from("pages")
    .update({ is_deleted: true, updated_at: now })
    .eq("parent_id", id)
    .eq("user_id", user.id);

  return NextResponse.json({ success: true });
}
