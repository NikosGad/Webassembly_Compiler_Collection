import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { SourceCodeFile } from '../models/source-code-file';
import { SourceCodeFileService } from '../source-code-file.service';

@Component({
  selector: 'app-personal-file-details',
  templateUrl: './personal-file-details.component.html',
  styleUrls: ['./personal-file-details.component.css']
})
export class PersonalFileDetailsComponent implements OnInit {
  @Input() file: SourceCodeFile;
  @Input() file_content: string;

  @Output() fileChange: EventEmitter<SourceCodeFile>;
  @Output() file_contentChange: EventEmitter<string>;
  @Output() onFileDelete: EventEmitter<SourceCodeFile>;

  constructor(private sourceCodeFileService: SourceCodeFileService) {
    this.fileChange = new EventEmitter<SourceCodeFile>();
    this.file_contentChange = new EventEmitter<SourceCodeFile>();
    this.onFileDelete = new EventEmitter<SourceCodeFile>();
  }

  ngOnInit() {
  }

  closeDetails() {
    this.fileChange.emit(null);
  }

  downloadResults() {
    this.sourceCodeFileService.downloadFileResult(this.file).subscribe(
      (res:any) => {
        const url= window.URL.createObjectURL(res);
        let element: HTMLAnchorElement = document.getElementById("downloadResultsAnchor") as HTMLAnchorElement;
        element.href = url;
        element.download = "results.zip";
        element.target = "_blank";
        element.click();
      }
    );
  }

  getSourceCode() {
    this.sourceCodeFileService.getFileSourceCode(this.file).subscribe(
      (res:any) => {
        this.file_contentChange.emit(res);
        console.log(res);
      }
    );
  }

  deleteFile() {
    this.sourceCodeFileService.deleteFile(this.file).subscribe(
      (res:any) => {
        console.log("File Deleted");
        this.onFileDelete.emit(this.file);
        this.closeDetails();
      }
    );
  }

}
