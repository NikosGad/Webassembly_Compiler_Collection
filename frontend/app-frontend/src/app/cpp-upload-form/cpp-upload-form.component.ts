import { Component, OnInit, Input } from '@angular/core';
import { CppCompilationOptions, CppCompilationOptionsAllowedValues } from '../compilation-options/cpp-compilation-options';

@Component({
  selector: 'app-cpp-upload-form',
  templateUrl: './cpp-upload-form.component.html',
  styleUrls: ['./cpp-upload-form.component.css']
})
export class CppUploadFormComponent implements OnInit {
  @Input() cpp_compilation_options: CppCompilationOptions;
  cpp_compilation_options_allowed_values = CppCompilationOptionsAllowedValues;

  constructor() { }

  ngOnInit() {
  }

}
