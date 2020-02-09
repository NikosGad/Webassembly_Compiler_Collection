import { Component, OnInit } from '@angular/core';
import { SourceCodeFileService } from '../source-code-file.service';
import { CCompilationOptions } from '../compilation-options/c-compilation-options';
import { CppCompilationOptions } from '../compilation-options/cpp-compilation-options';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css']
})
export class FileUploadComponent implements OnInit {
  language: string;
  c_compilation_options: CCompilationOptions;
  cpp_compilation_options: CppCompilationOptions
  resultsZipFileBlob: Blob;

  constructor(private sourceCodeFileService: SourceCodeFileService) {
    this.language = "C";
    this.c_compilation_options = new CCompilationOptions();
    this.cpp_compilation_options = new CppCompilationOptions();
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

  upload(file: any): void {
    this.resultsZipFileBlob = new Blob();

    this.sourceCodeFileService.uploadFile(file.files[0], this.language, this.c_compilation_options).subscribe(
      (res) => {
        this.resultsZipFileBlob = res
        console.log(res)
      },
      (err) => {
          console.log("this is an error");
          console.log(err)
      }
    );
  }

}
