import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("js-cookie", () => ({
    default: {
        get: vi.fn(),
        set: vi.fn(),
        remove: vi.fn(),
    },
}));

vi.mock("@/lib/portalProfileClient", () => ({
    invalidatePortalProfileCache: vi.fn(),
}));

import Cookies from "js-cookie";
import { clearUserData, getUserData, isAuthorized, saveUserData } from "./auth.js";

describe("auth utils", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.resetAllMocks();
    });

    it("getUserData возвращает null если cookie нет", () => {
        Cookies.get.mockReturnValue(undefined);
        expect(getUserData()).toBeNull();
    });

    it("getUserData парсит JSON из cookie", () => {
        Cookies.get.mockReturnValue(JSON.stringify({ email: "a@b.com", token: true }));
        expect(getUserData()).toEqual({ email: "a@b.com", token: true });
    });

    it("getUserData возвращает null при битом JSON", () => {
        Cookies.get.mockReturnValue("{not json");
        expect(getUserData()).toBeNull();
    });

    it("isAuthorized false без токена", () => {
        Cookies.get.mockReturnValue(JSON.stringify({ email: "x@y.com" }));
        expect(isAuthorized()).toBe(false);
    });

    it("isAuthorized true при token в userData", () => {
        Cookies.get.mockReturnValue(JSON.stringify({ token: true }));
        expect(isAuthorized()).toBe(true);
    });

    it("saveUserData мержит данные и ставит token, вызывает Cookies.set", () => {
        Cookies.get.mockReturnValue(null);
        const out = saveUserData({ email: "n@n.ru", username: "nick" });
        expect(out.token).toBe(true);
        expect(out.email).toBe("n@n.ru");
        expect(Cookies.set).toHaveBeenCalledWith(
            "userData",
            expect.stringContaining("n@n.ru"),
            expect.objectContaining({ path: "/", sameSite: "strict" }),
        );
    });

    it("clearUserData удаляет cookie и сбрасывает кэш портала", async () => {
        const { invalidatePortalProfileCache } = await import("@/lib/portalProfileClient");
        clearUserData();
        expect(Cookies.remove).toHaveBeenCalledWith("userData");
        expect(invalidatePortalProfileCache).toHaveBeenCalled();
    });
});
