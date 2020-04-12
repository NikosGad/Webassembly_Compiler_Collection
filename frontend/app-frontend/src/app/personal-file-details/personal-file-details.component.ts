import { Component, OnInit, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-personal-file-details',
  templateUrl: './personal-file-details.component.html',
  styleUrls: ['./personal-file-details.component.css']
})
export class PersonalFileDetailsComponent implements OnInit {
  @Input() file: any;
  // file_content: string;
  // { name, path, language, options, status, content },

  constructor(private http: HttpClient) { }

  ngOnInit() {
  }

  getFileSourceCode() {
    this.http.get('http://127.0.0.1:8080/api/personal_files', { responseType: 'text'}).subscribe(
      (res:any) => {
        console.log(res);
        this.file.content = res;
        console.log(this.file.content);
      }
    );
  }

}
