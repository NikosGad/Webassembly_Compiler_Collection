import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SystemAdminGraphComponent } from './system-admin-graph.component';

describe('SystemAdminGraphComponent', () => {
  let component: SystemAdminGraphComponent;
  let fixture: ComponentFixture<SystemAdminGraphComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SystemAdminGraphComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SystemAdminGraphComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
