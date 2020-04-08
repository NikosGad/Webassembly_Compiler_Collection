import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor, HttpResponse } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthenticationService } from '../authentication.service';
import { Router } from '@angular/router';

@Injectable()
export class BackendErrorInterceptor implements HttpInterceptor {
  constructor(private authenticationService: AuthenticationService, private router: Router) { }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      catchError(err => {
        switch (err.status) {
          case 400: {
            switch (err.error.type) {
              case "application/zip": {
                alert("Compilation status was not successful. Returning compilation logs.")
                console.log("The error:", err);
                return of(new HttpResponse({body: err.error}));
                break;
              }
              case "JSONParseError":
              case "LanguageSelectionError":
              case "LogInError": {
                alert(err.error.message);
                break;
              }
              case "SignUpError": {
                console.log(err.error.message);
                let alert_message = "";
                for (let [field_name, field_value] of Object.entries(err.error.message)) {
                  alert_message += field_name + ": " + field_value + "\n";
                }
                alert(alert_message);
                break;
              }
              case "UniqueEmailViolation":
              case "UniqueUsernameViolation": {
                alert(err.error.message);
                break;
              }
              default: {
                alert(err.message);
                break;
              }
            }
            break;
          } // End of case: 400
          case 401: {
            /* This switch statement is here as a placeholder.
             * The implementation may change in the future.
             */
            switch (err.error.type) {
              case "AuthorizationViolation":
              case "AuthorizationSchemaViolation":
              case "AuthorizationJWTViolation":
              default: {
                break;
              }
            }
            this.authenticationService.logout();
            location.reload(true);
            break;
          } // End of case: 401
          case 404: {
            alert("The resource is not found!");
            break;
          } // End of case: 404
          case 500: {
            switch (err.error.type) {
              case "UnexpectedException":
              default: {
                break;
              }
            }
          } // End of case: 500
          default: {
            let alert_message = err.error.message || err.message;
            alert_message += "\nPlease try again later.";
            alert(alert_message);
            break;
          }
        }

        return throwError(err);
      })
    );
  }
}
