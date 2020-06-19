import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {
  private isLoggedInSub: BehaviorSubject<boolean>;
  public isLoggedInObs: Observable<boolean>;

  constructor(private http: HttpClient) {
    /* If jwt is not null then set the initial value to true (a user is logged in) */
    this.isLoggedInSub = new BehaviorSubject<boolean>(localStorage.getItem("jwt") != null);
    this.isLoggedInObs = this.isLoggedInSub.asObservable();
  }

  login(userInfo: any) {
    const formData = new FormData();

    formData.append("username", userInfo.username);
    formData.append("password", userInfo.password);

    return this.http.post(environment.apiUrl + '/api/login', formData).pipe(
      map((response:any) => {
        console.log("Login Request Response:", response);
        console.log("Local Storage Before Login:", localStorage);
        localStorage.setItem("jwt", response.jwt);
        this.isLoggedInSub.next(true);
        console.log("Local Storage After  Login:", localStorage);
        return response.message;
      })
    );
  }

  logout() {
    console.log("Local Storage Before Logout: ", localStorage);
    localStorage.removeItem("jwt");
    this.isLoggedInSub.next(false);
    console.log("Local Storage After  Logout: ", localStorage);
  }

  /* Return a read only value */
  isLoggedIn() {
    return this.isLoggedInSub.value;
  }

  getJwt() {
    return localStorage.getItem("jwt");
  }
}
