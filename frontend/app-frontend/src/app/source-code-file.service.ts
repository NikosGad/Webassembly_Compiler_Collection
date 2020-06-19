import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {SourceCodeFile} from './models/source-code-file';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SourceCodeFileService {
  private url_compile = environment.apiUrl + "/api/compile"
  private url_files = environment.apiUrl + "/api/files"

  constructor(private http: HttpClient) { }

  public uploadFile(source_code: File, language: string, compilation_options: any, store: boolean) {
    let server_url: string
    const formData = new FormData();

    formData.append("code", source_code);
    formData.append("compilation_options", JSON.stringify(compilation_options));

    server_url = this.url_compile + "/" + language

    if (store) {
      server_url = server_url + "/store";
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
