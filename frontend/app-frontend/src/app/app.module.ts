/* Modules from external libraries */
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { HTTP_INTERCEPTORS } from '@angular/common/http';

import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatCheckboxModule } from '@angular/material/checkbox';

/* Project Specific Interceptors */
import { JwtInterceptor } from './interceptors/jwt.interceptor';
import { BackendErrorInterceptor } from './interceptors/backend-error.interceptor';

/* Project specific Components */
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { FileUploadComponent } from './file-upload/file-upload.component';
import { HeaderComponent } from './header/header.component';
import { CUploadFormComponent } from './c-upload-form/c-upload-form.component';
import { CppUploadFormComponent } from './cpp-upload-form/cpp-upload-form.component';
import { GolangUploadFormComponent } from './golang-upload-form/golang-upload-form.component';
import { SignUpComponent } from './sign-up/sign-up.component';
import { LogInComponent } from './log-in/log-in.component';
import { PersonalFilesComponent } from './personal-files/personal-files.component';
import { PersonalFileDetailsComponent } from './personal-file-details/personal-file-details.component';

@NgModule({
  declarations: [
    AppComponent,
    FileUploadComponent,
    HeaderComponent,
    CUploadFormComponent,
    CppUploadFormComponent,
    GolangUploadFormComponent,
    SignUpComponent,
    LogInComponent,
    PersonalFilesComponent,
    PersonalFileDetailsComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    BrowserAnimationsModule,
    MatToolbarModule,
    MatSelectModule,
    MatSlideToggleModule,
    MatInputModule,
    MatButtonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatIconModule,
    MatSidenavModule,
    MatListModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatCheckboxModule,
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true },
    { provide: HTTP_INTERCEPTORS, useClass: BackendErrorInterceptor, multi: true },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
