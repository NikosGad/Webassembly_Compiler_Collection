import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { FileUploadComponent } from './file-upload/file-upload.component';

const routes: Routes = [
    { path: '', component: FileUploadComponent },
    { path: 'compile', redirectTo: '' },
    // TODO: This should be changed to a redirection to an error page
    { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
