/* Modules from external libraries */
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatInputModule } from '@angular/material/input';

/* Project specific Component */
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { FileUploadComponent } from './file-upload/file-upload.component';

/* Project specific Services */
import { SourceCodeFileService } from './source-code-file.service';
import { HeaderComponent } from './header/header.component';
import { CUploadFormComponent } from './c-upload-form/c-upload-form.component';
import { CppUploadFormComponent } from './cpp-upload-form/cpp-upload-form.component';
import { GolangUploadFormComponent } from './golang-upload-form/golang-upload-form.component';

@NgModule({
  declarations: [
    AppComponent,
    FileUploadComponent,
    HeaderComponent,
    CUploadFormComponent,
    CppUploadFormComponent,
    GolangUploadFormComponent,
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
  ],
  providers: [SourceCodeFileService],
  bootstrap: [AppComponent]
})
export class AppModule { }
