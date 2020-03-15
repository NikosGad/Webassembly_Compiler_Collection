import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'app-sign-up',
  templateUrl: './sign-up.component.html',
  styleUrls: ['./sign-up.component.css']
})
export class SignUpComponent implements OnInit {
  sign_up_form: FormGroup;
  submitted: boolean = false;

  constructor(private fb: FormBuilder) {
    this.sign_up_form = this.fb.group({
        username: ['', [Validators.required, Validators.minLength(2)]],
        email: ['', [Validators.required, Validators.email]],
        password: ['', Validators.required],
        confirm_password: ['', Validators.required]
    });
  }

  ngOnInit() {
  }

  onSubmit() {
    this.submitted = true;
    console.log("Sending the form...");
    console.log(this.sign_up_form);
    if (this.sign_up_form.invalid) {
      console.log("Invalid Sign Up Form!")
      return;
    }
    console.log("Sent form!");
  }

}
