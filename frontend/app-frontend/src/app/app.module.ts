/* Modules from external libraries */
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

/* Project specific Component */
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { FileUploadComponent } from './file-upload/file-upload.component';

/* Project specific Services */
import { SourceCodeFileService } from './source-code-file.service';

@NgModule({
  declarations: [
    AppComponent,
    FileUploadComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
  ],
  providers: [SourceCodeFileService],
  bootstrap: [AppComponent]
})
export class AppModule { }
