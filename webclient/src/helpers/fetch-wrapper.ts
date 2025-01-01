import { useAuthStore } from '../stores/auth.store';
import type { Result } from "@/helpers/result";

export const fetchWrapper = {
    get: request('GET'),
    post: request('POST'),
    put: request('PUT'),
    delete: request('DELETE')
};

const BASE_URL = import.meta.env.VITE_API_URL;

function request(method: string) {
    return async (url: string, body: any): Promise<Result<any, {status: number, message: string}>> => {
        const requestOptions : Record<string, any> = {
            method,
            headers: authHeader(url)
        };
        if (body) {
            requestOptions.headers['Content-Type'] = 'application/json';
            requestOptions.body = JSON.stringify(body);
        }
        const response = await fetch(url, requestOptions);
        if(response.status == 200){
            return {success: true, value: await response.json()};
        }

        if(response.ok){
            return {success: true, value: null};
        }

        const text = await response.text();
        const data = text && JSON.parse(text);

        const { token, logout } = useAuthStore();
        if (response.status == 401 && token) {
            // auto logout if 401 Unauthorized response returned from api
            logout();
        }

        const error = (data && data.message) || response.statusText;
        return {success: false, error: {status: response.status, message: error}};
    }
}

// helper functions

function authHeader(url : string) : Record<string, string>{
    // return auth header with jwt if user is logged in and request is to the api url
    const { token } = useAuthStore();
    const isLoggedIn = !!token;
    const isApiUrl = url.startsWith(BASE_URL || '/');
    if (isLoggedIn && isApiUrl) {
        return { Authorization: `Bearer ${token}` };
    } else {
        return {};
    }
}
