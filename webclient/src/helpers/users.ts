import { fetchWrapper } from "./fetch-wrapper";

export interface User {
    userid: string
    username: string
}

const cache = new Map<string,User>();

let myuserid: string | null = null;

export async function getUser(userid: string): Promise<User | null> {
    let user = cache.get(userid);
    console.log("getUser", userid);
    if(user === undefined){
        console.log("cache miss, fetching user");
        let response = await fetchWrapper.get(`/api/users/find-by-id/${userid}`)
        if(response.success){
            user = response.value as User;
            cache.set(userid, user);
        }
        else{
            console.log("fetching user failed", response.error);
            return null;
        }
    }
    return user;
}

export function getMe() : User | null {
    if(myuserid !== null){
        return cache.get(myuserid)!;
    }
    return null;
}

export async function prefetchMe() {
    if(myuserid !== null) return;
    let response = await fetchWrapper.get(`/api/users/me`)
    if(response.success){
        const me = response.value as User;
        cache.set(me.userid, me);
        myuserid = me.userid;
    }
    else{
        console.error("fetching me failed", response.error);
        throw "!";
    }
}
