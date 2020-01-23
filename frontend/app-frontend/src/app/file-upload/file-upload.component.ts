import { Component, OnInit } from '@angular/core';
import { SourceCodeFileService } from '../source-code-file.service';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css']
})
export class FileUploadComponent implements OnInit {

  constructor(private sourceCodeFileService: SourceCodeFileService) { }

  ngOnInit() {
  }

  add(file: any): void {
    // name = name.trim();
    // if (!name) { return; }
    this.sourceCodeFileService.uploadFile(file.files[0]);
    // this.heroService.addHero({ name } as Hero)
    //   .subscribe(hero => {
    //     this.heroes.push(hero);
    //   });
  }

}
