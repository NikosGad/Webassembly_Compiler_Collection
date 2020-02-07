import { Component, OnInit, Input } from '@angular/core';
import { CCompilationOptions, CCompilationOptionsAllowedValues } from '../compilation-options/c-compilation-options';

@Component({
  selector: 'app-c-upload-form',
  templateUrl: './c-upload-form.component.html',
  styleUrls: ['./c-upload-form.component.css']
})
export class CUploadFormComponent implements OnInit {
  @Input() c_compilation_options: CCompilationOptions;
  c_compilation_options_allowed_values = CCompilationOptionsAllowedValues;

  constructor() { }

  ngOnInit() {
  }

}
