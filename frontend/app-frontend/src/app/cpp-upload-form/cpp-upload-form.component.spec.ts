import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CppUploadFormComponent } from './cpp-upload-form.component';

describe('CppUploadFormComponent', () => {
  let component: CppUploadFormComponent;
  let fixture: ComponentFixture<CppUploadFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CppUploadFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CppUploadFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
