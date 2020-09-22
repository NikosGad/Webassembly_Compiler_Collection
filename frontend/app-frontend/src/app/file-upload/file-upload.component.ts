import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';

import { AuthenticationService } from '../authentication.service';
import { SourceCodeFileService } from '../source-code-file.service';
import { AvailableLanguages } from '../models/source-code-file';
import { CCompilationOptions } from '../compilation-options/c-compilation-options';
import { CppCompilationOptions } from '../compilation-options/cpp-compilation-options';
import { GolangCompilationOptions } from '../compilation-options/golang-compilation-options';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css']
})
export class FileUploadComponent implements OnInit {
  isLoggedIn: boolean;
  isLoggedInSubscription: Subscription;

  file_path: string;
  language: string;
  available_languages: string[];
  c_compilation_options: CCompilationOptions;
  cpp_compilation_options: CppCompilationOptions;
  golang_compilation_options: GolangCompilationOptions;
  resultsZipFileBlob: Blob;

  constructor(private authenticationService: AuthenticationService, private sourceCodeFileService: SourceCodeFileService) {
    this.isLoggedInSubscription = this.authenticationService.isLoggedInObs.subscribe(login_state => this.isLoggedIn = login_state);
    this.file_path = "";
    this.language = "C";
    this.available_languages = AvailableLanguages;
    this.c_compilation_options = new CCompilationOptions();
    this.cpp_compilation_options = new CppCompilationOptions();
    this.golang_compilation_options = new GolangCompilationOptions();
    this.resultsZipFileBlob = new Blob();
  }

  ngOnInit() {
  }

  ngOnDestroy() {
    if (this.isLoggedInSubscription != null) {
      this.isLoggedInSubscription.unsubscribe();
    }
  }

  downloadZip(): void {
    let element: HTMLAnchorElement = document.getElementById("downloadResultsAnchor") as HTMLAnchorElement;
    element.href = window.URL.createObjectURL(this.resultsZipFileBlob);
    element.click();
    // window.location.href = url;
  }

  resetInputFile(readonlyInputElement) {
    this.file_path = "";
    readonlyInputElement.value = "";
  }

  upload(file: any, store: boolean): void {
    let compilation_options: any;
    this.resultsZipFileBlob = new Blob();

    if (this.language == "C") {
      compilation_options = this.c_compilation_options;
    }
    else if (this.language == "Cpp") {
      compilation_options = this.cpp_compilation_options;
    }
    else if (this.language == "Golang") {
        compilation_options = this.golang_compilation_options;
    }
    else {
      compilation_options = {};
    }

    this.sourceCodeFileService.uploadFile(file.files[0], this.language, compilation_options, store).subscribe(
      (res) => {
        console.log(res)
        this.resultsZipFileBlob = res;
        this.downloadZip();
      }
    );
  }

}
