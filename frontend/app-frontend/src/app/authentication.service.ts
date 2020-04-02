import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {

  constructor(private http: HttpClient) { }

  login(userInfo: any) {
    const formData = new FormData();

    formData.append("username", userInfo.username);
    formData.append("password", userInfo.password);

    return this.http.post('http://127.0.0.1:8080/api/login', formData).pipe(
      map((response:any) => {
        console.log("Login Request Response:", response);
        console.log("Local Storage Before Login:", localStorage);
        localStorage.setItem("jwt", response.jwt);
        console.log("Local Storage After  Login:", localStorage);
        return response.message;
      })
    );
  }

  logout() {
    console.log("Local Storage Before Logout: ", localStorage);
    localStorage.removeItem("jwt");
    console.log("Local Storage After  Logout: ", localStorage);
  }

  isLoggedIn() {
     /* If jwt is not null then return true (a user is logged in) */
     return localStorage.getItem("jwt") != null
  }
}
