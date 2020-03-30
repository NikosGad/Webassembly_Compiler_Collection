import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { FileUploadComponent } from './file-upload/file-upload.component';
import { LogInComponent } from './log-in/log-in.component';
import { SignUpComponent } from './sign-up/sign-up.component';
import { SystemAdminGraphComponent } from './admin/system-admin-graph/system-admin-graph.component';

const routes: Routes = [
    { path: '', component: FileUploadComponent },
    { path: 'compile', redirectTo: '' },
    { path: 'login', component: LogInComponent },
    { path: 'signup', component: SignUpComponent },
    { path: 'system-admin', component: SystemAdminGraphComponent },
    // TODO: This should be changed to a redirection to an error page
    { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
