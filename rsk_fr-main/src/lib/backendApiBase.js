const PROD_API_DEFAULT = "https://api.rosdk.ru";

const DEFAULT_LOCAL_DIRECT_ORIGINS = {
    AUTH: "http://localhost:8002",
    USERS: "http://localhost:8003",
    TEAMS: "http://localhost:8004",
    ORGS: "http://localhost:8005",
    ADMIN_BOT: "http://localhost:8009",
    PROJECTS: "http://localhost:8010",
    LEARNING: "http://localhost:8011",
};

function stripTrailingSlash(s) {
    return String(s).replace(/\/$/, "");
}

function joinOrigin(origin, pathSuffix) {
    const o = stripTrailingSlash(origin);
    if (!pathSuffix || pathSuffix === "/") {
        return o;
    }
    const s = pathSuffix.startsWith("/") ? pathSuffix : `/${pathSuffix}`;
    return `${o}${s}`;
}

function isDirectRouting() {
    return (
        process.env.BACKEND_API_ROUTING === "direct" ||
        process.env.NEXT_PUBLIC_API_ROUTING === "direct"
    );
}

function getDirectOrigin(name, serverSide) {
    const bk = process.env[`BACKEND_DIRECT_${name}_URL`];
    const pub = process.env[`NEXT_PUBLIC_DIRECT_${name}_URL`];
    if (serverSide) {
        if (bk && String(bk).trim()) {
            return stripTrailingSlash(bk);
        }
        if (pub && String(pub).trim()) {
            return stripTrailingSlash(pub);
        }
    } else if (pub && String(pub).trim()) {
        return stripTrailingSlash(pub);
    }
    return DEFAULT_LOCAL_DIRECT_ORIGINS[name];
}

export function resolveDirectBackendUrl(path, serverSide) {
    const p = path.startsWith("/") ? path : `/${path}`;

    if (p === "/admin_bot" || p.startsWith("/admin_bot/")) {
        const rest = p.length <= 10 ? "/" : p.slice(10);
        return joinOrigin(getDirectOrigin("ADMIN_BOT", serverSide), rest);
    }
    if (p === "/learning" || p.startsWith("/learning/")) {
        const rest = p.length <= 9 ? "/" : p.slice(9);
        return joinOrigin(getDirectOrigin("LEARNING", serverSide), rest);
    }
    if (p === "/projects" || p.startsWith("/projects/")) {
        return joinOrigin(getDirectOrigin("PROJECTS", serverSide), p);
    }
    if (p === "/teams" || p.startsWith("/teams/")) {
        return joinOrigin(getDirectOrigin("TEAMS", serverSide), p);
    }
    if (p === "/orgs" || p.startsWith("/orgs/")) {
        const rest = p.length <= 5 ? "/" : p.slice(5);
        return joinOrigin(getDirectOrigin("ORGS", serverSide), rest);
    }
    if (p === "/users" || p.startsWith("/users/")) {
        const rest = p.length <= 6 ? "/" : p.slice(6);
        return joinOrigin(getDirectOrigin("USERS", serverSide), rest);
    }
    if (p === "/auth" || p.startsWith("/auth/")) {
        const rest = p.length <= 5 ? "/" : p.slice(5);
        return joinOrigin(getDirectOrigin("AUTH", serverSide), rest);
    }

    return joinOrigin(getDirectOrigin("AUTH", serverSide), p);
}

function devLocalGatewayBase(raw) {
    const s = raw && String(raw).trim();
    if (!s) {
        return process.env.NODE_ENV === "development" ? "http://localhost" : null;
    }
    if (process.env.NODE_ENV !== "development") {
        return stripTrailingSlash(s);
    }
    try {
        const u = new URL(s);
        if (u.hostname === "traefik") {
            u.hostname = "localhost";
            return stripTrailingSlash(u.toString());
        }
    } catch {}
    return stripTrailingSlash(s);
}

export function getBackendApiBaseUrl() {
    const resolved = devLocalGatewayBase(process.env.BACKEND_API_BASE_URL);
    if (resolved) {
        return resolved;
    }
    return PROD_API_DEFAULT;
}

export function backendApiUrl(path) {
    if (isDirectRouting()) {
        return resolveDirectBackendUrl(path, true);
    }
    const base = getBackendApiBaseUrl();
    const p = path.startsWith("/") ? path : `/${path}`;
    return `${base}${p}`;
}

export function getPublicBackendApiBaseUrl() {
    if (isDirectRouting()) {
        return DEFAULT_LOCAL_DIRECT_ORIGINS.AUTH;
    }
    const resolved = devLocalGatewayBase(process.env.NEXT_PUBLIC_BACKEND_API_URL);
    if (resolved) {
        return resolved;
    }
    return PROD_API_DEFAULT;
}

export function publicBackendApiUrl(path) {
    if (isDirectRouting()) {
        return resolveDirectBackendUrl(path, false);
    }
    const base = getPublicBackendApiBaseUrl();
    const p = path.startsWith("/") ? path : `/${path}`;
    return `${base}${p}`;
}
