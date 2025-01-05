import { defineStore } from 'pinia';

import { fetchWrapper } from '@/helpers/fetch-wrapper';
import { type Result, isSuccess } from "@/helpers/result";
import router from '@/router/index.ts'

const baseUrl = `${import.meta.env.VITE_API_URL}/users` || '';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        // initialize state from local storage to enable user to stay logged in
        token: localStorage.getItem('voizchat-token'),
        returnUrl: null
    }),
    actions: {
        async login(email: string, password: string) {
            const response = await fetchWrapper.post(`${baseUrl}/login`, { email, password });

            if(isSuccess(response)){
                this.token = response.value.token;
                localStorage.setItem('voizchat-token', this.token!);
                router.push(this.returnUrl || '/messages');
                return null;
            }
            else {
                return response.error.message;
            }
        },
        async register(email:string, username: string, password: string): Promise<string | null> {
            let response = await fetchWrapper.post(`${baseUrl}/register`, { email, username, password });
            if(isSuccess(response)){
                this.token = response.value.token;
                localStorage.setItem('voizchat-token', this.token!);
                return null;
            }
            else {
                return response.error.message;
            }
        },
        async verifyCode(verificationCode: string): Promise<string | null>{
            let response = await fetchWrapper.get(`${baseUrl}/verify/${verificationCode}`)
            if(isSuccess(response)){
                return null;
            }
            else {
                return response.error.message;
            }
        },
        logout() {
            this.token = null;
            localStorage.removeItem('voizchat-token');
            router.push('/login');
        }
    }
});