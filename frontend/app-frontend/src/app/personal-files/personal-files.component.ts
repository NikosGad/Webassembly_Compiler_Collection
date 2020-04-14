import { Component, OnInit } from '@angular/core';
import { AvailableLanguages, SourceCodeFile } from '../models/source-code-file';

@Component({
  selector: 'app-personal-files',
  templateUrl: './personal-files.component.html',
  styleUrls: ['./personal-files.component.css']
})
export class PersonalFilesComponent implements OnInit {
  files: { [key: string]: SourceCodeFile[]; } = {
      "C": [
          { name: "hello.c", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C", options: "-O2, gnu11", status:"Successful", content: "" },
      ],
      "C++": [
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
          { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
      ],
      "Golang": [
          { name: "hello.go", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "Golang", options: "-O2", status: "Erroneous", content: "" },
          { name: "hello.go", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "Golang", options: "-O2", status: "Erroneous", content: "" },
      ],
      "Rust": [],
  };

  available_languages: string[];
  selected_file: SourceCodeFile;
  all_files_list: SourceCodeFile[];
  filtered_files: SourceCodeFile[];

  constructor() { }

  ngOnInit() {
    this.available_languages = AvailableLanguages;
    this.selected_file = null;
    this.all_files_list = [];

    for (let language of this.available_languages) {
      console.log(language ,this.files[language]);
      this.all_files_list = this.all_files_list.concat(this.files[language]);
    }

    this.filtered_files = this.all_files_list;
    console.log("All files list:", this.all_files_list);
  }

  onFileSelect(file:any): void {
    this.selected_file = file;
    console.log("You selected:", this.selected_file);
  }

  closeDetails() {
    this.selected_file = null;
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
