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
        returnUrl: null
    }),
    actions: {
        async login(email: string, password: string) {
            const response = await fetchWrapper.post(`${baseUrl}/login`, { email, password });

            if(isSuccess(response)){
                this.token = response.value.token;
                this.userinfo = response.value.user;
                localStorage.setItem('voizchat-token', this.token!);
                localStorage.setItem('voizchat-userinfo', JSON.stringify(this.userinfo));
                router.push(this.returnUrl || '/');
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
                this.userinfo = response.value.user;
                localStorage.setItem('voizchat-token', this.token!);
                localStorage.setItem('voizchat-userinfo', JSON.stringify(this.userinfo));
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
        async logout() {
            this.token = null;
            localStorage.removeItem('voizchat-token');
            localStorage.removeItem('voizchat-userinfo');
            router.push('/login');
        }
    }
});