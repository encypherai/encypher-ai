import { NextResponse } from "next/server";

export function GET(request: Request) {
  const url = new URL(request.url);
  url.pathname = "/assets/logo.png";

  return NextResponse.redirect(url, 307);
}
