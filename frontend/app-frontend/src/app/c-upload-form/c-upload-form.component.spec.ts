import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CUploadFormComponent } from './c-upload-form.component';

describe('CUploadFormComponent', () => {
  let component: CUploadFormComponent;
  let fixture: ComponentFixture<CUploadFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CUploadFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CUploadFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
