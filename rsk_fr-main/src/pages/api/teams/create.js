import { backendApiUrl } from "@/lib/backendApiBase";
function parseOrgId(raw) {
    if (raw === undefined || raw === null || raw === "") {
        return null;
    }
    const n = Number.parseInt(String(raw).trim(), 10);
    return Number.isFinite(n) && n > 0 ? n : null;
}

export default async function RegHandler(req, res) {
    try {
        const token = req.cookies.users_access_token;
        if (!token) {
            return res.status(401).json({ success: false, error: "No token provided" });
        }

        const organization_id = parseOrgId(req.body.organization_id);

        const response = await fetch(backendApiUrl('/teams/teams/register'), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Cookie: req.headers.cookie || "",
            },
            body: JSON.stringify({
                name: req.body.name,
                direction: "Другое",
                region: req.body.region ?? "",
                ...(organization_id != null ? { organization_id } : {}),
            }),
            cache: "no-store",
        });

        let data;
        try {
            data = await response.json();
        } catch {
            data = { detail: "Invalid JSON from teams service" };
        }

        if (!response.ok) {
            return res.status(response.status).json({ success: false, data });
        }

        return res.status(200).json({ success: true, data });
    } catch (err) {
        console.log("error", err.message);
        return res.status(500).json({ success: false, error: err.message });
    }
}
