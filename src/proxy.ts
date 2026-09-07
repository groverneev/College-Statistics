import { NextRequest, NextResponse } from "next/server";

const protectedPath = "/trends/international-enrollment-exposure";

function isProtectedPath(pathname: string) {
  return pathname === protectedPath || pathname === `${protectedPath}/`;
}

function hasValidCredentials(
  authorization: string | null,
  expectedUsername: string,
  expectedPassword: string,
) {
  if (!authorization?.startsWith("Basic ")) return false;

  try {
    const encodedCredentials = authorization.slice("Basic ".length);
    const decodedCredentials = atob(encodedCredentials);
    const separatorIndex = decodedCredentials.indexOf(":");
    if (separatorIndex < 0) return false;

    const suppliedUsername = decodedCredentials.slice(0, separatorIndex);
    const suppliedPassword = decodedCredentials.slice(separatorIndex + 1);
    return suppliedUsername === expectedUsername && suppliedPassword === expectedPassword;
  } catch {
    return false;
  }
}

export function proxy(request: NextRequest) {
  if (!isProtectedPath(request.nextUrl.pathname)) {
    return NextResponse.next();
  }

  const username = process.env.REPORTER_PREVIEW_USERNAME;
  const password = process.env.REPORTER_PREVIEW_PASSWORD;

  // Fail closed if the preview credentials were not configured at deployment.
  if (!username || !password) {
    return new NextResponse("Reporter preview is not configured.", {
      status: 503,
      headers: {
        "Cache-Control": "no-store",
        "X-Robots-Tag": "noindex, nofollow",
      },
    });
  }

  if (hasValidCredentials(request.headers.get("authorization"), username, password)) {
    const response = NextResponse.next();
    response.headers.set("X-Robots-Tag", "noindex, nofollow");
    return response;
  }

  return new NextResponse("Authentication required.", {
    status: 401,
    headers: {
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow",
      "WWW-Authenticate": 'Basic realm="College Statistics reporter preview"',
    },
  });
}

export const config = {
  matcher: ["/trends/international-enrollment-exposure/:path*"],
};
