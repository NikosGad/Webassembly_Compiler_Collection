import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PersonalFileDetailsComponent } from './personal-file-details.component';

describe('PersonalFileDetailsComponent', () => {
  let component: PersonalFileDetailsComponent;
  let fixture: ComponentFixture<PersonalFileDetailsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PersonalFileDetailsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PersonalFileDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
