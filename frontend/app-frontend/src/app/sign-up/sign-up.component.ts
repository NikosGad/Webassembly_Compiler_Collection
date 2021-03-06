import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { shouldContainRegexpWithErrorName, fieldsShouldMatch } from '../custom-form-validators';
import { UserService } from '../models/users/user.service';

@Component({
  selector: 'app-sign-up',
  templateUrl: './sign-up.component.html',
  styleUrls: ['./sign-up.component.css']
})
export class SignUpComponent implements OnInit {
  sign_up_form: FormGroup;
  submitted: boolean = false;

  constructor(private fb: FormBuilder, private router: Router, private userService: UserService) {
    this.sign_up_form = this.fb.group({
      username: [
        '',
        [
          Validators.required,
          Validators.minLength(2),
          Validators.pattern("^[A-Za-z0-9]+[A-Za-z0-9_ ]*[A-Za-z0-9]+$")
        ]
      ],
      email: [
        '',
        [
          Validators.required,
          Validators.email
        ]
      ],
      password: [
        '',
        [
          Validators.required,
          Validators.minLength(6),
          shouldContainRegexpWithErrorName("^\\S*$", "whitespaces"),
          shouldContainRegexpWithErrorName("^.*\\d.*$", "digitsAmount"),
          shouldContainRegexpWithErrorName("^.*[A-Za-z].*$", "lettersAmount")
        ]
      ],
      confirm_password: [
        '',
        [
          Validators.required
        ]
      ]
    }, {
      validator: [fieldsShouldMatch("password", "confirm_password")]
    });
  }

  ngOnInit() {
  }

  onSubmit() {
    this.submitted = true;
    console.log("The Sign Up Form is: ", this.sign_up_form);
    if (this.sign_up_form.invalid) {
      console.log("Invalid Sign Up Form!")
      return;
    }

    this.userService.signUp(this.sign_up_form.value).subscribe(
      (res) => {
        alert("Successfully Signed Up");
        this.router.navigate(['login']);
      }
    );
  }

}
