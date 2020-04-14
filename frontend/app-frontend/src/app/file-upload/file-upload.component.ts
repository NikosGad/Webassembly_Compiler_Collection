import { Component, OnInit } from '@angular/core';
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
  file_path: string;
  language: string;
  available_languages: string[];
  c_compilation_options: CCompilationOptions;
  cpp_compilation_options: CppCompilationOptions;
  golang_compilation_options: GolangCompilationOptions;
  resultsZipFileBlob: Blob;

  constructor(private sourceCodeFileService: SourceCodeFileService) {
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

  saveZip(): void {
    let url = window.URL.createObjectURL(this.resultsZipFileBlob);
    let element: HTMLAnchorElement = document.getElementById("downloadhref") as HTMLAnchorElement
    element.href = url
    element.download = "results.zip"
    element.target = "_blank"
    element.click()
    // window.location.href = url;
  }

  resetInputFile() {
    this.file_path = ""
  }

  upload(file: any): void {
    let compilation_options: any;
    this.resultsZipFileBlob = new Blob();

    if (this.language == "C") {
      compilation_options = this.c_compilation_options;
    }
    else if (this.language == "C++") {
      compilation_options = this.cpp_compilation_options;
    }
    else if (this.language == "Golang") {
        compilation_options = this.golang_compilation_options;
    }
    else {
      compilation_options = {};
    }

    this.sourceCodeFileService.uploadFile(file.files[0], this.language, compilation_options).subscribe(
      (res) => {
        this.resultsZipFileBlob = res
        console.log(res)
      }
    );
  }

}
