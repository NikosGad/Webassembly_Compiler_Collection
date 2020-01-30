import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class SourceCodeFileService {
  private url = 'http://127.0.0.1:8080/compile'

  // httpOptions = {
  //   headers: new HttpHeaders({ 'Content-Type': 'application/x-www-form-urlencoded' })
  // };

  constructor(private http: HttpClient) { }

  public uploadFile(source_code: File) {
    const formData = new FormData();

    formData.append("mycode", source_code);

    console.log("HIIII")
    console.log(source_code)
    console.log(formData)

    return this.http.post(this.url, formData, {responseType: "blob"}).subscribe(
      (res) => {
          // saveAs(res, "results.zip");
          let blob = new Blob([res], { type: "application/zip"});
        let url = window.URL.createObjectURL(blob);
        let pwa = window.open(url);
        if (!pwa || pwa.closed || typeof pwa.closed == 'undefined') {
            alert( 'Please disable your Pop-up blocker and try again.');
        }
          console.log(res)
      },
      (err) => {
          console.log("this is an error");
          console.log(err)
      }
    );
  }
}
