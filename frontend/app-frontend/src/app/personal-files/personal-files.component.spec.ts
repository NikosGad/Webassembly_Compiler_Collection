import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PersonalFilesComponent } from './personal-files.component';

describe('PersonalFilesComponent', () => {
  let component: PersonalFilesComponent;
  let fixture: ComponentFixture<PersonalFilesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PersonalFilesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PersonalFilesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
