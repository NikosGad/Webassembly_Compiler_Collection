import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DummyPrivilegedComponent } from './dummy-privileged.component';

describe('DummyPrivilegedComponent', () => {
  let component: DummyPrivilegedComponent;
  let fixture: ComponentFixture<DummyPrivilegedComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DummyPrivilegedComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DummyPrivilegedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
