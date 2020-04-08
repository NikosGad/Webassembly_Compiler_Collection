import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { AuthenticationService } from '../authentication.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit, OnDestroy {
  isLoggedIn: boolean;
  isLoggedInSubscription: Subscription;

  constructor(private authenticationService: AuthenticationService, private router: Router) {
    this.isLoggedInSubscription = this.authenticationService.isLoggedInObs.subscribe(login_state => this.isLoggedIn = login_state);
  }

  ngOnInit() {
  }

  ngOnDestroy() {
    if (this.isLoggedInSubscription != null) {
      this.isLoggedInSubscription.unsubscribe();
    }
  }

  logout() {
    this.authenticationService.logout();
    this.router.navigate(["login"])
  }

}
