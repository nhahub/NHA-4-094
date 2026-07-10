import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

// ─── GET: Fetch trashed pages for the authenticated user ─────────────────────
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
    .eq("is_deleted", true)
    .order("updated_at", { ascending: false });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json(data);
}

// ─── PATCH: Restore a trashed page (set is_deleted = false) ──────────────────
export async function PATCH(request: NextRequest) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json();
  const { id } = body;

  if (!id) {
    return NextResponse.json({ error: "Missing page id" }, { status: 400 });
  }

  // Restore the page and all its children
  // First restore the parent
  const { error: parentError } = await supabase
    .from("pages")
    .update({ is_deleted: false, updated_at: new Date().toISOString() })
    .eq("id", id)
    .eq("user_id", user.id);

  if (parentError) {
    return NextResponse.json({ error: parentError.message }, { status: 500 });
  }

  // Then restore all children that have this page as parent
  await supabase
    .from("pages")
    .update({ is_deleted: false, updated_at: new Date().toISOString() })
    .eq("parent_id", id)
    .eq("user_id", user.id)
    .eq("is_deleted", true);

  return NextResponse.json({ success: true });
}

// ─── DELETE: Permanently delete a trashed page ───────────────────────────────
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

  // Permanently delete — CASCADE will handle children
  const { error } = await supabase
    .from("pages")
    .delete()
    .eq("id", id)
    .eq("user_id", user.id);

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ success: true });
}
