import { afterEach, describe, expect, it } from "vitest";

import {
    backendApiUrl,
    getPublicBackendApiBaseUrl,
    publicBackendApiUrl,
    resolveDirectBackendUrl,
} from "./backendApiBase.js";

describe("resolveDirectBackendUrl", () => {
    afterEach(() => {
        delete process.env.BACKEND_API_ROUTING;
        delete process.env.NEXT_PUBLIC_API_ROUTING;
    });

    it("в режиме direct маршрутизирует /auth на порт AUTH (localhost:8002)", () => {
        process.env.BACKEND_API_ROUTING = "direct";
        const url = resolveDirectBackendUrl("/auth/users_interaction/login/", true);
        expect(url).toMatch(/^http:\/\/localhost:8002\//);
    });

    it("в режиме direct маршрутизирует /teams на порт TEAMS (localhost:8004)", () => {
        process.env.NEXT_PUBLIC_API_ROUTING = "direct";
        const url = resolveDirectBackendUrl("/teams/teams/all_teams/", false);
        expect(url).toMatch(/^http:\/\/localhost:8004\//);
    });

    it("direct: /learning ведёт на LEARNING (8011)", () => {
        process.env.BACKEND_API_ROUTING = "direct";
        const url = resolveDirectBackendUrl("/learning/api/courses", true);
        expect(url).toMatch(/^http:\/\/localhost:8011\//);
    });

    it("direct: /orgs обрезает префикс и ведёт на ORGS (8005)", () => {
        process.env.BACKEND_API_ROUTING = "direct";
        const url = resolveDirectBackendUrl("/orgs/list", true);
        expect(url).toBe("http://localhost:8005/list");
    });
});

describe("backendApiUrl", () => {
    afterEach(() => {
        delete process.env.BACKEND_API_ROUTING;
        delete process.env.BACKEND_API_BASE_URL;
        delete process.env.NODE_ENV;
    });

    it("без direct и без BACKEND_API_BASE_URL в production использует продовый хост", () => {
        process.env.NODE_ENV = "production";
        const url = backendApiUrl("/auth/foo");
        expect(url).toBe("https://api.rosdk.ru/auth/foo");
    });

    it("в development без BACKEND_API_BASE_URL подставляет localhost как шлюз", () => {
        process.env.NODE_ENV = "development";
        const url = backendApiUrl("/projects/zvezda");
        expect(url).toBe("http://localhost/projects/zvezda");
    });
});

describe("publicBackendApiUrl", () => {
    afterEach(() => {
        delete process.env.BACKEND_API_ROUTING;
        delete process.env.NEXT_PUBLIC_BACKEND_API_URL;
    });

    it("в режиме direct public указывает на локальный AUTH для совместимости", () => {
        process.env.BACKEND_API_ROUTING = "direct";
        expect(getPublicBackendApiBaseUrl()).toBe("http://localhost:8002");
        expect(publicBackendApiUrl("/teams/x")).toMatch(/8004/);
    });
});
