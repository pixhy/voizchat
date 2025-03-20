import { defineStore } from 'pinia';
import { fetchWrapper } from '@/helpers/fetch-wrapper';
import { isSuccess } from "@/helpers/result";
import router from '@/router/index.ts'

const baseUrl = `${import.meta.env.VITE_API_URL}/users` || '';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        // initialize state from local storage to enable user to stay logged in
        token: localStorage.getItem('voizchat-token'),
        userinfo: JSON.parse(localStorage.getItem('voizchat-userinfo')!),
        returnUrl: null,
        isLoggingIn: false,
        isRegistering: false,
        isVerifying: false
    }),
    actions: {
        async login(email: string, password: string) {
            if (this.isLoggingIn) return;
            this.isLoggingIn = true;
            try {
                const response = await fetchWrapper.post(`${baseUrl}/login`, { email, password });
                if (isSuccess(response)) {
                    this.token = response.value.token;
                    this.userinfo = response.value.user;
                    localStorage.setItem('voizchat-token', this.token!);
                    localStorage.setItem('voizchat-userinfo', JSON.stringify(this.userinfo));
                    router.push(this.returnUrl || '/');
                    return null;
                } else {
                    return response.error.message;
                }
            } finally {
                this.isLoggingIn = false;
            }
        },
        async register(email: string, username: string, password: string): Promise<string | null> {
            if (this.isRegistering) return null;
            this.isRegistering = true;
            try {
                let response = await fetchWrapper.post(`${baseUrl}/register`, { email, username, password });
                if (isSuccess(response)) {
                    this.token = response.value.token;
                    this.userinfo = response.value.user;
                    localStorage.setItem('voizchat-token', this.token!);
                    localStorage.setItem('voizchat-userinfo', JSON.stringify(this.userinfo));
                    return null;
                } else {
                    return response.error.message;
                }
            } finally {
                this.isRegistering = false;
            }
        },
        async verifyCode(verificationCode: string): Promise<string | null> {
            if (this.isVerifying) return null;
            this.isVerifying = true;
            try {
                let response = await fetchWrapper.get(`${baseUrl}/verify/${verificationCode}`);
                if (isSuccess(response)) {
                    return null;
                } else {
                    return response.error.message;
                }
            } finally {
                this.isVerifying = false;
            }
        },
        async logout() {
            this.token = null;
            localStorage.removeItem('voizchat-token');
            localStorage.removeItem('voizchat-userinfo');
            router.push('/login');
        }
    }
});