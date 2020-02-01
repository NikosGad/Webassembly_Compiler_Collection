import { Component, OnInit } from '@angular/core';
import { SourceCodeFileService } from '../source-code-file.service';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css']
})
export class FileUploadComponent implements OnInit {
  resultsZipFileBlob: Blob = new Blob();

  constructor(private sourceCodeFileService: SourceCodeFileService) { }

  ngOnInit() {
  }

  add(file: any): void {
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
