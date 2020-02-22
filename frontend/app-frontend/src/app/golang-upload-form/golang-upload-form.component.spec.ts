import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GolangUploadFormComponent } from './golang-upload-form.component';

describe('GolangUploadFormComponent', () => {
  let component: GolangUploadFormComponent;
  let fixture: ComponentFixture<GolangUploadFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GolangUploadFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GolangUploadFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
