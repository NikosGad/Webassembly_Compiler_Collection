import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private http: HttpClient) { }

  public signUp(userInfo: any) {
    const formData = new FormData();

    formData.append("username", userInfo.username);
    formData.append("email", userInfo.email);
    formData.append("password", userInfo.password);

    return this.http.post(environment.apiUrl + '/api/signup', formData);
  }
}
