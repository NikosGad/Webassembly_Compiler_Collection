import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { AuthenticationService } from '../authentication.service';

@Component({
  selector: 'app-log-in',
  templateUrl: './log-in.component.html',
  styleUrls: ['./log-in.component.css']
})
export class LogInComponent implements OnInit {
  log_in_form: FormGroup;
  submitted: boolean = false;

  constructor(private fb: FormBuilder, private authenticationService: AuthenticationService) {
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
    console.log("The Log In Form is: ", this.log_in_form);
    if (this.log_in_form.invalid) {
      console.log("Invalid Log In Form!")
      return;
    }

    this.authenticationService.login(this.log_in_form.value).subscribe(
      (res) => {
        console.log("The Token is: ", res);
      },
      (err) => {
        console.log("Nologin!");
        console.log(err)
      }
    );
  }

}
