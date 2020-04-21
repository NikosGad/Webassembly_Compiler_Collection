import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { FileUploadComponent } from './file-upload/file-upload.component';
import { LogInComponent } from './log-in/log-in.component';
import { SignUpComponent } from './sign-up/sign-up.component';
import { PersonalFilesComponent } from './personal-files/personal-files.component';

import { AuthenticatedUserGuard } from './guards/authenticated-user.guard'

const routes: Routes = [
    { path: '', component: FileUploadComponent },
    { path: 'compile', redirectTo: '' },
    { path: 'login', component: LogInComponent },
    { path: 'signup', component: SignUpComponent },
    { path: 'personal_files', component: PersonalFilesComponent, canActivate: [AuthenticatedUserGuard] },
    // TODO: This should be changed to a redirection to an error page
    { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
