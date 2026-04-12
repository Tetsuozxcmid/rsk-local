import { backendApiUrl } from "@/lib/backendApiBase";
// /pages/api/auth/logout.js
export default async function handler(req, res) {
    if (req.method !== "POST") {
        return res.status(405).json({ success: false });
    }

    try {
        await fetch(backendApiUrl('/auth/users_interaction/logout/'), {
            method: "POST",
            headers: {
                Cookie: req.headers.cookie || "",
            },
        });

        const domain = (process.env.LOGOUT_COOKIE_DOMAIN || "").trim();
        const secure = String(process.env.LOGOUT_COOKIE_SECURE || "").toLowerCase() === "true";
        const parts = ["users_access_token=", "Path=/", "Max-Age=0", "HttpOnly"];
        if (domain) parts.push(`Domain=${domain}`);
        if (secure) {
            parts.push("Secure");
            parts.push("SameSite=None");
        } else {
            parts.push("SameSite=Lax");
        }
        res.setHeader("Set-Cookie", [parts.join("; ")]);

        res.status(200).json({ success: true });
    } catch (err) {
        res.status(500).json({ success: false });
    }
}
