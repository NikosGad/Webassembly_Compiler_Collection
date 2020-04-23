import { Component, OnInit, Input } from '@angular/core';
import { SourceCodeFile } from '../models/source-code-file';
import { SourceCodeFileService } from '../source-code-file.service';

@Component({
  selector: 'app-personal-file-details',
  templateUrl: './personal-file-details.component.html',
  styleUrls: ['./personal-file-details.component.css']
})
export class PersonalFileDetailsComponent implements OnInit {
  @Input() file: SourceCodeFile;
  @Input() files_content_dict: {[file_id:number]: string};

  constructor(private sourceCodeFileService: SourceCodeFileService) { }

  ngOnInit() {
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
        this.files_content_dict[this.file.id] = res;
        console.log(this.files_content_dict[this.file.id]);
      }
    );
  }

  deleteFile() {
    this.sourceCodeFileService.deleteFile(this.file).subscribe(
      (res:any) => {
        console.log("File Deleted");
      }
    );
  }

}
