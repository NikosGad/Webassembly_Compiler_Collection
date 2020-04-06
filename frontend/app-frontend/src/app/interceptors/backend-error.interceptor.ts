import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor, HttpResponse } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthenticationService } from '../authentication.service';

@Injectable()
export class BackendErrorInterceptor implements HttpInterceptor {
  constructor(private authenticationService: AuthenticationService) { }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      catchError(err => {
        switch (err.status) {
          case 400:
            switch (err.error.type) {
              case "application/zip":
                alert("Compilation status was not successful. Returning compilation logs.")
                console.log("The error:", err);
                return of(new HttpResponse({body: err.error}));
                break;
              case "JSONParseError":
                alert(err.error.message);
                break;
              case "LanguageSelectionError":
                alert(err.error.message);
                break;
              case "LogInError":
                break;
              case "SignUpError":
                break;
              case "UniqueUsernameViolation":
                break;
              case "UniqueEmailViolation":
                break;
            }
            break;
          case 401:
            console.log("401 Error!!");
            break;
          case 500:
            console.log("500 Error!!");
            break;
        }

        console.log("Error Occured!");
        return throwError(err);
      })
    );
  }
}
