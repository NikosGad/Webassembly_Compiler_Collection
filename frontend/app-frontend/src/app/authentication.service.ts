import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {

  constructor(private http: HttpClient) { }

  login(userInfo: any) {
    const formData = new FormData();

    formData.append("username", userInfo.username);
    formData.append("password", userInfo.password);

    return this.http.post('http://127.0.0.1:8080/api/login', formData);
  }
}
