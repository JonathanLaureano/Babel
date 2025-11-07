import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddSeries } from './add-series';

describe('AddSeries', () => {
  let component: AddSeries;
  let fixture: ComponentFixture<AddSeries>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddSeries]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddSeries);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
