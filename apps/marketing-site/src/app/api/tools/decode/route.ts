import { NextRequest, NextResponse } from "next/server";

import { mapVerifyResponseToDecodeToolResponse } from "@/lib/enterpriseApiTools";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  void request;
  void mapVerifyResponseToDecodeToolResponse;

  return NextResponse.json(
    {
      detail: "Deprecated endpoint. Use /api/tools/verify instead.",
    },
    { status: 410 }
  );
}
