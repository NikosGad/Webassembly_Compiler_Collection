import { Component, OnInit } from '@angular/core';
import { AvailableLanguages, SourceCodeFile } from '../models/source-code-file';
import { SourceCodeFileService } from '../source-code-file.service';

@Component({
  selector: 'app-personal-files',
  templateUrl: './personal-files.component.html',
  styleUrls: ['./personal-files.component.css']
})
export class PersonalFilesComponent implements OnInit {
  loading: boolean;
  available_languages: string[];
  files: any;
  files_content: {[file_id: number]: string};
  selected_file: SourceCodeFile;
  all_files_list: SourceCodeFile[];
  filtered_files: SourceCodeFile[];

  constructor(private sourceCodeFileService: SourceCodeFileService) {
    this.loading = true;
    this.available_languages = AvailableLanguages;
    this.files = {};
    this.files_content = {};
    this.selected_file = null;
    this.all_files_list = [];
    this.filtered_files = [];
  }

  ngOnInit() {
    this.sourceCodeFileService.getPersonalFiles().subscribe(
      (res) => {
        this.files = res;

        for (let language of this.available_languages) {
          if (this.files[language]) {
            this.all_files_list = this.all_files_list.concat(this.files[language]);
          }
          else {
            this.files[language] = [];
          }
        }

        this.filtered_files = this.all_files_list;

        console.log("Personal files:", this.files);
        console.log("All files list:", this.all_files_list);
      },
      (err) => {},
      () => {
        this.loading = false;
      }
    );
  }

  onFileSelect(file:any): void {
    this.selected_file = file;
    console.log("You selected:", this.selected_file);
    console.log("The contents of the selected file are:", this.files_content[file.id]);
  }

  filterFiles(language: string) {
    console.log("Filter by language:", language);

    if (language) {
      this.filtered_files = this.files[language];
    }
    else {
      this.filtered_files = this.all_files_list;
    }

    console.log(this.filtered_files);
  }

}
