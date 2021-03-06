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
          case 400: {
            switch (err.error.type) {
              case "application/zip": {
                alert("Compilation status was not successful. Returning compilation logs.")
                console.log("The error:", err);
                return of(new HttpResponse({body: err.error}));
                break;
              }
              case "application/json": {
                const reader = new FileReader();
                reader.addEventListener('loadend', () => {
                  alert(JSON.parse(<string>reader.result)["message"]);
                });
                reader.readAsText(err.error);
                break;
              }
              case "FileExistsError":
              case "FileIDTypeError":
              case "GetFileError":
              case "IncorrectCompileBodyError":
              case "JSONParseError":
              case "LanguageNotSupportedError":
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
            switch (err.error.type) {
              case "application/json": {
                const reader = new FileReader();
                reader.addEventListener('loadend', () => {
                  alert(JSON.parse(<string>reader.result)["message"]);
                });
                reader.readAsText(err.error);
                break;
              }
              case "FileNotFound": {
                alert(err.error.message);
                break;
              }
              default: {
                alert(err.message)
                break;
              }
            }
            break;
          } // End of case: 404
          case 500: {
            switch (err.error.type) {
              case "application/json": {
                const reader = new FileReader();
                reader.addEventListener('loadend', () => {
                  alert(JSON.parse(<string>reader.result)["message"] + "\nPlease try again later.");
                });
                reader.readAsText(err.error);
                break;
              }
              case "UnexpectedException": {
                alert(err.error.message + "\nPlease try again later.");
                break;
              }
              default: {
                alert(err.message + "\nPlease try again later.")
                break;
              }
            }
            break;
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
