import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {SourceCodeFile} from './models/source-code-file';

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
  private url_backend = this.scheme + this.domain + ":8080"
  private url_files = this.url_backend + "/api/files"

  constructor(private http: HttpClient) { }

  public uploadFile(source_code: File, language: string, compilation_options: any, store: boolean) {
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

    if (store) {
      server_url = server_url + "_and_store";
    }

    console.log("Server url to post: " + server_url)
    console.log(source_code)

    return this.http.post(server_url, formData, {responseType: "blob"});
  }

  getPersonalFiles() {
    return this.http.get(this.url_files + "/all_personal", {responseType: "json"});
  }

  downloadFileResult(file: SourceCodeFile) {
    let query_parameters = {
      language: file.language,
      directory: file.directory,
      name: "results.zip",
    };

    console.log("Getting File Results With Query Parameters:", query_parameters);

    return this.http.get(this.url_files + "/personal_file_content", {params: query_parameters, responseType: 'blob'});
  }

  getFileSourceCode(file: SourceCodeFile) {
    let query_parameters = {
      language: file.language,
      directory: file.directory,
      name: file.name,
    };

    console.log("Getting File Source Code With Query Parameters:", query_parameters);

    return this.http.get(this.url_files + "/personal_file_content", {params: query_parameters, responseType: 'text'});
  }

  deleteFile(file: SourceCodeFile) {
    console.log("Deleting File:", file);
    return this.http.delete(this.url_files + "/personal_file/" + file.id);
  }
}
