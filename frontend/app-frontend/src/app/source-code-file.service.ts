import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class SourceCodeFileService {
  private scheme = 'http://'
  private domain = '127.0.0.1'
  private backend_domain = this.scheme + this.domain
  private url_c = this.backend_domain + ':8080/compile_c'
  private url_cpp = this.backend_domain + ':8080/compile_cpp'
  private url_golang = this.backend_domain + ':8080/compile_golang'
  private url_non_existing = this.backend_domain + ':8080/compile_non_existing'

  // httpOptions = {
  //   headers: new HttpHeaders({ 'Content-Type': 'application/x-www-form-urlencoded' })
  // };

  constructor(private http: HttpClient) { }

  public uploadFile(source_code: File, language: string, compilation_options: any) {
    let server_url: string
    const formData = new FormData();

    formData.append("mycode", source_code);
    formData.append("language", language);
    formData.append("compilation_options", JSON.stringify(compilation_options));

    if (language == "C") {
      server_url = this.url_c;
    }
    else if (language == "C++") {
      server_url = this.url_cpp;
    }
    else if (language == "Golang") {
      server_url = this.url_golang;
    }
    else {
      server_url = this.url_non_existing;
    }

    console.log("Server url to post: " + server_url)
    console.log(source_code)

    return this.http.post(server_url, formData, {responseType: "blob"});
  }
}
