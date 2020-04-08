import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { AuthenticationService } from '../authentication.service';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-log-in',
  templateUrl: './log-in.component.html',
  styleUrls: ['./log-in.component.css']
})
export class LogInComponent implements OnInit {
  log_in_form: FormGroup;
  submitted: boolean = false;
  redirected_from: string;

  constructor(private fb: FormBuilder, private authenticationService: AuthenticationService, private router: Router, private route: ActivatedRoute) {
    if (this.authenticationService.isLoggedIn()) {
      this.router.navigate(['home']);
    }
  }

  ngOnInit() {
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

  onSubmit() {
    this.submitted = true;
    console.log("The Log In Form is: ", this.log_in_form);
    if (this.log_in_form.invalid) {
      console.log("Invalid Log In Form!")
      return;
    }

    this.authenticationService.login(this.log_in_form.value).subscribe(
      (res) => {
        console.log("Successful Login with response:", res);
        this.redirected_from = this.route.snapshot.queryParams["redirectedFrom"] || "/";
        console.log("Redirected from:", this.redirected_from);
        this.router.navigate([this.redirected_from]);
      }
    );
  }

}
