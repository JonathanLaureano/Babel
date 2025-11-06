import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditSeries } from './edit-series';

describe('EditSeries', () => {
  let component: EditSeries;
  let fixture: ComponentFixture<EditSeries>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditSeries]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditSeries);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
