import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'app-log-in',
  templateUrl: './log-in.component.html',
  styleUrls: ['./log-in.component.css']
})
export class LogInComponent implements OnInit {
  log_in_form: FormGroup;
  submitted: boolean = false;

  constructor(private fb: FormBuilder) {
    this.log_in_form = this.fb.group({
        username: [
          '',
          Validators.required
        ],
        password: [
          '',
          Validators.required
        ]
    });
  }

  ngOnInit() {
  }

  onSubmit() {
    this.submitted = true;
    console.log(this.log_in_form);
    if (this.log_in_form.invalid) {
      console.log("Invalid Log In Form!")
      return;
    }
    console.log("Sending the form...");
    console.log("Sent form!");
  }

}
