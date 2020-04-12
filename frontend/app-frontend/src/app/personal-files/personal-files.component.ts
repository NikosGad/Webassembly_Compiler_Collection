import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-personal-files',
  templateUrl: './personal-files.component.html',
  styleUrls: ['./personal-files.component.css']
})
export class PersonalFilesComponent implements OnInit {
  files = [
    { name: "hello.c", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C", options: "-O2, gnu11", status:"Successful", content: "" },
    { name: "hello.go", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "Golang", options: "-O2", status: "Erroneous", content: "" },
    { name: "hello.cpp", path: "/results/emscripten/2020-04-09 20:36:12.116313_f1bcfccb06e22196a782b8e74107dff168d0215224ed1b1116179e8717ed358e/", language: "C++", options: "-O2, gnu++11", status:"Successful", content: "" },
  ];

  selected_file = this.files[0];

  constructor() { }

  ngOnInit() {
  }

  onFileSelect(file:any): void {
    this.selected_file = file;
    console.log("You selected:", this.selected_file);
  }

  closeDetails() {
    this.selected_file = null;
  }

}
