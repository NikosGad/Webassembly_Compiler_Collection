import { Component, OnInit, Input } from '@angular/core';
import { GolangCompilationOptions } from '../compilation-options/golang-compilation-options';

@Component({
  selector: 'app-golang-upload-form',
  templateUrl: './golang-upload-form.component.html',
  styleUrls: ['./golang-upload-form.component.css']
})
export class GolangUploadFormComponent implements OnInit {
  @Input() golang_compilation_options: GolangCompilationOptions

  constructor() { }

  ngOnInit() {
  }

}
