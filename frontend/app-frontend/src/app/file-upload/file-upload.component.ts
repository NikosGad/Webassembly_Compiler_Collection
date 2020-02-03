import { Component, OnInit } from '@angular/core';
import { SourceCodeFileService } from '../source-code-file.service';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css']
})
export class FileUploadComponent implements OnInit {
  language = 'C';
  optimization_level = 'O0'
  resultsZipFileBlob: Blob = new Blob();

  constructor(private sourceCodeFileService: SourceCodeFileService) { }

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

    this.sourceCodeFileService.uploadFile(file.files[0]).subscribe(
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
