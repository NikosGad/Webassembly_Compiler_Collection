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

  public uploadFile(source_code: File, language: string, compilation_options: any) {
    const formData = new FormData();

    formData.append("mycode", source_code);
    formData.append("language", language);
    formData.append("compilation_options", JSON.stringify(compilation_options));

    console.log("HIIII")
    console.log(source_code)
    console.log(formData)

    return this.http.post(this.url, formData, {responseType: "blob"});
  }
}
